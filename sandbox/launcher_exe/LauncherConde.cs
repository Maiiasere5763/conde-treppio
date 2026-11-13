using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Speech.Synthesis;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;

[assembly: AssemblyTitle("Codice Lexicografico Imperial da Lingua Treppia (V8.4)")]
[assembly: AssemblyDescription("Launcher Executavel, Servidor Embarcado, Pronuncia IPA e Tradutor Bilingue TR-PT (/conde)")]
[assembly: AssemblyCompany("Chancelaria Imperial de Treppenia")]
[assembly: AssemblyProduct("Codice Treppio Conde V8.4")]
[assembly: AssemblyVersion("8.4.0.0")]

namespace CondeTreppioLauncher
{
    public class LexEntry
    {
        public string Treppio { get; set; }
        public string PtMeaning { get; set; }
        public string PtNorm { get; set; }
        public string ClassTag { get; set; }
        public string Detail { get; set; }
        public int Boost { get; set; }
    }

    public class IpaWordInfo
    {
        public string Word { get; set; }
        public string Ipa { get; set; }
        public string SyllablesJoined { get; set; }
        public string Notes { get; set; }
    }

    public class TreppioLexiconEngine
    {
        private static readonly HashSet<char> HaploVowels = new HashSet<char>(
            "aeiouyáéíóúýäëïöüAEIOUYÁÉÍÓÚÝÄËÏÖÜ".ToCharArray()
        );

        private static readonly HashSet<string> HaploOnsets = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "bl", "br", "dr", "fl", "fr", "gl", "gr", "kl", "kr", "pl", "pr", "sf", "tr"
        };

        private static readonly HashSet<string> HaploExempt = new HashSet<string>(StringComparer.Ordinal)
        {
            "Jesus", "Maria", "Giovanni", "Sprezzatura", "Christus", "Kristus",
            "Pontius", "Pilatus", "Eä", "Ilúvatar", "Ainur", "Valar"
        };

        private readonly object _lock = new object();
        private List<LexEntry> _ptEntries = new List<LexEntry>();
        private Dictionary<string, List<LexEntry>> _trReverse = new Dictionary<string, List<LexEntry>>(StringComparer.OrdinalIgnoreCase);
        private Dictionary<string, string> _corpusByTreppio = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        public volatile bool IsReady;
        public int IndexedFormsCount { get; private set; }
        public int IndexedLemmasCount { get; private set; }

        public static string StripAccents(string input)
        {
            if (string.IsNullOrEmpty(input)) return "";
            string norm = input.Normalize(NormalizationForm.FormD);
            StringBuilder sb = new StringBuilder(norm.Length);
            for (int i = 0; i < norm.Length; i++)
            {
                UnicodeCategory cat = CharUnicodeInfo.GetUnicodeCategory(norm[i]);
                if (cat != UnicodeCategory.NonSpacingMark)
                {
                    sb.Append(norm[i]);
                }
            }
            return sb.ToString().ToLowerInvariant();
        }

        public static List<string> Syllabify(string part)
        {
            List<string> res = new List<string>();
            if (string.IsNullOrEmpty(part)) return res;
            int n = part.Length;
            List<int[]> runs = new List<int[]>();
            int idx = 0;
            while (idx < n)
            {
                if (HaploVowels.Contains(part[idx]))
                {
                    int s = idx;
                    while (idx < n && HaploVowels.Contains(part[idx])) idx++;
                    runs.Add(new int[] { s, idx });
                }
                else
                {
                    idx++;
                }
            }
            if (runs.Count == 0)
            {
                res.Add(part);
                return res;
            }
            List<int> bounds = new List<int>();
            bounds.Add(0);
            for (int r = 0; r < runs.Count - 1; r++)
            {
                int cStart = runs[r][1];
                int cEnd = runs[r + 1][0];
                string clust = part.Substring(cStart, cEnd - cStart).ToLowerInvariant();
                if (clust.Length <= 1)
                {
                    bounds.Add(cStart);
                }
                else if (clust.Length == 2)
                {
                    if (clust[0] != clust[1] && HaploOnsets.Contains(clust)) bounds.Add(cStart);
                    else bounds.Add(cStart + 1);
                }
                else
                {
                    string tail = clust.Substring(clust.Length - 2);
                    if (HaploOnsets.Contains(tail) && tail[0] != tail[1]) bounds.Add(cEnd - 2);
                    else bounds.Add(cEnd - 1);
                }
            }
            bounds.Add(n);
            for (int i = 0; i < bounds.Count - 1; i++)
            {
                res.Add(part.Substring(bounds[i], bounds[i + 1] - bounds[i]));
            }
            return res;
        }

        public static string ApplyHaplology(string word)
        {
            if (string.IsNullOrEmpty(word) || word.Contains(" ") || word.Length < 4 || HaploExempt.Contains(word) || word.Contains("'"))
            {
                return word;
            }
            string punct = "";
            string w = word;
            char last = w[w.Length - 1];
            if (last == '!' || last == '?' || last == '.' || last == ',' || last == ';' || last == ':')
            {
                punct = last.ToString();
                w = w.Substring(0, w.Length - 1);
            }
            if (w.Length < 4 || w.Contains("'")) return word;
            List<string> syls = Syllabify(w);
            if (syls.Count < 2) return word;
            List<string> outSyls = new List<string>();
            outSyls.Add(syls[0]);
            bool changed = false;
            for (int i = 1; i < syls.Count; i++)
            {
                string prevS = outSyls[outSyls.Count - 1];
                string currS = syls[i];
                char c1 = char.ToLowerInvariant(prevS[0]);
                char c2 = char.ToLowerInvariant(currS[0]);
                bool isC1Cons = !HaploVowels.Contains(c1) && char.IsLetter(c1);
                bool isC2Cons = !HaploVowels.Contains(c2) && char.IsLetter(c2);
                bool isGem = char.ToLowerInvariant(prevS[prevS.Length - 1]) == c2;
                if (!changed && isC1Cons && isC2Cons && c1 == c2 && !isGem)
                {
                    string rem = currS.Substring(1);
                    if (rem.Length > 0 && (HaploVowels.Contains(rem[0]) || (currS.Length >= 2 && HaploOnsets.Contains(currS.Substring(0, 2)) && c2 == 'd' && prevS.ToLowerInvariant().EndsWith("da"))))
                    {
                        outSyls.Add("'" + rem);
                        changed = true;
                        continue;
                    }
                }
                outSyls.Add(currS);
            }
            return string.Join("", outSyls.ToArray()) + punct;
        }

        public static string SyllableToIpa(string syl)
        {
            string s = (syl ?? "").ToLowerInvariant();
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < s.Length; i++)
            {
                char ch = s[i];
                char next = (i + 1 < s.Length) ? s[i + 1] : '\0';
                if (ch == '\'') { sb.Append('ʔ'); continue; }
                if (ch == 'r' && next == 'r') { sb.Append('r'); i++; continue; }
                if (ch == next && "tdkbgpszmfln".IndexOf(ch) >= 0)
                {
                    sb.Append(ch == 'g' ? 'ɡ' : ch);
                    sb.Append('ː');
                    i++;
                    continue;
                }
                switch (ch)
                {
                    case 'a': case 'á': sb.Append('a'); break;
                    case 'e': case 'é': sb.Append('e'); break;
                    case 'ë': sb.Append('ə'); break;
                    case 'i': case 'í': case 'y': case 'ý': case 'ï': sb.Append('i'); break;
                    case 'o': sb.Append('ɔ'); break;
                    case 'ó': sb.Append('o'); break;
                    case 'u': case 'ú': sb.Append('u'); break;
                    case 'ä': sb.Append('ɛ'); break;
                    case 'ö': sb.Append('ø'); break;
                    case 'ü': sb.Append('y'); break;
                    case 'g': sb.Append('ɡ'); break;
                    case 'r': sb.Append('ɾ'); break;
                    default: sb.Append(ch); break;
                }
            }
            return sb.ToString();
        }

        public static IpaWordInfo AnalyzeWordIpa(string word)
        {
            string clean = Regex.Replace(word ?? "", @"[.,;:!?()\[\]""“”]", "").Trim();
            if (string.IsNullOrEmpty(clean)) return null;
            string hap = ApplyHaplology(clean);
            string[] segs = hap.Split('\'');
            List<string> syls = new List<string>();
            for (int sIdx = 0; sIdx < segs.Length; sIdx++)
            {
                if (string.IsNullOrEmpty(segs[sIdx])) continue;
                List<string> parts = Syllabify(segs[sIdx]);
                for (int pIdx = 0; pIdx < parts.Count; pIdx++)
                {
                    syls.Add((sIdx > 0 && pIdx == 0 ? "'" : "") + parts[pIdx]);
                }
            }
            if (syls.Count == 0) syls.Add(hap);
            int stressed = -1;
            for (int i = 0; i < syls.Count; i++)
            {
                if (Regex.IsMatch(syls[i], "[áéíóúýÁÉÍÓÚÝ]")) { stressed = i; break; }
            }
            if (stressed < 0) stressed = syls.Count > 1 ? syls.Count - 2 : 0;

            List<string> ipaSyls = new List<string>();
            for (int i = 0; i < syls.Count; i++)
            {
                string raw = SyllableToIpa(syls[i]);
                ipaSyls.Add(i == stressed ? "ˈ" + raw : raw);
            }
            List<string> notes = new List<string>();
            if (hap.IndexOf('g') >= 0 || hap.IndexOf('G') >= 0) notes.Add("G=/ɡ/ (guitarra)");
            if (hap.IndexOf('s') >= 0 || hap.IndexOf('S') >= 0) notes.Add("S=/s/ (sapato)");
            if (hap.IndexOf('x') >= 0 || hap.IndexOf('X') >= 0) notes.Add("X=/x/");
            if (hap.Contains("'")) notes.Add("Haplologia [ʔ]");
            return new IpaWordInfo
            {
                Word = hap,
                Ipa = "/" + string.Join(".", ipaSyls.ToArray()) + "/",
                SyllablesJoined = string.Join(" · ", syls.ToArray()),
                Notes = string.Join(" • ", notes.ToArray())
            };
        }

        public static string ToTtsPtBr(string text)
        {
            if (string.IsNullOrEmpty(text)) return "";
            string s = text.Replace("'", " ");
            s = Regex.Replace(s, @"([gG]+)(?=[eéëiíyýEÉËIÍYÝ])", "$1u");
            s = Regex.Replace(s, @"([aeiouyáéíóúýäëïöüAEIOUYÁÉÍÓÚÝÄËÏÖÜ])s([aeiouyáéíóúýäëïöüAEIOUYÁÉÍÓÚÝÄËÏÖÜ])", "$1ss$2");
            s = s.Replace("y", "i").Replace("Y", "I").Replace("ë", "ê").Replace("Ë", "Ê");
            return s;
        }

        private static void AddPtEntry(List<LexEntry> ptList, string treppio, string ptMeaning, string classTag, string detail, int boost)
        {
            if (string.IsNullOrEmpty(treppio) || string.IsNullOrEmpty(ptMeaning)) return;
            ptList.Add(new LexEntry
            {
                Treppio = treppio,
                PtMeaning = ptMeaning,
                PtNorm = StripAccents(ptMeaning).Trim(),
                ClassTag = classTag,
                Detail = detail ?? "",
                Boost = boost
            });
        }

        private static void AddTrForm(Dictionary<string, List<LexEntry>> rev, ref int count, string formStr, LexEntry template)
        {
            if (string.IsNullOrEmpty(formStr)) return;
            string clean = formStr.Replace("!", "").Replace("?", "").Trim().ToLowerInvariant();
            if (string.IsNullOrEmpty(clean)) return;
            List<LexEntry> list;
            if (!rev.TryGetValue(clean, out list))
            {
                list = new List<LexEntry>();
                rev[clean] = list;
            }
            if (list.Count < 8)
            {
                list.Add(template);
                count++;
            }
        }

        private static Dictionary<string, object> AsDict(object o)
        {
            return o as Dictionary<string, object>;
        }

        private static string GetStr(Dictionary<string, object> d, string key)
        {
            object v;
            if (d != null && d.TryGetValue(key, out v) && v != null) return v.ToString();
            return "";
        }

        public void BuildFromJsonBytes(byte[] jsonBytes)
        {
            if (jsonBytes == null || jsonBytes.Length == 0) return;
            string json = Encoding.UTF8.GetString(jsonBytes);
            JavaScriptSerializer ser = new JavaScriptSerializer();
            ser.MaxJsonLength = int.MaxValue;
            ser.RecursionLimit = 100;

            Dictionary<string, object> root = ser.Deserialize<Dictionary<string, object>>(json);
            if (root == null) return;

            List<LexEntry> nextPt = new List<LexEntry>();
            Dictionary<string, List<LexEntry>> nextRev = new Dictionary<string, List<LexEntry>>(StringComparer.OrdinalIgnoreCase);
            Dictionary<string, string> nextCorpus = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            int revCount = 0;

            string[,] funcWords = new string[,] {
                { "não", "ne", "Advérbio Negativo", "Negação factual pré-verbal." },
                { "nao", "ne", "Advérbio Negativo", "Negação factual pré-verbal." },
                { "e", "et", "Conjunção", "Aditiva ('e')." },
                { "ou", "u", "Conjunção", "Alternativa ('ou')." },
                { "que", "ke", "Conjunção / Relativo", "Pronome relativo / conjunção integrante." },
                { "como", "ko", "Conjunção", "Comparação ('como, assim como')." },
                { "se", "so", "Conjunção", "Condicional ('se')." },
                { "em", "in", "Preposição", "Posição estática (Dativo) ou movimento (Acusativo)." },
                { "no", "in", "Preposição", "Em / no (+ Dat. ou Acu.)." },
                { "na", "in", "Preposição", "Em / na (+ Dat. ou Acu.)." },
                { "para", "ad", "Preposição", "Direção (+ Acu.) ou finalidade (+ -ur)." },
                { "a", "ad", "Preposição", "Direção (+ Acu.) ou Dativo sintético." },
                { "de", "ex", "Preposição", "Origem/procedência (+ Dat.) ou Genitivo." },
                { "do", "ex", "Preposição", "De/do (+ Dat.) ou Genitivo." },
                { "da", "ex", "Preposição", "De/da (+ Dat.) ou Genitivo." },
                { "sob", "ponu", "Preposição", "Sob o poder ou jurisdição de." },
                { "eu", "eo", "Pronome Pessoal", "1ª Sg (pro-drop verbal -m)." },
                { "tu", "to", "Pronome Pessoal", "2ª Sg (pro-drop verbal -s)." },
                { "você", "to", "Pronome Pessoal", "2ª Sg (pro-drop verbal -s)." },
                { "nos", "no", "Pronome Pessoal", "1ª Pl (pro-drop verbal -n)." },
                { "vós", "vo", "Pronome Pessoal", "2ª Pl (pro-drop verbal -t)." },
                { "hoje", "sambel", "Advérbio", "San + bel (nb -> mb): hoje." },
                { "agora", "santonk", "Advérbio", "San + tonkre: agora." },
                { "sim", "yo", "Advérbio", "Afirmação prática." },
                { "amém", "Zo es", "Fórmula Litúrgica", "Assim sê! / Amém!" },
                { "bom dia", "Moba'el", "Saudação", "Moba + bel com haplologia." }
            };
            for (int i = 0; i < funcWords.GetLength(0); i++)
            {
                AddPtEntry(nextPt, funcWords[i, 1], funcWords[i, 0], funcWords[i, 2], funcWords[i, 3], 45);
            }

            Dictionary<string, object> subs = AsDict(root.ContainsKey("substantivos") ? root["substantivos"] : null);
            if (subs != null)
            {
                foreach (KeyValuePair<string, object> kv in subs)
                {
                    Dictionary<string, object> obj = AsDict(kv.Value);
                    if (obj == null) continue;
                    string decl = GetStr(obj, "declinacao");
                    string sig = GetStr(obj, "significado");
                    string etym = GetStr(obj, "etimologia");
                    string cTag = "Substantivo (" + decl + "ª Decl.)";
                    AddPtEntry(nextPt, kv.Key, sig, cTag, etym, 10);
                    Dictionary<string, object> formas = AsDict(obj.ContainsKey("formas") ? obj["formas"] : null);
                    if (formas != null)
                    {
                        foreach (KeyValuePair<string, object> fkv in formas)
                        {
                            string fv = fkv.Value != null ? fkv.Value.ToString() : "";
                            AddTrForm(nextRev, ref revCount, fv, new LexEntry { Treppio = kv.Key, PtMeaning = sig, ClassTag = cTag, Detail = fkv.Key });
                        }
                    }
                }
            }

            Dictionary<string, object> adjs = AsDict(root.ContainsKey("adjetivos") ? root["adjetivos"] : null);
            if (adjs != null)
            {
                foreach (KeyValuePair<string, object> kv in adjs)
                {
                    Dictionary<string, object> obj = AsDict(kv.Value);
                    if (obj == null) continue;
                    string sig = GetStr(obj, "Significado");
                    AddPtEntry(nextPt, kv.Key, sig, "Adjetivo", "Comp: " + GetStr(obj, "Comparativo"), 8);
                    foreach (KeyValuePair<string, object> fkv in obj)
                    {
                        if (fkv.Key == "Significado") continue;
                        string fv = fkv.Value != null ? fkv.Value.ToString() : "";
                        AddTrForm(nextRev, ref revCount, fv, new LexEntry { Treppio = kv.Key, PtMeaning = sig, ClassTag = "Adjetivo", Detail = fkv.Key });
                    }
                }
            }

            Dictionary<string, object> advs = AsDict(root.ContainsKey("adverbios") ? root["adverbios"] : null);
            if (advs != null)
            {
                foreach (KeyValuePair<string, object> kv in advs)
                {
                    Dictionary<string, object> obj = AsDict(kv.Value);
                    if (obj == null) continue;
                    string sig = GetStr(obj, "significado");
                    string subc = GetStr(obj, "subclasse");
                    AddPtEntry(nextPt, kv.Key, sig, "Advérbio (" + subc + ")", GetStr(obj, "etimologia"), 6);
                    AddTrForm(nextRev, ref revCount, kv.Key, new LexEntry { Treppio = kv.Key, PtMeaning = sig, ClassTag = "Advérbio", Detail = subc });
                }
            }

            Dictionary<string, object> prons = AsDict(root.ContainsKey("pronomes") ? root["pronomes"] : null);
            if (prons != null)
            {
                foreach (KeyValuePair<string, object> kv in prons)
                {
                    Dictionary<string, object> obj = AsDict(kv.Value);
                    if (obj == null) continue;
                    string desc = obj.ContainsKey("esfera") ? (kv.Key + ": " + GetStr(obj, "esfera")) : kv.Key;
                    string nomClean = Regex.Replace(GetStr(obj, "Nom"), @"\([^)]*\)", "").Trim();
                    AddPtEntry(nextPt, string.IsNullOrEmpty(nomClean) ? kv.Key : nomClean, desc, "Pronome", "", 15);
                    foreach (KeyValuePair<string, object> pkv in obj)
                    {
                        if (pkv.Key == "esfera" || pkv.Value == null) continue;
                        string[] parts = pkv.Value.ToString().Split('/');
                        for (int i = 0; i < parts.Length; i++)
                        {
                            string tok = Regex.Replace(parts[i], @"\([^)]*\)", "").Trim();
                            AddTrForm(nextRev, ref revCount, tok, new LexEntry { Treppio = kv.Key, PtMeaning = desc, ClassTag = "Pronome", Detail = pkv.Key });
                        }
                    }
                }
            }

            Dictionary<string, object> nums = AsDict(root.ContainsKey("numerais") ? root["numerais"] : null);
            if (nums != null)
            {
                foreach (KeyValuePair<string, object> kv in nums)
                {
                    Dictionary<string, object> obj = AsDict(kv.Value);
                    if (obj == null) continue;
                    string card = GetStr(obj, "cardinal");
                    string ord = Regex.Replace(GetStr(obj, "ordinal"), @"\([^)]*\)", "").Trim();
                    string desc = "numeral " + kv.Key + " (" + card + ", " + ord + ")";
                    AddPtEntry(nextPt, card + " / " + ord, desc, "Numeral", GetStr(obj, "compostos"), 14);
                    foreach (KeyValuePair<string, object> nkv in obj)
                    {
                        if (nkv.Key == "compostos" || nkv.Value == null) continue;
                        string[] parts = nkv.Value.ToString().Split('/');
                        for (int i = 0; i < parts.Length; i++)
                        {
                            string tok = Regex.Replace(parts[i], @"\([^)]*\)", "").Trim();
                            AddTrForm(nextRev, ref revCount, tok, new LexEntry { Treppio = card, PtMeaning = desc, ClassTag = "Numeral", Detail = kv.Key + " (" + nkv.Key + ")" });
                        }
                    }
                }
            }

            Dictionary<string, object> partsDic = AsDict(root.ContainsKey("particulas_e_afixos") ? root["particulas_e_afixos"] : null);
            if (partsDic != null)
            {
                foreach (KeyValuePair<string, object> kv in partsDic)
                {
                    Dictionary<string, object> obj = AsDict(kv.Value);
                    if (obj == null) continue;
                    string desc = GetStr(obj, "descricao");
                    string cls = GetStr(obj, "classe");
                    AddPtEntry(nextPt, kv.Key, desc, cls, "", 18);
                    string[] toks = kv.Key.Split('/');
                    for (int i = 0; i < toks.Length; i++)
                    {
                        string t = Regex.Replace(toks[i], @"\([^)]*\)", "").Trim();
                        if (!string.IsNullOrEmpty(t) && !t.StartsWith("-") && !t.EndsWith("-"))
                        {
                            AddTrForm(nextRev, ref revCount, t, new LexEntry { Treppio = kv.Key, PtMeaning = desc, ClassTag = cls, Detail = "Invariável" });
                        }
                    }
                }
            }

            Dictionary<string, object> diacs = AsDict(root.ContainsKey("registro_diacronico_e_variantes") ? root["registro_diacronico_e_variantes"] : null);
            if (diacs != null)
            {
                foreach (KeyValuePair<string, object> kv in diacs)
                {
                    Dictionary<string, object> obj = AsDict(kv.Value);
                    if (obj == null) continue;
                    string analise = GetStr(obj, "analise");
                    string est = GetStr(obj, "estatuto");
                    string eq = GetStr(obj, "equivalente_canonico");
                    AddPtEntry(nextPt, kv.Key + " -> " + eq, analise, est, eq, 2);
                    string[] toks = kv.Key.Split('/');
                    for (int i = 0; i < toks.Length; i++)
                    {
                        AddTrForm(nextRev, ref revCount, toks[i].Trim(), new LexEntry { Treppio = kv.Key, PtMeaning = analise, ClassTag = est, Detail = eq });
                    }
                }
            }

            Dictionary<string, object> verbs = AsDict(root.ContainsKey("verbos_quadripartite") ? root["verbos_quadripartite"] : null);
            if (verbs != null)
            {
                string[] persons = new string[] { "1ª Sg (-m)", "2ª Sg (-s)", "3ª Sg/Pl", "1ª Pl (-n)", "2ª Pl (-t)" };
                foreach (KeyValuePair<string, object> vkv in verbs)
                {
                    string vRoot = vkv.Key;
                    Dictionary<string, object> axes = AsDict(vkv.Value);
                    if (axes == null) continue;
                    foreach (KeyValuePair<string, object> akv in axes)
                    {
                        Dictionary<string, object> axObj = AsDict(akv.Value);
                        if (axObj == null) continue;
                        string mean = GetStr(axObj, "meaning");
                        Dictionary<string, object> conj = AsDict(axObj.ContainsKey("conjugation") ? axObj["conjugation"] : null);
                        if (conj == null) continue;
                        string inf = GetStr(conj, "Infinitivo(-ur)");
                        string imp = GetStr(conj, "Imperativo(Raiz)");
                        string cat = "Verbo [" + akv.Key + "]";
                        AddPtEntry(nextPt, inf, mean, cat, "Raiz " + vRoot + "- | Imp: " + imp, akv.Key.StartsWith("1.") ? 12 : 4);
                        AddTrForm(nextRev, ref revCount, inf, new LexEntry { Treppio = vRoot + "-", PtMeaning = mean, ClassTag = cat, Detail = "Infinitivo" });
                        AddTrForm(nextRev, ref revCount, imp, new LexEntry { Treppio = vRoot + "-", PtMeaning = mean, ClassTag = cat, Detail = "Imperativo" });
                        AddTrForm(nextRev, ref revCount, GetStr(conj, "Interrogativo.2Pl(-ka)"), new LexEntry { Treppio = vRoot + "-", PtMeaning = mean, ClassTag = cat, Detail = "Interrogativo 2ª Pl" });

                        foreach (KeyValuePair<string, object> ckv in conj)
                        {
                            object[] arr = ckv.Value as object[];
                            if (arr != null)
                            {
                                for (int pIdx = 0; pIdx < arr.Length; pIdx++)
                                {
                                    string wf = arr[pIdx] != null ? arr[pIdx].ToString() : "";
                                    string pLbl = pIdx < persons.Length ? persons[pIdx] : "";
                                    AddTrForm(nextRev, ref revCount, wf, new LexEntry { Treppio = inf, PtMeaning = mean, ClassTag = cat, Detail = ckv.Key + " " + pLbl });
                                }
                                continue;
                            }
                            Dictionary<string, object> subDict = AsDict(ckv.Value);
                            if (subDict != null)
                            {
                                foreach (KeyValuePair<string, object> sdkv in subDict)
                                {
                                    string wf = sdkv.Value != null ? sdkv.Value.ToString() : "";
                                    AddTrForm(nextRev, ref revCount, wf, new LexEntry { Treppio = vRoot + "-", PtMeaning = mean, ClassTag = cat, Detail = ckv.Key + ": " + sdkv.Key });
                                }
                            }
                        }
                    }
                }
            }

            object[] corpusArr = root.ContainsKey("corpus_canonico") ? root["corpus_canonico"] as object[] : null;
            if (corpusArr != null)
            {
                for (int i = 0; i < corpusArr.Length; i++)
                {
                    Dictionary<string, object> cObj = AsDict(corpusArr[i]);
                    if (cObj == null) continue;
                    string tr = GetStr(cObj, "treppio");
                    string pt = GetStr(cObj, "portugues");
                    string tit = GetStr(cObj, "titulo");
                    if (!string.IsNullOrEmpty(tr) && !string.IsNullOrEmpty(pt))
                    {
                        nextCorpus[tr] = tit + ": " + pt;
                        AddPtEntry(nextPt, tr, pt, "Corpus Canônico", tit, 5);
                    }
                }
            }

            lock (_lock)
            {
                _ptEntries = nextPt;
                _trReverse = nextRev;
                _corpusByTreppio = nextCorpus;
                IndexedFormsCount = revCount;
                IndexedLemmasCount = nextPt.Count;
                IsReady = true;
            }
        }

        private class ScoredLex
        {
            public int Score;
            public LexEntry Entry;
        }

        public List<LexEntry> SearchPtToken(string ptToken, int limit)
        {
            List<LexEntry> snapshot;
            lock (_lock) { snapshot = _ptEntries; }
            string q = StripAccents(ptToken).Trim();
            List<LexEntry> outList = new List<LexEntry>();
            if (string.IsNullOrEmpty(q) || snapshot.Count == 0) return outList;

            string qStem = q.Length > 4 ? Regex.Replace(q, "(s|es|os|as|mente|coes|cao|ado|ada|ar|er|ir)$", "") : q;
            List<ScoredLex> scored = new List<ScoredLex>();

            for (int i = 0; i < snapshot.Count; i++)
            {
                LexEntry item = snapshot[i];
                int sc = 0;
                int sepIdx = item.PtNorm.IndexOfAny(new char[] { ',', ';', '(' });
                string head = (sepIdx >= 0 ? item.PtNorm.Substring(0, sepIdx) : item.PtNorm).Trim();
                if (item.PtNorm == q)
                {
                    sc = 140;
                }
                else if (head == q)
                {
                    sc = 128;
                }
                else
                {
                    string[] headWords = Regex.Split(head, "[^a-z0-9]+");
                    bool inHead = false;
                    for (int h = 0; h < headWords.Length; h++)
                    {
                        if (headWords[h] == q) { inHead = true; break; }
                    }
                    string[] words = Regex.Split(item.PtNorm, "[^a-z0-9]+");
                    bool exactWord = false;
                    bool stemWord = false;
                    for (int w = 0; w < words.Length; w++)
                    {
                        if (words[w] == q) { exactWord = true; break; }
                        if (qStem.Length >= 3 && (words[w] == qStem || words[w].StartsWith(qStem))) stemWord = true;
                    }
                    if (inHead) sc = 105 - Math.Min(20, words.Length);
                    else if (exactWord) sc = 85 - Math.Min(25, words.Length * 2);
                    else if (stemWord) sc = 62 - Math.Min(20, words.Length);
                    else if (q.Length >= 3 && item.PtNorm.Contains(q)) sc = 40;
                }
                if (sc > 0)
                {
                    scored.Add(new ScoredLex { Score = sc + item.Boost, Entry = item });
                }
            }
            scored.Sort((a, b) => b.Score.CompareTo(a.Score));
            HashSet<string> seen = new HashSet<string>();
            for (int i = 0; i < scored.Count && outList.Count < limit; i++)
            {
                string key = scored[i].Entry.Treppio + "|" + scored[i].Entry.ClassTag;
                if (seen.Add(key)) outList.Add(scored[i].Entry);
            }
            return outList;
        }

        public string TranslatePtToTrReport(string query, out string primaryTreppio)
        {
            primaryTreppio = "";
            if (!IsReady) return "Indexando banco de dados em segundo plano... tente em 2 segundos.";
            string qRaw = (query ?? "").Trim();
            if (string.IsNullOrEmpty(qRaw)) return "Digite uma palavra ou frase em português.";

            string qNorm = StripAccents(qRaw);
            string[] tokens = Regex.Split(qNorm, @"\s+");
            HashSet<string> skips = new HashSet<string> { "o", "os", "um", "uma", "uns", "umas", "com", "por", "pelo", "pela" };

            List<string> synthWords = new List<string>();
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < tokens.Length; i++)
            {
                string t = Regex.Replace(tokens[i], @"[.,;:!?()\[\]""“”]", "");
                if (string.IsNullOrEmpty(t) || skips.Contains(t)) continue;
                List<LexEntry> cands = SearchPtToken(t, 4);
                if (cands.Count > 0)
                {
                    string top = cands[0].Treppio.Split('/')[0].Trim();
                    synthWords.Add(top);
                }
                else
                {
                    synthWords.Add("[" + t + "?]");
                }
            }

            List<LexEntry> direct = SearchPtToken(qRaw, 20);
            if (direct.Count > 0 && direct[0].PtNorm == qNorm && direct[0].Boost >= 40)
            {
                primaryTreppio = direct[0].Treppio;
            }
            else
            {
                primaryTreppio = string.Join(" ", synthWords.ToArray());
            }

            IpaWordInfo ipa = AnalyzeWordIpa(Regex.Replace(primaryTreppio, @"\[[^\]]+\]", "").Trim());
            sb.AppendLine("=== EQUIVALENTE SUGERIDO EM TRÉPPIO ===");
            sb.AppendLine("Tréppio: " + primaryTreppio);
            if (ipa != null) sb.AppendLine("IPA Est.: " + ipa.Ipa);
            sb.AppendLine();
            sb.AppendLine("=== VERBETES CORRESPONDENTES NO LÉXICO (TODAS AS 7 CLASSES) ===");
            if (direct.Count == 0 && tokens.Length == 1)
            {
                sb.AppendLine("Nenhum verbete direto encontrado para \"" + qRaw + "\".");
            }
            else
            {
                List<LexEntry> toShow = direct.Count > 0 ? direct : SearchPtToken(tokens[0], 15);
                for (int i = 0; i < toShow.Count; i++)
                {
                    LexEntry e = toShow[i];
                    sb.AppendFormat(
                        "• {0}  [{1}]  ->  {2}{3}\r\n",
                        e.Treppio,
                        e.ClassTag,
                        e.PtMeaning,
                        string.IsNullOrEmpty(e.Detail) ? "" : " (" + e.Detail + ")"
                    );
                }
            }
            return sb.ToString();
        }

        public string TranslateTrToPtReport(string query)
        {
            if (!IsReady) return "Indexando banco de dados em segundo plano... tente em 2 segundos.";
            string qRaw = (query ?? "").Trim();
            if (string.IsNullOrEmpty(qRaw)) return "Digite palavras ou frases em Tréppio.";

            Dictionary<string, List<LexEntry>> revSnap;
            Dictionary<string, string> corpSnap;
            lock (_lock)
            {
                revSnap = _trReverse;
                corpSnap = _corpusByTreppio;
            }

            StringBuilder sb = new StringBuilder();
            foreach (KeyValuePair<string, string> ckv in corpSnap)
            {
                if (ckv.Key.IndexOf(qRaw, StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    sb.AppendLine("=== PASSAGEM DO CORPUS CANÔNICO ===");
                    sb.AppendLine(ckv.Value);
                    sb.AppendLine();
                    break;
                }
            }

            string[] tokens = Regex.Split(qRaw, @"\s+");
            List<string> glosses = new List<string>();
            StringBuilder detailSb = new StringBuilder();
            for (int i = 0; i < tokens.Length; i++)
            {
                string clean = Regex.Replace(tokens[i], @"[.,;:!?()\[\]""“”]", "");
                if (string.IsNullOrEmpty(clean)) continue;
                string hap = ApplyHaplology(clean);
                List<LexEntry> list = null;
                if (!revSnap.TryGetValue(clean.ToLowerInvariant(), out list))
                {
                    revSnap.TryGetValue(hap.ToLowerInvariant(), out list);
                }
                IpaWordInfo ipa = AnalyzeWordIpa(hap);
                if (list != null && list.Count > 0)
                {
                    string shortMean = Regex.Split(list[0].PtMeaning ?? "", @"[,;(]")[0].Trim();
                    glosses.Add(string.IsNullOrEmpty(shortMean) ? list[0].Treppio : shortMean);
                    detailSb.AppendFormat("• {0} {1}\r\n", hap, ipa != null ? ipa.Ipa : "");
                    int maxShow = Math.Min(3, list.Count);
                    for (int m = 0; m < maxShow; m++)
                    {
                        LexEntry e = list[m];
                        detailSb.AppendFormat("    [{0}] {1} ({2}) -> {3}\r\n", e.ClassTag, e.Treppio, e.Detail, e.PtMeaning);
                    }
                }
                else
                {
                    glosses.Add("[" + clean + "?]");
                    detailSb.AppendFormat("• {0} {1} -> (não encontrado diretamente nas formas indexadas)\r\n", hap, ipa != null ? ipa.Ipa : "");
                }
            }

            sb.AppendLine("=== GLOSA MORFOLÓGICA EM PORTUGUÊS ===");
            sb.AppendLine(string.Join(" ", glosses.ToArray()));
            sb.AppendLine();
            sb.AppendLine("=== ANÁLISE PALAVRA A PALAVRA ===");
            sb.Append(detailSb.ToString());
            return sb.ToString();
        }
    }

    public class TreppioTtsService
    {
        private SpeechSynthesizer _synth;
        private readonly object _ttsLock = new object();

        public TreppioTtsService()
        {
            try
            {
                _synth = new SpeechSynthesizer();
                _synth.SetOutputToDefaultAudioDevice();
                _synth.Rate = -1;
                foreach (InstalledVoice v in _synth.GetInstalledVoices())
                {
                    string name = v.VoiceInfo != null && v.VoiceInfo.Culture != null ? v.VoiceInfo.Culture.Name.ToLowerInvariant() : "";
                    if (name == "pt-br")
                    {
                        _synth.SelectVoice(v.VoiceInfo.Name);
                        break;
                    }
                }
            }
            catch
            {
                _synth = null;
            }
        }

        public void SpeakAsync(string treppioText)
        {
            if (string.IsNullOrEmpty(treppioText)) return;
            string phonetic = TreppioLexiconEngine.ToTtsPtBr(treppioText);
            ThreadPool.QueueUserWorkItem(_ =>
            {
                lock (_ttsLock)
                {
                    if (_synth == null) return;
                    try
                    {
                        _synth.SpeakAsyncCancelAll();
                        _synth.SpeakAsync(phonetic);
                    }
                    catch { }
                }
            });
        }
    }

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

        public TreppioLexiconEngine Lexicon { get; private set; }
        public event Action LexiconUpdated;

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
            Lexicon = new TreppioLexiconEngine();
            _appDataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "CondeTreppio");
            Directory.CreateDirectory(_appDataDir);
            _cachedDbPath = Path.Combine(_appDataDir, "dicionario_formas_expandidas.json");
            _cloudConfigPath = Path.Combine(_appDataDir, "cloud_url.txt");

            CloudUrl = File.Exists(_cloudConfigPath) ? File.ReadAllText(_cloudConfigPath, Encoding.UTF8).Trim() : "";
            ReloadPayloads();
        }

        public void ReloadPayloads()
        {
            _cachedHtmlBytes = File.Exists(_localCondeHtmlPath)
                ? File.ReadAllBytes(_localCondeHtmlPath)
                : ReadEmbeddedResource("index.html");

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
            StartBackgroundIndexBuild();
        }

        public void StartBackgroundIndexBuild()
        {
            byte[] snapshot = _cachedJsonBytes;
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try
                {
                    Lexicon.BuildFromJsonBytes(snapshot);
                    Action handler = LexiconUpdated;
                    if (handler != null) handler();
                }
                catch { }
            });
        }

        private void ParseMetadataMetrics()
        {
            TotalForms = 246737;
            NounsCount = 2109;
            VerbsCount = 1768;
            AdjsCount = 446;
            AdvsCount = 1202;

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

                if (TotalForms == 246737 && _cachedJsonBytes.Length > 4096)
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
                    wc.Headers.Add("User-Agent", "CondeTreppioLauncher/8.4");
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
                    StartBackgroundIndexBuild();
                    ActiveSource = "Nuvem Sincronizada (Git/Google Drive)";
                    message = "Banco atualizado da nuvem (" + TotalForms.ToString("N0", new CultureInfo("pt-BR")) + " formas)!";
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

        private static string ResolveDownloadArtifact(string relativeName)
        {
            string[] bases = new string[] { @"D:\Conde_Treppio", @"D:\Conde_Treppio\dist", AppDomain.CurrentDomain.BaseDirectory };
            for (int i = 0; i < bases.Length; i++)
            {
                string cand = Path.Combine(bases[i], relativeName);
                if (File.Exists(cand)) return cand;
            }
            return null;
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
                    string cleanPath = firstLine[1].Split('?')[0];

                    if (cleanPath == "/api/db" || cleanPath.EndsWith("/dicionario_formas_expandidas.json"))
                    {
                        SendResponse(stream, "200 OK", "application/json; charset=utf-8", _cachedJsonBytes);
                    }
                    else if (cleanPath == "/api/recompilar" && method == "POST")
                    {
                        string msg;
                        RecompileLocalConde(out msg);
                        string body = "{\"status\":\"ok\",\"source\":\"" + EscapeJson(ActiveSource) + "\",\"db\":" + Encoding.UTF8.GetString(_cachedJsonBytes) + "}";
                        SendResponse(stream, "200 OK", "application/json; charset=utf-8", Encoding.UTF8.GetBytes(body));
                    }
                    else if (cleanPath == "/api/cloud-config" && method == "POST")
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
                    else if (cleanPath == "/dados_dicionario_conde.js")
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
                    else if (cleanPath == "/Codice_Treppio_Conde.exe" || cleanPath == "/Codice_Treppio_Conde.apk" || cleanPath == "/dist/Codice_Treppio_Portatil.html")
                    {
                        string diskPath = ResolveDownloadArtifact(cleanPath.TrimStart('/').Replace('/', Path.DirectorySeparatorChar));
                        if (diskPath != null)
                        {
                            string mime = cleanPath.EndsWith(".html") ? "text/html; charset=utf-8" : "application/octet-stream";
                            SendResponse(stream, "200 OK", mime, File.ReadAllBytes(diskPath));
                        }
                        else
                        {
                            SendResponse(stream, "404 Not Found", "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Artifact not found"));
                        }
                    }
                    else if (cleanPath == "/" || cleanPath == "/index.html")
                    {
                        SendResponse(stream, "200 OK", "text/html; charset=utf-8", _cachedHtmlBytes);
                    }
                    else
                    {
                        SendResponse(stream, "404 Not Found", "text/plain; charset=utf-8", Encoding.UTF8.GetBytes("Not found"));
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
        [DllImport("dwmapi.dll")]
        private static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);

        private const int DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19;
        private const int DWMWA_USE_IMMERSIVE_DARK_MODE = 20;

        public static void EnableDarkMode(IntPtr handle)
        {
            try
            {
                int trueValue = 1;
                if (DwmSetWindowAttribute(handle, DWMWA_USE_IMMERSIVE_DARK_MODE, ref trueValue, sizeof(int)) != 0)
                {
                    DwmSetWindowAttribute(handle, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1, ref trueValue, sizeof(int));
                }
            }
            catch { }
        }

        protected override void OnHandleCreated(EventArgs e)
        {
            base.OnHandleCreated(e);
            EnableDarkMode(Handle);
        }

        private readonly EmbeddedServer _server;
        private readonly TreppioTtsService _tts;
        private readonly CultureInfo _ptBr = new CultureInfo("pt-BR");

        private TabControl _tabs;
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

        private TextBox _txtIpaInput;
        private TextBox _txtIpaOutput;

        private RadioButton _rbPtToTr;
        private RadioButton _rbTrToPt;
        private TextBox _txtTransInput;
        private TextBox _txtTransOutput;
        private Label _lblTransIndexStatus;
        private string _lastPrimaryTreppio = "falde et Vé";

        public LauncherForm(EmbeddedServer server)
        {
            _server = server;
            _tts = new TreppioTtsService();

            AutoScaleMode = AutoScaleMode.Dpi;
            Text = "Códice Lexicográfico Imperial — Língua Tréppia (Era Clássica V8.4 | /conde)";
            ClientSize = new Size(880, 620);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(9, 9, 11);
            ForeColor = Color.FromArgb(244, 244, 245);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;

            Font titleFont = new Font("Segoe UI", 13.5f, FontStyle.Bold);
            Font subFont = new Font("Segoe UI", 9f, FontStyle.Regular);
            Font boldFont = new Font("Segoe UI", 9.5f, FontStyle.Bold);
            Font monoFont = new Font("Consolas", 9.5f, FontStyle.Regular);

            Panel goldTopBar = new Panel { Dock = DockStyle.Top, Height = 2, BackColor = Color.FromArgb(212, 175, 55) };
            Panel headerPanel = new Panel { Dock = DockStyle.Top, Height = 78, BackColor = Color.FromArgb(17, 17, 21) };

            Label lblCrest = new Label
            {
                Text = "𝓣",
                Font = new Font("Segoe UI", 18f, FontStyle.Bold),
                ForeColor = Color.White,
                BackColor = Color.FromArgb(26, 26, 32),
                TextAlign = ContentAlignment.MiddleCenter,
                Size = new Size(48, 48),
                Location = new Point(22, 15)
            };
            Label lblTitle = new Label
            {
                Text = "CÓDICE LEXICOGRÁFICO IMPERIAL DO TRÉPPIO (V8.4)",
                Font = titleFont,
                ForeColor = Color.White,
                AutoSize = true,
                Location = new Point(82, 14)
            };
            _lblSubtitle = new Label
            {
                Text = FormatSubtitleText(),
                Font = subFont,
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = true,
                Location = new Point(84, 42)
            };
            headerPanel.Controls.Add(lblCrest);
            headerPanel.Controls.Add(lblTitle);
            headerPanel.Controls.Add(_lblSubtitle);

            _tabs = new TabControl
            {
                Dock = DockStyle.Fill,
                DrawMode = TabDrawMode.OwnerDrawFixed,
                SizeMode = TabSizeMode.Fixed,
                ItemSize = new Size(220, 36),
                Font = boldFont
            };
            _tabs.DrawItem += OnDrawTabItem;

            TabPage tabPanel = BuildMainPanelTab(subFont, boldFont, monoFont);
            TabPage tabIpa = BuildPhoneticsTab(subFont, boldFont, monoFont);
            TabPage tabTranslator = BuildTranslatorTab(subFont, boldFont, monoFont);

            _tabs.TabPages.Add(tabPanel);
            _tabs.TabPages.Add(tabIpa);
            _tabs.TabPages.Add(tabTranslator);

            Controls.Add(_tabs);
            Controls.Add(headerPanel);
            Controls.Add(goldTopBar);

            _server.LexiconUpdated += () =>
            {
                try
                {
                    if (IsHandleCreated && !IsDisposed)
                    {
                        BeginInvoke((Action)RefreshIndexStatusUi);
                    }
                }
                catch { }
            };
            RefreshIndexStatusUi();
            RunIpaAnalysis();
            Shown += (s, e) => LaunchDedicatedWindow();
        }

        private TabPage BuildMainPanelTab(Font subFont, Font boldFont, Font monoFont)
        {
            TabPage page = new TabPage("  I. Painel & Códice  ")
            {
                BackColor = Color.FromArgb(9, 9, 11),
                ForeColor = Color.FromArgb(244, 244, 245),
                Padding = new Padding(16)
            };

            int cardY = 16;
            int cardW = 198;
            int cardGap = 12;
            page.Controls.Add(CreateTelemetryCard("FORMAS VALIDADAS", _server.TotalForms.ToString("N0", _ptBr), "26 Leis Sândi + Haplologia", new Point(22, cardY), cardW, out _valForms));
            page.Controls.Add(CreateTelemetryCard("SUBSTANTIVOS", _server.NounsCount.ToString("N0", _ptBr), "8 Casos + 10 Sufixos", new Point(22 + (cardW + cardGap) * 1, cardY), cardW, out _valNouns));
            page.Controls.Add(CreateTelemetryCard("VERBOS (4 EIXOS)", _server.VerbsCount.ToString("N0", _ptBr), "114 Formas por Verbo", new Point(22 + (cardW + cardGap) * 2, cardY), cardW, out _valVerbs));
            page.Controls.Add(CreateTelemetryCard("ADJS & ADVÉRBIOS", _server.AdjsCount + " / " + _server.AdvsCount, "Superl. -n & Modal -vë", new Point(22 + (cardW + cardGap) * 3, cardY), cardW, out _valAdjs));

            _lblStatus = new Label
            {
                Text = "● Fonte Ativa: " + _server.ActiveSource,
                Font = boldFont,
                ForeColor = Color.FromArgb(52, 211, 153),
                AutoSize = true,
                Location = new Point(22, 112)
            };
            page.Controls.Add(_lblStatus);

            _lblUrl = new Label
            {
                Text = "Servidor Local Embarcado: http://127.0.0.1:" + _server.Port + "  |  V8.4 (G=/ɡ/, S=/s/)",
                Font = monoFont,
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = true,
                Location = new Point(22, 136)
            };
            page.Controls.Add(_lblUrl);

            Button btnOpenApp = CreateStyledButton(
                "📖 ABRIR CÓDICE TRÉPPIO COMPLETO (JANELA WEB DEDICADA)",
                new Point(22, 168),
                new Size(828, 48),
                Color.White,
                Color.FromArgb(9, 9, 11)
            );
            btnOpenApp.Font = new Font("Segoe UI", 11f, FontStyle.Bold);
            btnOpenApp.FlatAppearance.BorderSize = 0;
            btnOpenApp.Click += (s, e) => LaunchDedicatedWindow();
            page.Controls.Add(btnOpenApp);

            Button btnVoiceWhisper = CreateStyledButton(
                "🎙️ CONVERSAR POR VOZ COM O CONDE (WHISPER STT + VOZ NEURAL)",
                new Point(22, 226),
                new Size(828, 44),
                Color.FromArgb(18, 24, 22),
                Color.FromArgb(52, 211, 153)
            );
            btnVoiceWhisper.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            btnVoiceWhisper.FlatAppearance.BorderColor = Color.FromArgb(52, 211, 153);
            btnVoiceWhisper.Click += (s, e) => LaunchWhisperVoiceGui();
            page.Controls.Add(btnVoiceWhisper);

            Label lblCloud = new Label
            {
                Text = "URL do Banco Online (GitHub Raw ou Google Drive):",
                Font = subFont,
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = true,
                Location = new Point(22, 286)
            };
            page.Controls.Add(lblCloud);

            _txtCloudUrl = new TextBox
            {
                Location = new Point(22, 310),
                Size = new Size(828, 28),
                BackColor = Color.FromArgb(17, 17, 21),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = monoFont,
                Text = _server.CloudUrl
            };
            page.Controls.Add(_txtCloudUrl);

            _btnSyncCloud = CreateStyledButton(
                "☁️ Sincronizar da Nuvem (Git / Drive)",
                new Point(22, 348),
                new Size(406, 40),
                Color.FromArgb(24, 24, 28),
                Color.FromArgb(244, 244, 245)
            );
            _btnSyncCloud.Click += OnSyncCloudClick;
            page.Controls.Add(_btnSyncCloud);

            _btnRecompileLocal = CreateStyledButton(
                "🔨 Recompilar e Sincronizar Base /conde",
                new Point(444, 348),
                new Size(406, 40),
                Color.FromArgb(24, 24, 28),
                Color.FromArgb(244, 244, 245)
            );
            _btnRecompileLocal.Click += OnRecompileClick;
            page.Controls.Add(_btnRecompileLocal);

            _lblFeedback = new Label
            {
                Text = "Pronto. Haplologia Silábica V8.4, Aba de Pronúncia IPA e Tradutor Bilíngue TR <-> PT carregados.",
                Font = subFont,
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = false,
                Size = new Size(828, 46),
                Location = new Point(22, 404)
            };
            page.Controls.Add(_lblFeedback);

            return page;
        }

        private TabPage BuildPhoneticsTab(Font subFont, Font boldFont, Font monoFont)
        {
            TabPage page = new TabPage("  II. Pronúncia & IPA  ")
            {
                BackColor = Color.FromArgb(9, 9, 11),
                ForeColor = Color.FromArgb(244, 244, 245),
                Padding = new Padding(16)
            };

            Label lblBanner = new Label
            {
                Text = "REGRAS INVIOLÁVEIS:  G / g = SEMPRE /ɡ/ (guitarra, nunca /ʒ/)  |  S / s = SEMPRE /s/ (sapato, nunca /z/)  |  ' = Haplologia [ʔ] (S_i[0] == S_{i+1}[0])",
                Font = boldFont,
                ForeColor = Color.FromArgb(253, 226, 142),
                BackColor = Color.FromArgb(18, 18, 22),
                BorderStyle = BorderStyle.FixedSingle,
                TextAlign = ContentAlignment.MiddleLeft,
                Padding = new Padding(10, 0, 10, 0),
                Size = new Size(828, 36),
                Location = new Point(22, 16)
            };
            page.Controls.Add(lblBanner);

            _txtIpaInput = new TextBox
            {
                Location = new Point(22, 64),
                Size = new Size(570, 28),
                BackColor = Color.FromArgb(17, 17, 21),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = monoFont,
                Text = "Haly'itror giza in oxej: falde, Vé, rase, ve'ar et Tepy'atte"
            };
            _txtIpaInput.TextChanged += (s, e) => RunIpaAnalysis();
            page.Controls.Add(_txtIpaInput);

            Button btnSpeak = CreateStyledButton(
                "🔊 Analisar & Ouvir (pt-BR / SAPI)",
                new Point(602, 62),
                new Size(248, 32),
                Color.FromArgb(18, 24, 22),
                Color.FromArgb(52, 211, 153)
            );
            btnSpeak.FlatAppearance.BorderColor = Color.FromArgb(52, 211, 153);
            btnSpeak.Click += (s, e) =>
            {
                RunIpaAnalysis();
                _tts.SpeakAsync(TreppioLexiconEngine.ApplyHaplology(_txtIpaInput.Text));
            };
            page.Controls.Add(btnSpeak);

            string[] samples = new string[] { "Haly'itror", "giza", "esur", "rase", "vevar", "avurvé", "Tepy'atte", "doote'i" };
            int chipX = 22;
            for (int i = 0; i < samples.Length; i++)
            {
                string tok = samples[i];
                Button b = CreateStyledButton(tok, new Point(chipX, 104), new Size(94, 28), Color.FromArgb(24, 24, 28), Color.White);
                b.Font = monoFont;
                b.Click += (s, e) =>
                {
                    _txtIpaInput.Text = tok;
                    RunIpaAnalysis();
                    _tts.SpeakAsync(TreppioLexiconEngine.ApplyHaplology(tok));
                };
                page.Controls.Add(b);
                chipX += 102;
            }

            _txtIpaOutput = new TextBox
            {
                Location = new Point(22, 144),
                Size = new Size(828, 324),
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                BackColor = Color.FromArgb(14, 14, 18),
                ForeColor = Color.FromArgb(228, 228, 231),
                BorderStyle = BorderStyle.FixedSingle,
                Font = monoFont
            };
            page.Controls.Add(_txtIpaOutput);

            return page;
        }

        private TabPage BuildTranslatorTab(Font subFont, Font boldFont, Font monoFont)
        {
            TabPage page = new TabPage("  III. Tradutor TR <-> PT  ")
            {
                BackColor = Color.FromArgb(9, 9, 11),
                ForeColor = Color.FromArgb(244, 244, 245),
                Padding = new Padding(16)
            };

            _rbPtToTr = new RadioButton
            {
                Text = "Português -> Tréppio",
                Checked = true,
                AutoSize = true,
                Font = boldFont,
                ForeColor = Color.FromArgb(253, 226, 142),
                Location = new Point(22, 18)
            };
            _rbTrToPt = new RadioButton
            {
                Text = "Tréppio -> Português",
                AutoSize = true,
                Font = boldFont,
                ForeColor = Color.FromArgb(244, 244, 245),
                Location = new Point(215, 18)
            };
            _rbPtToTr.CheckedChanged += (s, e) => { if (_rbPtToTr.Checked) RunTranslation(); };
            _rbTrToPt.CheckedChanged += (s, e) => { if (_rbTrToPt.Checked) RunTranslation(); };
            page.Controls.Add(_rbPtToTr);
            page.Controls.Add(_rbTrToPt);

            _lblTransIndexStatus = new Label
            {
                Text = "Carregando índice lexical...",
                Font = subFont,
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = true,
                Location = new Point(420, 20)
            };
            page.Controls.Add(_lblTransIndexStatus);

            _txtTransInput = new TextBox
            {
                Location = new Point(22, 50),
                Size = new Size(540, 28),
                BackColor = Color.FromArgb(17, 17, 21),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = new Font("Segoe UI", 10.5f, FontStyle.Regular),
                Text = "pão e água na casa"
            };
            _txtTransInput.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) { e.SuppressKeyPress = true; RunTranslation(); } };
            page.Controls.Add(_txtTransInput);

            Button btnTranslate = CreateStyledButton(
                "🔄 Traduzir",
                new Point(572, 48),
                new Size(134, 32),
                Color.White,
                Color.FromArgb(9, 9, 11)
            );
            btnTranslate.FlatAppearance.BorderSize = 0;
            btnTranslate.Click += (s, e) => RunTranslation();
            page.Controls.Add(btnTranslate);

            Button btnSpeakRes = CreateStyledButton(
                "🔊 Ouvir TR",
                new Point(716, 48),
                new Size(134, 32),
                Color.FromArgb(18, 24, 22),
                Color.FromArgb(52, 211, 153)
            );
            btnSpeakRes.FlatAppearance.BorderColor = Color.FromArgb(52, 211, 153);
            btnSpeakRes.Click += (s, e) =>
            {
                string target = _rbTrToPt.Checked ? _txtTransInput.Text : _lastPrimaryTreppio;
                _tts.SpeakAsync(target);
            };
            page.Controls.Add(btnSpeakRes);

            _txtTransOutput = new TextBox
            {
                Location = new Point(22, 92),
                Size = new Size(828, 376),
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                BackColor = Color.FromArgb(14, 14, 18),
                ForeColor = Color.FromArgb(228, 228, 231),
                BorderStyle = BorderStyle.FixedSingle,
                Font = monoFont
            };
            page.Controls.Add(_txtTransOutput);

            return page;
        }

        private void OnDrawTabItem(object sender, DrawItemEventArgs e)
        {
            TabPage page = _tabs.TabPages[e.Index];
            bool selected = (_tabs.SelectedIndex == e.Index);
            using (SolidBrush bg = new SolidBrush(selected ? Color.FromArgb(28, 28, 36) : Color.FromArgb(14, 14, 18)))
            {
                e.Graphics.FillRectangle(bg, e.Bounds);
            }
            if (selected)
            {
                using (Pen goldPen = new Pen(Color.FromArgb(212, 175, 55), 2))
                {
                    e.Graphics.DrawLine(goldPen, e.Bounds.Left, e.Bounds.Bottom - 1, e.Bounds.Right, e.Bounds.Bottom - 1);
                }
            }
            TextRenderer.DrawText(
                e.Graphics,
                page.Text,
                _tabs.Font,
                e.Bounds,
                selected ? Color.FromArgb(253, 226, 142) : Color.FromArgb(161, 161, 170),
                TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter
            );
        }

        private void RefreshIndexStatusUi()
        {
            if (_server.Lexicon.IsReady)
            {
                _lblTransIndexStatus.ForeColor = Color.FromArgb(52, 211, 153);
                _lblTransIndexStatus.Text = string.Format(
                    _ptBr,
                    "Índice Pronto: {0:N0} lemas / {1:N0} formas (7 classes)",
                    _server.Lexicon.IndexedLemmasCount,
                    _server.Lexicon.IndexedFormsCount
                );
                RunTranslation();
            }
            else
            {
                _lblTransIndexStatus.ForeColor = Color.FromArgb(253, 226, 142);
                _lblTransIndexStatus.Text = "Indexando base JSON em background...";
            }
        }

        private void RunIpaAnalysis()
        {
            string input = (_txtIpaInput.Text ?? "").Trim();
            StringBuilder sb = new StringBuilder();
            if (string.IsNullOrEmpty(input))
            {
                _txtIpaOutput.Text = "Digite uma palavra ou frase em Tréppio.";
                return;
            }
            string[] words = Regex.Split(input, @"\s+");
            List<string> normalizedWords = new List<string>();
            List<string> fullIpa = new List<string>();
            StringBuilder cardSb = new StringBuilder();
            for (int i = 0; i < words.Length; i++)
            {
                string rawClean = Regex.Replace(words[i], @"[.,;:!?()\[\]""“”]", "");
                if (string.IsNullOrEmpty(rawClean)) continue;
                IpaWordInfo info = TreppioLexiconEngine.AnalyzeWordIpa(rawClean);
                if (info == null) continue;
                normalizedWords.Add(info.Word);
                fullIpa.Add(info.Ipa.Trim('/'));
                string diffNote = rawClean != info.Word ? "  (pré-haplologia: " + rawClean + ")" : "";
                cardSb.AppendFormat("• {0}{1}\r\n    IPA: {2}  |  Sílabas: {3}\r\n", info.Word, diffNote, info.Ipa, info.SyllablesJoined);
                if (!string.IsNullOrEmpty(info.Notes))
                {
                    cardSb.AppendFormat("    Notas: {0}\r\n", info.Notes);
                }
            }
            sb.AppendLine("Transcrição IPA Contínua: [" + string.Join(" ", fullIpa.ToArray()) + "]");
            sb.AppendLine("Forma Canônica V8.4:      " + string.Join(" ", normalizedWords.ToArray()));
            sb.AppendLine("Normalização TTS (pt-BR): " + TreppioLexiconEngine.ToTtsPtBr(string.Join(" ", normalizedWords.ToArray())));
            sb.AppendLine();
            sb.Append(cardSb.ToString());
            sb.AppendLine();
            sb.AppendLine("=== ALFABETO FONÉTICO RESUMIDO (IPA) ===");
            sb.AppendLine("G / g -> /ɡ/ (sempre guitarra, nunca /ʒ/)   |  S / s -> /s/ (sempre sapato, nunca /z/)");
            sb.AppendLine("'     -> [ʔ] (corte silábico de haplologia)  |  X / x -> /x/ (fricativa velar)");
            sb.AppendLine("R / r -> /ɾ/ vs rr -> /r/                    |  Ë / ë -> /ə/ (diérese modal)");
            sb.AppendLine("Y / y -> /i/                                 |  J / j -> /j/ (dativo -ej/-aj/-ij)");
            _txtIpaOutput.Text = sb.ToString();
        }

        private void RunTranslation()
        {
            if (_txtTransOutput == null) return;
            if (_rbPtToTr.Checked)
            {
                string primary;
                _txtTransOutput.Text = _server.Lexicon.TranslatePtToTrReport(_txtTransInput.Text, out primary);
                _lastPrimaryTreppio = primary;
            }
            else
            {
                _txtTransOutput.Text = _server.Lexicon.TranslateTrToPtReport(_txtTransInput.Text);
            }
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
            RefreshIndexStatusUi();
        }

        private Panel CreateTelemetryCard(string title, string value, string sub, Point loc, int width, out Label valueLabel)
        {
            Panel card = new Panel
            {
                Location = loc,
                Size = new Size(width, 82),
                BackColor = Color.FromArgb(18, 18, 22),
                BorderStyle = BorderStyle.FixedSingle
            };
            Panel leftAccent = new Panel { Dock = DockStyle.Left, Width = 3, BackColor = Color.FromArgb(212, 175, 55) };
            Label lblCardTitle = new Label
            {
                Text = title,
                Font = new Font("Segoe UI", 7.2f, FontStyle.Bold),
                ForeColor = Color.FromArgb(113, 113, 122),
                AutoSize = true,
                Location = new Point(10, 8)
            };
            valueLabel = new Label
            {
                Text = value,
                Font = new Font("Segoe UI", 14.5f, FontStyle.Bold),
                ForeColor = Color.White,
                AutoSize = true,
                Location = new Point(10, 26)
            };
            Label lblSub = new Label
            {
                Text = sub,
                Font = new Font("Segoe UI", 7.2f, FontStyle.Regular),
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = true,
                Location = new Point(10, 56)
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
            b.FlatAppearance.BorderColor = Color.FromArgb(63, 63, 70);
            b.FlatAppearance.BorderSize = 1;
            return b;
        }

        private void OnSyncCloudClick(object sender, EventArgs e)
        {
            string url = _txtCloudUrl.Text;
            _btnSyncCloud.Enabled = false;
            _lblFeedback.ForeColor = Color.FromArgb(253, 226, 142);
            _lblFeedback.Text = "⏳ Conectando à nuvem em background...";

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
            _lblFeedback.Text = "⏳ Recompilando base morfológica do /conde...";

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
                try { Process.Start("python", "\"" + scriptPath + "\""); }
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
                    for (int waitMs = 0; waitMs < 15000 && !server.Lexicon.IsReady; waitMs += 50)
                    {
                        Thread.Sleep(50);
                    }
                    bool hapOk = TreppioLexiconEngine.ApplyHaplology("vevar") == "ve'ar"
                              && TreppioLexiconEngine.ApplyHaplology("Treppenína") == "Treppení'a"
                              && TreppioLexiconEngine.ApplyHaplology("katkom") == "kat'om"
                              && TreppioLexiconEngine.ApplyHaplology("barur") == "barur"
                              && TreppioLexiconEngine.ToTtsPtBr("giza esu") == "guiza essu";
                    string prim;
                    string ptOut = server.Lexicon.TranslatePtToTrReport("pão", out prim);
                    string trOut = server.Lexicon.TranslateTrToPtReport("in faldem");
                    bool transOk = server.Lexicon.IsReady && prim.Trim().Equals("falde", StringComparison.OrdinalIgnoreCase) && ptOut.IndexOf("falde", StringComparison.OrdinalIgnoreCase) >= 0 && trOut.IndexOf("Preposição", StringComparison.OrdinalIgnoreCase) >= 0;

                    using (WebClient wc = new WebClient())
                    {
                        wc.Encoding = Encoding.UTF8;
                        string dbJson = wc.DownloadString("http://127.0.0.1:" + server.Port + "/api/db");
                        bool validDb = dbJson.Contains("\"substantivos\"") && dbJson.Contains("\"verbos_quadripartite\"");
                        bool notFoundOk = false;
                        try
                        {
                            wc.DownloadString("http://127.0.0.1:" + server.Port + "/nao_existe_404.png");
                        }
                        catch (WebException wex)
                        {
                            HttpWebResponse resp = wex.Response as HttpWebResponse;
                            if (resp != null && (int)resp.StatusCode == 404) notFoundOk = true;
                        }

                        bool allOk = validDb && hapOk && transOk && notFoundOk;
                        string msg = string.Format(
                            "TEST_HEADLESS_OK={0} DB={1} HAPLO_TTS={2} TRANS={3} HTTP404={4} PORT={5} BYTES={6} FORMS={7} LEMMAS={8} SOURCE={9}",
                            allOk, validDb, hapOk, transOk, notFoundOk, server.Port, dbJson.Length, server.TotalForms, server.Lexicon.IndexedLemmasCount, server.ActiveSource
                        );
                        Console.WriteLine(msg);
                        try
                        {
                            string logPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "headless_test_result.txt");
                            File.WriteAllText(logPath, msg, Encoding.UTF8);
                        }
                        catch { }
                        server.Stop();
                        return allOk ? 0 : 1;
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
