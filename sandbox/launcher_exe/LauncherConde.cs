using System;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;

[assembly: AssemblyTitle("Codice Lexicografico Imperial da Lingua Treppia (V8.2)")]
[assembly: AssemblyDescription("Launcher Executavel, Servidor Embarcado e Central de Voz Whisper do Dicionario Treppio (/conde)")]
[assembly: AssemblyCompany("Chancelaria Imperial de Treppenia")]
[assembly: AssemblyProduct("Codice Treppio Conde V8.2")]
[assembly: AssemblyVersion("8.2.0.0")]

namespace CondeTreppioLauncher
{
    public class EmbeddedServer
    {
        private TcpListener _listener;
        private Thread _serverThread;
        private volatile bool _running;
        public int Port { get; private set; }
        public string ActiveSource { get; set; }
        public string CloudUrl { get; set; }

        public int TotalForms { get; private set; }
        public int NounsCount { get; private set; }
        public int VerbsCount { get; private set; }
        public int AdjsCount { get; private set; }
        public int AdvsCount { get; private set; }

        private readonly string _appDataDir;
        private readonly string _cachedDbPath;
        private readonly string _cloudConfigPath;
        private readonly string _localCondeDbPath = @"D:\Conde_Treppio\sandbox\dicionario_exaustivo\dicionario_formas_expandidas.json";
        private readonly string _localCondeHtmlPath = @"D:\Conde_Treppio\sandbox\ui_dicionario\index.html";
        private readonly string _localUiDir = @"D:\Conde_Treppio\sandbox\ui_dicionario";

        private byte[] _cachedHtmlBytes;
        private byte[] _cachedJsonBytes;

        public EmbeddedServer()
        {
            _appDataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "CondeTreppio");
            Directory.CreateDirectory(_appDataDir);
            _cachedDbPath = Path.Combine(_appDataDir, "dicionario_formas_expandidas.json");
            _cloudConfigPath = Path.Combine(_appDataDir, "cloud_url.txt");

            if (File.Exists(_cloudConfigPath))
            {
                CloudUrl = File.ReadAllText(_cloudConfigPath, Encoding.UTF8).Trim();
            }
            else
            {
                CloudUrl = "";
            }

            ReloadPayloads();
        }

        public void ReloadPayloads()
        {
            if (File.Exists(_localCondeHtmlPath))
            {
                _cachedHtmlBytes = File.ReadAllBytes(_localCondeHtmlPath);
            }
            else
            {
                _cachedHtmlBytes = ReadEmbeddedResource("index.html");
            }

            if (File.Exists(_localCondeDbPath))
            {
                _cachedJsonBytes = File.ReadAllBytes(_localCondeDbPath);
                ActiveSource = "Base Local Oficial (D:\\Conde_Treppio)";
            }
            else if (File.Exists(_cachedDbPath))
            {
                _cachedJsonBytes = File.ReadAllBytes(_cachedDbPath);
                ActiveSource = "Banco Sincronizado da Nuvem (Git/Drive)";
            }
            else
            {
                _cachedJsonBytes = ReadEmbeddedResource("dicionario_formas_expandidas.json");
                ActiveSource = "Banco Embutido no Executavel (Offline)";
            }

            ParseMetadataMetrics();
        }

        private void ParseMetadataMetrics()
        {
            TotalForms = 153005;
            NounsCount = 1248;
            VerbsCount = 1108;
            AdjsCount = 281;
            AdvsCount = 603;

            try
            {
                if (_cachedJsonBytes == null || _cachedJsonBytes.Length == 0) return;
                int scanLen = Math.Min(_cachedJsonBytes.Length, 4096);
                string head = Encoding.UTF8.GetString(_cachedJsonBytes, 0, scanLen);

                TotalForms = ExtractIntMetric(head, "total_expanded_word_forms", TotalForms);
                NounsCount = ExtractIntMetric(head, "nouns_count", NounsCount);
                VerbsCount = ExtractIntMetric(head, "verb_stems_quadripartite", VerbsCount);
                AdjsCount = ExtractIntMetric(head, "adjectives_count", AdjsCount);
                AdvsCount = ExtractIntMetric(head, "adverbs_count", AdvsCount);

                // Caso total_expanded_word_forms esteja no final do JSON, inspecionar os últimos 4 KB
                if (TotalForms == 153005 && _cachedJsonBytes.Length > 4096)
                {
                    string tail = Encoding.UTF8.GetString(_cachedJsonBytes, _cachedJsonBytes.Length - 4096, 4096);
                    TotalForms = ExtractIntMetric(tail, "total_expanded_word_forms", TotalForms);
                }
            }
            catch { }
        }

        private static int ExtractIntMetric(string text, string key, int fallback)
        {
            Match m = Regex.Match(text, "\"" + key + "\"\\s*:\\s*(\\d+)");
            if (m.Success)
            {
                int val;
                if (int.TryParse(m.Groups[1].Value, out val)) return val;
            }
            return fallback;
        }

        private byte[] ReadEmbeddedResource(string resourceName)
        {
            Assembly asm = Assembly.GetExecutingAssembly();
            using (Stream s = asm.GetManifestResourceStream(resourceName))
            {
                if (s == null) return Encoding.UTF8.GetBytes("{}");
                using (MemoryStream ms = new MemoryStream())
                {
                    s.CopyTo(ms);
                    return ms.ToArray();
                }
            }
        }

        public static string NormalizeCloudUrl(string rawUrl)
        {
            if (string.IsNullOrWhiteSpace(rawUrl)) return "";
            string u = rawUrl.Trim();
            Match m = Regex.Match(u, @"/file/d/([a-zA-Z0-9_-]+)");
            if (!m.Success) m = Regex.Match(u, @"[?&]id=([a-zA-Z0-9_-]+)");
            if (m.Success && u.Contains("drive.google.com"))
            {
                return "https://drive.google.com/uc?export=download&id=" + m.Groups[1].Value;
            }
            if (u.Contains("github.com") && u.Contains("/blob/"))
            {
                return u.Replace("github.com", "raw.githubusercontent.com").Replace("/blob/", "/");
            }
            return u;
        }

        public bool SyncFromCloud(string rawUrl, out string message)
        {
            try
            {
                string directUrl = NormalizeCloudUrl(rawUrl);
                if (string.IsNullOrEmpty(directUrl))
                {
                    message = "Informe uma URL valida do GitHub ou Google Drive.";
                    return false;
                }

                ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
                using (WebClient wc = new WebClient())
                {
                    wc.Encoding = Encoding.UTF8;
                    wc.Headers.Add("User-Agent", "CondeTreppioLauncher/8.2");
                    string json = wc.DownloadString(directUrl);
                    if (!json.Contains("\"substantivos\""))
                    {
                        message = "O arquivo baixado nao contem um banco de dados valido do /conde.";
                        return false;
                    }
                    File.WriteAllText(_cachedDbPath, json, Encoding.UTF8);
                    File.WriteAllText(_cloudConfigPath, directUrl, Encoding.UTF8);
                    CloudUrl = directUrl;
                    _cachedJsonBytes = Encoding.UTF8.GetBytes(json);
                    ParseMetadataMetrics();
                    ActiveSource = "Nuvem Sincronizada (Git/Google Drive)";
                    message = "Banco de dados atualizado com sucesso da nuvem (" + TotalForms.ToString("N0", new CultureInfo("pt-BR")) + " formas)!";
                    return true;
                }
            }
            catch (Exception ex)
            {
                message = "Falha ao sincronizar da nuvem: " + ex.Message;
                return false;
            }
        }

        public bool RecompileLocalConde(out string message)
        {
            string scriptPath = @"D:\Conde_Treppio\sandbox\gerador_dicionario_integral_sandbox.py";
            if (!File.Exists(scriptPath))
            {
                if (!string.IsNullOrEmpty(CloudUrl))
                {
                    return SyncFromCloud(CloudUrl, out message);
                }
                ReloadPayloads();
                message = "Base embutida recarregada (" + TotalForms.ToString("N0", new CultureInfo("pt-BR")) + " formas).";
                return true;
            }

            try
            {
                ProcessStartInfo psi = new ProcessStartInfo("python", "\"" + scriptPath + "\"")
                {
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                };
                using (Process p = Process.Start(psi))
                {
                    p.WaitForExit(20000);
                }
                ReloadPayloads();
                ActiveSource = "Base Local /conde Recompilada";
                message = "Base local D:\\Conde_Treppio recompilada (" + TotalForms.ToString("N0", new CultureInfo("pt-BR")) + " formas)!";
                return true;
            }
            catch (Exception ex)
            {
                message = "Erro ao recompilar: " + ex.Message;
                return false;
            }
        }

        public void Start()
        {
            int[] candidatePorts = new int[] { 8766, 8767, 8768, 0 };
            foreach (int p in candidatePorts)
            {
                try
                {
                    _listener = new TcpListener(IPAddress.Loopback, p);
                    _listener.Start();
                    Port = ((IPEndPoint)_listener.LocalEndpoint).Port;
                    break;
                }
                catch
                {
                    _listener = null;
                }
            }

            _running = true;
            _serverThread = new Thread(ListenLoop) { IsBackground = true };
            _serverThread.Start();
        }

        public void Stop()
        {
            _running = false;
            try { _listener.Stop(); } catch { }
        }

        private void ListenLoop()
        {
            while (_running)
            {
                try
                {
                    TcpClient client = _listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleClient, client);
                }
                catch
                {
                    if (!_running) break;
                }
            }
        }

        private void HandleClient(object state)
        {
            using (TcpClient client = (TcpClient)state)
            using (NetworkStream stream = client.GetStream())
            {
                try
                {
                    client.ReceiveTimeout = 5000;
                    client.SendTimeout = 5000;
                    byte[] buffer = new byte[8192];
                    int read = stream.Read(buffer, 0, buffer.Length);
                    if (read <= 0) return;

                    string requestText = Encoding.UTF8.GetString(buffer, 0, read);
                    string[] lines = requestText.Split(new[] { "\r\n" }, StringSplitOptions.None);
                    if (lines.Length == 0) return;

                    string[] firstLine = lines[0].Split(' ');
                    if (firstLine.Length < 2) return;
                    string method = firstLine[0].ToUpperInvariant();
                    string rawPath = firstLine[1];
                    string cleanPath = rawPath.Split('?')[0];

                    if (cleanPath.StartsWith("/api/db") || cleanPath.EndsWith("/dicionario_formas_expandidas.json"))
                    {
                        SendResponse(stream, "200 OK", "application/json; charset=utf-8", _cachedJsonBytes);
                    }
                    else if (cleanPath.StartsWith("/api/recompilar") && method == "POST")
                    {
                        string msg;
                        RecompileLocalConde(out msg);
                        string body = "{\"status\":\"ok\",\"source\":\"" + EscapeJson(ActiveSource) + "\",\"db\":" + Encoding.UTF8.GetString(_cachedJsonBytes) + "}";
                        SendResponse(stream, "200 OK", "application/json; charset=utf-8", Encoding.UTF8.GetBytes(body));
                    }
                    else if (cleanPath.StartsWith("/api/cloud-config") && method == "POST")
                    {
                        int bodyIdx = requestText.IndexOf("\r\n\r\n");
                        if (bodyIdx >= 0)
                        {
                            string postBody = requestText.Substring(bodyIdx + 4);
                            Match m = Regex.Match(postBody, "\"cloud_url\"\\s*:\\s*\"([^\"]+)\"");
                            if (m.Success)
                            {
                                string msg;
                                SyncFromCloud(m.Groups[1].Value, out msg);
                            }
                        }
                        SendResponse(stream, "200 OK", "application/json; charset=utf-8", Encoding.UTF8.GetBytes("{\"status\":\"ok\"}"));
                    }
                    else if (cleanPath.StartsWith("/dados_dicionario_conde.js"))
                    {
                        string js = "window.CONDE_DB = " + Encoding.UTF8.GetString(_cachedJsonBytes) + ";";
                        SendResponse(stream, "200 OK", "application/javascript; charset=utf-8", Encoding.UTF8.GetBytes(js));
                    }
                    else if (cleanPath == "/manifest.json" || cleanPath == "/sw.js" || cleanPath == "/icon-512.png")
                    {
                        string fileName = cleanPath.TrimStart('/');
                        string localAsset = Path.Combine(_localUiDir, fileName);
                        if (File.Exists(localAsset))
                        {
                            string mime = fileName.EndsWith(".json") ? "application/manifest+json; charset=utf-8"
                                        : fileName.EndsWith(".js") ? "application/javascript; charset=utf-8"
                                        : "image/png";
                            SendResponse(stream, "200 OK", mime, File.ReadAllBytes(localAsset));
                        }
                        else
                        {
                            SendResponse(stream, "404 Not Found", "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Not found"));
                        }
                    }
                    else
                    {
                        SendResponse(stream, "200 OK", "text/html; charset=utf-8", _cachedHtmlBytes);
                    }
                }
                catch { }
            }
        }

        private static string EscapeJson(string s)
        {
            return (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"");
        }

        private static void SendResponse(NetworkStream stream, string status, string contentType, byte[] body)
        {
            string header =
                "HTTP/1.1 " + status + "\r\n" +
                "Content-Type: " + contentType + "\r\n" +
                "Content-Length: " + body.Length + "\r\n" +
                "Cache-Control: no-store\r\n" +
                "Access-Control-Allow-Origin: *\r\n" +
                "Connection: close\r\n\r\n";
            byte[] headerBytes = Encoding.UTF8.GetBytes(header);
            stream.Write(headerBytes, 0, headerBytes.Length);
            stream.Write(body, 0, body.Length);
            stream.Flush();
        }
    }

    public class LauncherForm : Form
    {
        private readonly EmbeddedServer _server;
        private readonly CultureInfo _ptBr = new CultureInfo("pt-BR");
        private Label _lblSubtitle;
        private Label _lblStatus;
        private Label _lblUrl;
        private Label _valForms;
        private Label _valNouns;
        private Label _valVerbs;
        private Label _valAdjs;
        private TextBox _txtCloudUrl;
        private Label _lblFeedback;
        private Button _btnSyncCloud;
        private Button _btnRecompileLocal;

        public LauncherForm(EmbeddedServer server)
        {
            _server = server;
            Text = "Códice Lexicográfico Imperial — Língua Tréppia (Era Clássica V8.2 | /conde)";
            ClientSize = new Size(820, 560);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(6, 8, 13);
            ForeColor = Color.FromArgb(242, 245, 252);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;

            Font titleFont = new Font("Georgia", 15f, FontStyle.Bold);
            Font subFont = new Font("Segoe UI", 9.5f, FontStyle.Regular);
            Font boldFont = new Font("Segoe UI", 9.5f, FontStyle.Bold);
            Font monoFont = new Font("Consolas", 9.5f, FontStyle.Regular);

            // Filete Superior Ouro Imperial
            Panel goldTopBar = new Panel
            {
                Dock = DockStyle.Top,
                Height = 3,
                BackColor = Color.FromArgb(212, 175, 55)
            };

            // Header Imperial
            Panel headerPanel = new Panel
            {
                Dock = DockStyle.Top,
                Height = 86,
                BackColor = Color.FromArgb(15, 20, 34),
                Padding = new Padding(24, 14, 24, 12)
            };

            Label lblCrest = new Label
            {
                Text = "𝓣",
                Font = new Font("Georgia", 22f, FontStyle.Bold),
                ForeColor = Color.FromArgb(253, 226, 142),
                BackColor = Color.FromArgb(26, 33, 54),
                TextAlign = ContentAlignment.MiddleCenter,
                Size = new Size(52, 52),
                Location = new Point(24, 17)
            };

            Label lblTitle = new Label
            {
                Text = "CÓDICE LEXICOGRÁFICO IMPERIAL DO TRÉPPIO (V8.2)",
                Font = titleFont,
                ForeColor = Color.FromArgb(253, 226, 142),
                AutoSize = true,
                Location = new Point(88, 16)
            };

            _lblSubtitle = new Label
            {
                Text = FormatSubtitleText(),
                Font = subFont,
                ForeColor = Color.FromArgb(157, 169, 197),
                AutoSize = true,
                Location = new Point(90, 46)
            };

            headerPanel.Controls.Add(lblCrest);
            headerPanel.Controls.Add(lblTitle);
            headerPanel.Controls.Add(_lblSubtitle);
            Controls.Add(headerPanel);
            Controls.Add(goldTopBar);

            // 4 Cards Bento de Telemetria ao Vivo
            int cardY = 104;
            int cardW = 184;
            int cardGap = 12;
            Controls.Add(CreateTelemetryCard("FORMAS VALIDADAS", _server.TotalForms.ToString("N0", _ptBr), "0 Colisões • 21 Leis Sandi", new Point(24, cardY), cardW, out _valForms));
            Controls.Add(CreateTelemetryCard("SUBSTANTIVOS", _server.NounsCount.ToString("N0", _ptBr), "8 Casos + 10 Sufixos", new Point(24 + (cardW + cardGap) * 1, cardY), cardW, out _valNouns));
            Controls.Add(CreateTelemetryCard("VERBOS (4 EIXOS)", _server.VerbsCount.ToString("N0", _ptBr), "114 Formas por Verbo", new Point(24 + (cardW + cardGap) * 2, cardY), cardW, out _valVerbs));
            Controls.Add(CreateTelemetryCard("ADJS & ADVÉRBIOS", _server.AdjsCount + " / " + _server.AdvsCount, "Superl. -n & Modal -vë", new Point(24 + (cardW + cardGap) * 3, cardY), cardW, out _valAdjs));

            // Status e Servidor Local
            _lblStatus = new Label
            {
                Text = "● Fonte Ativa: " + _server.ActiveSource,
                Font = boldFont,
                ForeColor = Color.FromArgb(52, 199, 135),
                AutoSize = true,
                Location = new Point(24, 198)
            };
            Controls.Add(_lblStatus);

            _lblUrl = new Label
            {
                Text = "Servidor Local Embarcado: http://127.0.0.1:" + _server.Port + "  |  Fila Autônoma: 200 Temas (30 min)",
                Font = monoFont,
                ForeColor = Color.FromArgb(87, 156, 248),
                AutoSize = true,
                Location = new Point(24, 222)
            };
            Controls.Add(_lblUrl);

            // Botão Principal: Abrir Dicionário
            Button btnOpenApp = CreateStyledButton(
                "📖 ABRIR CÓDICE TRÉPPIO (JANELA DEDICADA)",
                new Point(24, 254),
                new Size(772, 48),
                Color.FromArgb(42, 34, 16),
                Color.FromArgb(253, 226, 142)
            );
            btnOpenApp.Font = new Font("Segoe UI", 11.5f, FontStyle.Bold);
            btnOpenApp.FlatAppearance.BorderColor = Color.FromArgb(212, 175, 55);
            btnOpenApp.FlatAppearance.BorderSize = 2;
            btnOpenApp.Click += (s, e) => LaunchDedicatedWindow();
            Controls.Add(btnOpenApp);

            // Botão Dedicado: Conversar por Voz com o Conde (Whisper + Voz Neural)
            Button btnVoiceWhisper = CreateStyledButton(
                "🎙️ CONVERSAR POR VOZ COM O CONDE (WHISPER STT + VOZ NEURAL)",
                new Point(24, 312),
                new Size(772, 44),
                Color.FromArgb(18, 34, 46),
                Color.FromArgb(115, 220, 175)
            );
            btnVoiceWhisper.Font = new Font("Segoe UI", 10.5f, FontStyle.Bold);
            btnVoiceWhisper.FlatAppearance.BorderColor = Color.FromArgb(52, 199, 135);
            btnVoiceWhisper.Click += (s, e) => LaunchWhisperVoiceGui();
            Controls.Add(btnVoiceWhisper);

            // Configuração de Nuvem
            Label lblCloud = new Label
            {
                Text = "URL do Banco de Dados Online (GitHub Raw ou Link Público do Google Drive):",
                Font = subFont,
                ForeColor = Color.FromArgb(212, 175, 55),
                AutoSize = true,
                Location = new Point(24, 372)
            };
            Controls.Add(lblCloud);

            _txtCloudUrl = new TextBox
            {
                Location = new Point(24, 396),
                Size = new Size(772, 28),
                BackColor = Color.FromArgb(15, 20, 34),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = monoFont,
                Text = _server.CloudUrl
            };
            Controls.Add(_txtCloudUrl);

            _btnSyncCloud = CreateStyledButton(
                "☁️ Sincronizar da Nuvem (Git / Drive)",
                new Point(24, 434),
                new Size(378, 40),
                Color.FromArgb(20, 26, 44),
                Color.FromArgb(242, 245, 252)
            );
            _btnSyncCloud.Click += OnSyncCloudClick;
            Controls.Add(_btnSyncCloud);

            _btnRecompileLocal = CreateStyledButton(
                "🔨 Recompilar e Sincronizar Base /conde",
                new Point(418, 434),
                new Size(378, 40),
                Color.FromArgb(20, 26, 44),
                Color.FromArgb(253, 226, 142)
            );
            _btnRecompileLocal.Click += OnRecompileClick;
            Controls.Add(_btnRecompileLocal);

            _lblFeedback = new Label
            {
                Text = "Pronto. O Códice funciona 100% offline, sincroniza via nuvem e inclui audiência vocal bidirecional via Whisper.",
                Font = subFont,
                ForeColor = Color.FromArgb(157, 169, 197),
                AutoSize = false,
                Size = new Size(772, 44),
                Location = new Point(24, 488)
            };
            Controls.Add(_lblFeedback);

            Shown += (s, e) => LaunchDedicatedWindow();
        }

        private string FormatSubtitleText()
        {
            return string.Format(
                _ptBr,
                "{0:N0} Substantivos • {1:N0} Verbos Quadripartites • {2:N0} Adjetivos • {3:N0} Advérbios • {4:N0} Formas",
                _server.NounsCount,
                _server.VerbsCount,
                _server.AdjsCount,
                _server.AdvsCount,
                _server.TotalForms
            );
        }

        private void RefreshMetricsUi()
        {
            _lblSubtitle.Text = FormatSubtitleText();
            _lblStatus.Text = "● Fonte Ativa: " + _server.ActiveSource;
            _valForms.Text = _server.TotalForms.ToString("N0", _ptBr);
            _valNouns.Text = _server.NounsCount.ToString("N0", _ptBr);
            _valVerbs.Text = _server.VerbsCount.ToString("N0", _ptBr);
            _valAdjs.Text = _server.AdjsCount + " / " + _server.AdvsCount;
        }

        private Panel CreateTelemetryCard(string title, string value, string sub, Point loc, int width, out Label valueLabel)
        {
            Panel card = new Panel
            {
                Location = loc,
                Size = new Size(width, 78),
                BackColor = Color.FromArgb(15, 20, 34),
                BorderStyle = BorderStyle.FixedSingle
            };

            Panel leftAccent = new Panel
            {
                Dock = DockStyle.Left,
                Width = 3,
                BackColor = Color.FromArgb(212, 175, 55)
            };

            Label lblCardTitle = new Label
            {
                Text = title,
                Font = new Font("Segoe UI", 7.5f, FontStyle.Bold),
                ForeColor = Color.FromArgb(157, 169, 197),
                AutoSize = true,
                Location = new Point(10, 8)
            };

            valueLabel = new Label
            {
                Text = value,
                Font = new Font("Consolas", 13.5f, FontStyle.Bold),
                ForeColor = Color.FromArgb(253, 226, 142),
                AutoSize = true,
                Location = new Point(10, 25)
            };

            Label lblSub = new Label
            {
                Text = sub,
                Font = new Font("Segoe UI", 7.5f, FontStyle.Regular),
                ForeColor = Color.FromArgb(98, 111, 141),
                AutoSize = true,
                Location = new Point(10, 52)
            };

            card.Controls.Add(lblCardTitle);
            card.Controls.Add(valueLabel);
            card.Controls.Add(lblSub);
            card.Controls.Add(leftAccent);
            return card;
        }

        private Button CreateStyledButton(string text, Point loc, Size sz, Color back, Color fore)
        {
            Button b = new Button
            {
                Text = text,
                Location = loc,
                Size = sz,
                BackColor = back,
                ForeColor = fore,
                FlatStyle = FlatStyle.Flat,
                Cursor = Cursors.Hand,
                Font = new Font("Segoe UI", 9.5f, FontStyle.Bold)
            };
            b.FlatAppearance.BorderColor = Color.FromArgb(212, 175, 55);
            b.FlatAppearance.BorderSize = 1;
            return b;
        }

        private void OnSyncCloudClick(object sender, EventArgs e)
        {
            string url = _txtCloudUrl.Text;
            _btnSyncCloud.Enabled = false;
            _lblFeedback.ForeColor = Color.FromArgb(253, 226, 142);
            _lblFeedback.Text = "⏳ Conectando à nuvem em background para baixar dicionario_formas_expandidas.json...";

            ThreadPool.QueueUserWorkItem(_ =>
            {
                string msg;
                bool ok = _server.SyncFromCloud(url, out msg);
                BeginInvoke((Action)(() =>
                {
                    _btnSyncCloud.Enabled = true;
                    RefreshMetricsUi();
                    _lblFeedback.ForeColor = ok ? Color.FromArgb(52, 199, 135) : Color.FromArgb(226, 92, 104);
                    _lblFeedback.Text = msg;
                }));
            });
        }

        private void OnRecompileClick(object sender, EventArgs e)
        {
            _btnRecompileLocal.Enabled = false;
            _lblFeedback.ForeColor = Color.FromArgb(253, 226, 142);
            _lblFeedback.Text = "⏳ Recompilando base morfológica do /conde em background...";

            ThreadPool.QueueUserWorkItem(_ =>
            {
                string msg;
                bool ok = _server.RecompileLocalConde(out msg);
                BeginInvoke((Action)(() =>
                {
                    _btnRecompileLocal.Enabled = true;
                    RefreshMetricsUi();
                    _lblFeedback.ForeColor = ok ? Color.FromArgb(52, 199, 135) : Color.FromArgb(226, 92, 104);
                    _lblFeedback.Text = msg;
                }));
            });
        }

        public void LaunchWhisperVoiceGui()
        {
            string scriptPath = @"D:\Conde_Treppio\sandbox\interface_voz_whisper.py";
            if (!File.Exists(scriptPath))
            {
                _lblFeedback.ForeColor = Color.FromArgb(226, 92, 104);
                _lblFeedback.Text = "Script de voz não encontrado em: " + scriptPath;
                return;
            }
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo("pythonw", "\"" + scriptPath + "\"")
                {
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                Process.Start(psi);
                _lblFeedback.ForeColor = Color.FromArgb(52, 199, 135);
                _lblFeedback.Text = "🎙️ Interface de Conversação por Voz (Whisper + Voz Neural) iniciada!";
            }
            catch
            {
                try
                {
                    Process.Start("python", "\"" + scriptPath + "\"");
                }
                catch (Exception ex)
                {
                    _lblFeedback.ForeColor = Color.FromArgb(226, 92, 104);
                    _lblFeedback.Text = "Erro ao abrir interface de voz: " + ex.Message;
                }
            }
        }

        public void LaunchDedicatedWindow()
        {
            string url = "http://127.0.0.1:" + _server.Port;
            try
            {
                string[] edgePaths = new[]
                {
                    @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    @"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                };
                foreach (string ep in edgePaths)
                {
                    if (File.Exists(ep))
                    {
                        Process.Start(ep, "--app=" + url + " --window-size=1480,920");
                        return;
                    }
                }
                Process.Start(url);
            }
            catch
            {
                try { Process.Start(url); } catch { }
            }
        }
    }

    internal static class Program
    {
        [DllImport("user32.dll")]
        private static extern bool SetProcessDPIAware();

        [STAThread]
        private static int Main(string[] args)
        {
            try { SetProcessDPIAware(); } catch { }

            EmbeddedServer server = new EmbeddedServer();
            server.Start();

            if (args != null && args.Length > 0 && args[0] == "--test-headless")
            {
                try
                {
                    using (WebClient wc = new WebClient())
                    {
                        wc.Encoding = Encoding.UTF8;
                        string dbJson = wc.DownloadString("http://127.0.0.1:" + server.Port + "/api/db");
                        bool valid = dbJson.Contains("\"substantivos\"") && dbJson.Contains("\"verbos_quadripartite\"");
                        string msg = "TEST_HEADLESS_OK=" + valid + " PORT=" + server.Port + " BYTES=" + dbJson.Length + " FORMS=" + server.TotalForms + " SOURCE=" + server.ActiveSource;
                        Console.WriteLine(msg);
                        try
                        {
                            string logPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "headless_test_result.txt");
                            File.WriteAllText(logPath, msg, Encoding.UTF8);
                        }
                        catch { }
                        server.Stop();
                        return valid ? 0 : 1;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("TEST_HEADLESS_ERROR=" + ex.Message);
                    server.Stop();
                    return 2;
                }
            }

            if (!string.IsNullOrEmpty(server.CloudUrl))
            {
                ThreadPool.QueueUserWorkItem(_ =>
                {
                    string msg;
                    server.SyncFromCloud(server.CloudUrl, out msg);
                });
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LauncherForm(server));
            server.Stop();
            return 0;
        }
    }
}
