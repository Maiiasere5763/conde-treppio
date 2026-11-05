using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;

[assembly: AssemblyTitle("Codice Lexicografico Imperial da Lingua Treppia (V8.1)")]
[assembly: AssemblyDescription("Launcher Executavel e Servidor Embarcado do Dicionario Treppio (/conde)")]
[assembly: AssemblyCompany("Chancelaria Imperial de Treppenia")]
[assembly: AssemblyProduct("Codice Treppio Conde V8.1")]
[assembly: AssemblyVersion("8.1.0.0")]

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

        private readonly string _appDataDir;
        private readonly string _cachedDbPath;
        private readonly string _cloudConfigPath;
        private readonly string _localCondeDbPath = @"D:\Conde_Treppio\sandbox\dicionario_exaustivo\dicionario_formas_expandidas.json";
        private readonly string _localCondeHtmlPath = @"D:\Conde_Treppio\sandbox\ui_dicionario\index.html";

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
            // 1. Carregar HTML (prioriza arquivo local do /conde se existir, senão usa recurso embutido no .exe)
            if (File.Exists(_localCondeHtmlPath))
            {
                _cachedHtmlBytes = File.ReadAllBytes(_localCondeHtmlPath);
            }
            else
            {
                _cachedHtmlBytes = ReadEmbeddedResource("index.html");
            }

            // 2. Carregar Banco de Dados JSON (prioriza Nuvem sincronizada se mais recente, ou D:\Conde_Treppio, ou Embutido no .exe)
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
                    wc.Headers.Add("User-Agent", "CondeTreppioLauncher/8.1");
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
                    ActiveSource = "Nuvem Sincronizada (Git/Google Drive)";
                    message = "Banco de dados atualizado com sucesso da nuvem!";
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
                message = "Base embutida recarregada.";
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
                    p.WaitForExit(15000);
                }
                ReloadPayloads();
                ActiveSource = "Base Local /conde Recompilada";
                message = "Base local D:\\Conde_Treppio recompilada com sucesso!";
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
                    string path = firstLine[1];

                    if (path.StartsWith("/api/db"))
                    {
                        SendResponse(stream, "200 OK", "application/json; charset=utf-8", _cachedJsonBytes);
                    }
                    else if (path.StartsWith("/api/recompilar") && method == "POST")
                    {
                        string msg;
                        RecompileLocalConde(out msg);
                        string body = "{\"status\":\"ok\",\"source\":\"" + EscapeJson(ActiveSource) + "\",\"db\":" + Encoding.UTF8.GetString(_cachedJsonBytes) + "}";
                        SendResponse(stream, "200 OK", "application/json; charset=utf-8", Encoding.UTF8.GetBytes(body));
                    }
                    else if (path.StartsWith("/api/cloud-config") && method == "POST")
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
                    else if (path.StartsWith("/dados_dicionario_conde.js"))
                    {
                        string js = "window.CONDE_DB = " + Encoding.UTF8.GetString(_cachedJsonBytes) + ";";
                        SendResponse(stream, "200 OK", "application/javascript; charset=utf-8", Encoding.UTF8.GetBytes(js));
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
        private Label _lblStatus;
        private Label _lblUrl;
        private TextBox _txtCloudUrl;
        private Label _lblFeedback;

        public LauncherForm(EmbeddedServer server)
        {
            _server = server;
            Text = "Códice Lexicográfico Imperial — Língua Tréppia (Era Clássica V8.1 | /conde)";
            Size = new Size(700, 450);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(11, 13, 19);
            ForeColor = Color.FromArgb(238, 241, 248);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;

            Font titleFont = new Font("Georgia", 15f, FontStyle.Bold);
            Font subFont = new Font("Segoe UI", 9.5f, FontStyle.Regular);
            Font boldFont = new Font("Segoe UI", 9.5f, FontStyle.Bold);
            Font monoFont = new Font("Consolas", 9f, FontStyle.Regular);

            Panel headerPanel = new Panel
            {
                Dock = DockStyle.Top,
                Height = 82,
                BackColor = Color.FromArgb(18, 22, 33),
                Padding = new Padding(20, 14, 20, 10)
            };

            Label lblTitle = new Label
            {
                Text = "CÓDICE LEXICOGRÁFICO IMPERIAL DO TRÉPPIO (V8.1)",
                Font = titleFont,
                ForeColor = Color.FromArgb(255, 216, 107),
                AutoSize = true,
                Location = new Point(20, 14)
            };

            Label lblSubtitle = new Label
            {
                Text = "310 Substantivos • 272 Verbos Quadripartites • 68 Adjetivos • 74 Advérbios • 37.769 Formas",
                Font = subFont,
                ForeColor = Color.FromArgb(166, 176, 201),
                AutoSize = true,
                Location = new Point(22, 46)
            };

            headerPanel.Controls.Add(lblTitle);
            headerPanel.Controls.Add(lblSubtitle);
            Controls.Add(headerPanel);

            _lblStatus = new Label
            {
                Text = "Fonte Ativa: " + _server.ActiveSource,
                Font = boldFont,
                ForeColor = Color.FromArgb(56, 184, 135),
                AutoSize = true,
                Location = new Point(24, 100)
            };
            Controls.Add(_lblStatus);

            _lblUrl = new Label
            {
                Text = "Servidor Local Embarcado: http://127.0.0.1:" + _server.Port,
                Font = monoFont,
                ForeColor = Color.FromArgb(88, 153, 245),
                AutoSize = true,
                Location = new Point(24, 124)
            };
            Controls.Add(_lblUrl);

            Button btnOpenApp = CreateStyledButton(
                "📖 ABRIR DICIONÁRIO TRÉPPIO (JANELA DEDICADA)",
                new Point(24, 158),
                new Size(636, 48),
                Color.FromArgb(46, 39, 20),
                Color.FromArgb(255, 216, 107)
            );
            btnOpenApp.Font = new Font("Segoe UI", 11f, FontStyle.Bold);
            btnOpenApp.Click += (s, e) => LaunchDedicatedWindow();
            Controls.Add(btnOpenApp);

            Label lblCloud = new Label
            {
                Text = "URL do Banco de Dados Online (GitHub Raw ou Link Público do Google Drive):",
                Font = subFont,
                ForeColor = Color.FromArgb(226, 185, 75),
                AutoSize = true,
                Location = new Point(24, 224)
            };
            Controls.Add(lblCloud);

            _txtCloudUrl = new TextBox
            {
                Location = new Point(24, 248),
                Size = new Size(636, 28),
                BackColor = Color.FromArgb(23, 28, 43),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = monoFont,
                Text = _server.CloudUrl
            };
            Controls.Add(_txtCloudUrl);

            Button btnSyncCloud = CreateStyledButton(
                "☁️ Sincronizar da Nuvem (Git / Drive)",
                new Point(24, 286),
                new Size(310, 38),
                Color.FromArgb(23, 28, 43),
                Color.FromArgb(238, 241, 248)
            );
            btnSyncCloud.Click += OnSyncCloudClick;
            Controls.Add(btnSyncCloud);

            Button btnRecompileLocal = CreateStyledButton(
                "🔨 Recompilar e Sincronizar Base /conde",
                new Point(350, 286),
                new Size(310, 38),
                Color.FromArgb(23, 28, 43),
                Color.FromArgb(226, 185, 75)
            );
            btnRecompileLocal.Click += OnRecompileClick;
            Controls.Add(btnRecompileLocal);

            _lblFeedback = new Label
            {
                Text = "Pronto. O dicionário funciona 100% offline e também sincroniza via GitHub ou Google Drive.",
                Font = subFont,
                ForeColor = Color.FromArgb(166, 176, 201),
                AutoSize = false,
                Size = new Size(636, 45),
                Location = new Point(24, 338)
            };
            Controls.Add(_lblFeedback);

            Shown += (s, e) => LaunchDedicatedWindow();
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
            b.FlatAppearance.BorderColor = Color.FromArgb(226, 185, 75);
            b.FlatAppearance.BorderSize = 1;
            return b;
        }

        private void OnSyncCloudClick(object sender, EventArgs e)
        {
            _lblFeedback.ForeColor = Color.FromArgb(255, 216, 107);
            _lblFeedback.Text = "Conectando à nuvem para baixar dicionario_formas_expandidas.json...";
            Application.DoEvents();

            string msg;
            bool ok = _server.SyncFromCloud(_txtCloudUrl.Text, out msg);
            _lblStatus.Text = "Fonte Ativa: " + _server.ActiveSource;
            _lblFeedback.ForeColor = ok ? Color.FromArgb(56, 184, 135) : Color.FromArgb(217, 78, 90);
            _lblFeedback.Text = msg;
        }

        private void OnRecompileClick(object sender, EventArgs e)
        {
            _lblFeedback.ForeColor = Color.FromArgb(255, 216, 107);
            _lblFeedback.Text = "Recompilando base morfológica do /conde (37.769 formas)...";
            Application.DoEvents();

            string msg;
            bool ok = _server.RecompileLocalConde(out msg);
            _lblStatus.Text = "Fonte Ativa: " + _server.ActiveSource;
            _lblFeedback.ForeColor = ok ? Color.FromArgb(56, 184, 135) : Color.FromArgb(217, 78, 90);
            _lblFeedback.Text = msg;
        }

        public void LaunchDedicatedWindow()
        {
            string url = "http://127.0.0.1:" + _server.Port;
            try
            {
                // Tentar abrir em modo Aplicativo dedicado via Microsoft Edge ou Google Chrome
                string[] edgePaths = new[]
                {
                    @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    @"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                };
                foreach (string ep in edgePaths)
                {
                    if (File.Exists(ep))
                    {
                        Process.Start(ep, "--app=" + url + " --window-size=1440,900");
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
        [STAThread]
        private static int Main(string[] args)
        {
            EmbeddedServer server = new EmbeddedServer();
            server.Start();

            // Modo de verificação automatizada (--test-headless)
            if (args != null && args.Length > 0 && args[0] == "--test-headless")
            {
                try
                {
                    using (WebClient wc = new WebClient())
                    {
                        wc.Encoding = Encoding.UTF8;
                        string dbJson = wc.DownloadString("http://127.0.0.1:" + server.Port + "/api/db");
                        bool valid = dbJson.Contains("\"substantivos\"") && dbJson.Contains("\"verbos_quadripartite\"");
                        string msg = "TEST_HEADLESS_OK=" + valid + " PORT=" + server.Port + " BYTES=" + dbJson.Length + " SOURCE=" + server.ActiveSource;
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

            // Se houver URL da nuvem salva, sincroniza silenciosamente em background ao abrir
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
