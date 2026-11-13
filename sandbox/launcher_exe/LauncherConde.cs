using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Speech.Synthesis;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

[assembly: AssemblyTitle("Codice Lexicografico Imperial da Lingua Treppia (V8.5)")]
[assembly: AssemblyDescription("Launcher Executavel, Servidor HTTP/1.1 Async Keep-Alive, Brasao do Conde, Pronuncia IPA e Tradutor TR-PT (/conde)")]
[assembly: AssemblyCompany("Chancelaria Imperial de Treppenia")]
[assembly: AssemblyProduct("Codice Treppio Conde V8.5")]
[assembly: AssemblyVersion("8.5.0.0")]

namespace CondeTreppioLauncher
{
    public class LexEntry
    {
        public string Treppio { get; set; }
        public string PtMeaning { get; set; }
        public string PtNorm { get; set; }
        public string PtHead { get; set; }
        public string[] HeadWords { get; set; }
        public string[] Words { get; set; }
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

        private sealed class LexiconSnapshot
        {
            public List<LexEntry> PtEntries = new List<LexEntry>();
            public Dictionary<string, List<int>> PtTokenMap = new Dictionary<string, List<int>>(StringComparer.Ordinal);
            public Dictionary<string, List<int>> PtStemMap = new Dictionary<string, List<int>>(StringComparer.Ordinal);
            public Dictionary<string, List<LexEntry>> TrReverse = new Dictionary<string, List<LexEntry>>(StringComparer.OrdinalIgnoreCase);
            public Dictionary<string, string> CorpusByTreppio = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            public int IndexedFormsCount;
            public int IndexedLemmasCount;
            public int Generation;
            public bool IsReady;
        }

        private volatile LexiconSnapshot _snap = new LexiconSnapshot();
        private int _generationSeq;

        public bool IsReady { get { return _snap.IsReady; } }
        public int IndexedFormsCount { get { return _snap.IndexedFormsCount; } }
        public int IndexedLemmasCount { get { return _snap.IndexedLemmasCount; } }
        public int Generation { get { return _snap.Generation; } }

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

        public static List<IpaWordInfo> AnalyzeSentenceIpa(string sentence)
        {
            List<IpaWordInfo> list = new List<IpaWordInfo>();
            if (string.IsNullOrWhiteSpace(sentence)) return list;
            string[] tokens = Regex.Split(sentence.Trim(), @"\s+");
            for (int i = 0; i < tokens.Length; i++)
            {
                IpaWordInfo info = AnalyzeWordIpa(tokens[i]);
                if (info != null) list.Add(info);
            }
            return list;
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

        private static string[] SplitAlphaNum(string norm)
        {
            if (string.IsNullOrEmpty(norm)) return new string[0];
            List<string> list = new List<string>(8);
            int start = -1;
            for (int i = 0; i < norm.Length; i++)
            {
                char ch = norm[i];
                bool isAlnum = (ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9');
                if (isAlnum)
                {
                    if (start < 0) start = i;
                }
                else if (start >= 0)
                {
                    list.Add(norm.Substring(start, i - start));
                    start = -1;
                }
            }
            if (start >= 0) list.Add(norm.Substring(start));
            return list.ToArray();
        }

        private static string ComputePtStem(string q)
        {
            if (string.IsNullOrEmpty(q) || q.Length <= 4) return q ?? "";
            string[] suffixes = new string[] { "mente", "coes", "cao", "ado", "ada", "es", "os", "as", "ar", "er", "ir", "s" };
            for (int i = 0; i < suffixes.Length; i++)
            {
                string suf = suffixes[i];
                if (q.Length > suf.Length + 2 && q.EndsWith(suf, StringComparison.Ordinal))
                {
                    return q.Substring(0, q.Length - suf.Length);
                }
            }
            return q;
        }

        private static void IndexBucket(Dictionary<string, List<int>> map, string key, int entryIdx)
        {
            if (string.IsNullOrEmpty(key)) return;
            List<int> bucket;
            if (!map.TryGetValue(key, out bucket))
            {
                bucket = new List<int>(4);
                map[key] = bucket;
            }
            if (bucket.Count == 0 || bucket[bucket.Count - 1] != entryIdx)
            {
                bucket.Add(entryIdx);
            }
        }

        private static void AddPtEntry(LexiconSnapshot snap, string treppio, string ptMeaning, string classTag, string detail, int boost)
        {
            if (string.IsNullOrEmpty(treppio) || string.IsNullOrEmpty(ptMeaning)) return;
            string norm = StripAccents(ptMeaning).Trim();
            int sepIdx = norm.IndexOfAny(new char[] { ',', ';', '(' });
            string head = (sepIdx >= 0 ? norm.Substring(0, sepIdx) : norm).Trim();
            string[] headWords = SplitAlphaNum(head);
            string[] words = SplitAlphaNum(norm);

            int idx = snap.PtEntries.Count;
            snap.PtEntries.Add(new LexEntry
            {
                Treppio = treppio,
                PtMeaning = ptMeaning,
                PtNorm = norm,
                PtHead = head,
                HeadWords = headWords,
                Words = words,
                ClassTag = classTag,
                Detail = detail ?? "",
                Boost = boost
            });

            IndexBucket(snap.PtTokenMap, norm, idx);
            if (!string.IsNullOrEmpty(head)) IndexBucket(snap.PtTokenMap, head, idx);
            for (int i = 0; i < words.Length; i++)
            {
                string w = words[i];
                IndexBucket(snap.PtTokenMap, w, idx);
                if (w.Length >= 3)
                {
                    IndexBucket(snap.PtStemMap, w.Substring(0, 3), idx);
                }
            }
        }

        private static void AddTrForm(Dictionary<string, List<LexEntry>> rev, ref int count, string formStr, LexEntry template)
        {
            if (string.IsNullOrEmpty(formStr)) return;
            string clean = formStr.Replace("!", "").Replace("?", "").Trim().ToLowerInvariant();
            if (string.IsNullOrEmpty(clean)) return;
            List<LexEntry> list;
            if (!rev.TryGetValue(clean, out list))
            {
                list = new List<LexEntry>(2);
                rev[clean] = list;
            }
            if (list.Count < 8)
            {
                list.Add(template);
                count++;
            }
        }

        private sealed class FastJsonCursor
        {
            private readonly string _s;
            private readonly int _len;
            public int Pos;

            public FastJsonCursor(string json)
            {
                _s = json ?? "";
                _len = _s.Length;
                Pos = 0;
            }

            public void SkipWs()
            {
                while (Pos < _len)
                {
                    char c = _s[Pos];
                    if (c == ' ' || c == '\t' || c == '\r' || c == '\n') Pos++;
                    else break;
                }
            }

            public char Peek()
            {
                SkipWs();
                return Pos < _len ? _s[Pos] : '\0';
            }

            public bool TryConsume(char expected)
            {
                SkipWs();
                if (Pos < _len && _s[Pos] == expected)
                {
                    Pos++;
                    return true;
                }
                return false;
            }

            public string ReadString()
            {
                SkipWs();
                if (Pos >= _len || _s[Pos] != '"') return null;
                Pos++;
                int start = Pos;
                bool hasEscape = false;
                while (Pos < _len)
                {
                    char c = _s[Pos];
                    if (c == '"')
                    {
                        string res = hasEscape ? Unescape(_s, start, Pos) : _s.Substring(start, Pos - start);
                        Pos++;
                        return res;
                    }
                    if (c == '\\')
                    {
                        hasEscape = true;
                        Pos += 2;
                    }
                    else
                    {
                        Pos++;
                    }
                }
                return _s.Substring(start);
            }

            private static string Unescape(string s, int start, int end)
            {
                StringBuilder sb = new StringBuilder(end - start);
                for (int i = start; i < end; i++)
                {
                    char c = s[i];
                    if (c == '\\' && i + 1 < end)
                    {
                        char n = s[++i];
                        if (n == '"' || n == '\\' || n == '/') sb.Append(n);
                        else if (n == 'n') sb.Append('\n');
                        else if (n == 'r') sb.Append('\r');
                        else if (n == 't') sb.Append('\t');
                        else if (n == 'b') sb.Append('\b');
                        else if (n == 'f') sb.Append('\f');
                        else if (n == 'u' && i + 4 < end)
                        {
                            int code;
                            if (int.TryParse(s.Substring(i + 1, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out code))
                            {
                                sb.Append((char)code);
                            }
                            i += 4;
                        }
                        else sb.Append(n);
                    }
                    else
                    {
                        sb.Append(c);
                    }
                }
                return sb.ToString();
            }

            public string ReadScalarAsString()
            {
                SkipWs();
                if (Pos >= _len) return "";
                char c = _s[Pos];
                if (c == '"') return ReadString() ?? "";
                if (c == '{' || c == '[')
                {
                    SkipValue();
                    return "";
                }
                int start = Pos;
                while (Pos < _len)
                {
                    char ch = _s[Pos];
                    if (ch == ',' || ch == '}' || ch == ']' || ch == ' ' || ch == '\r' || ch == '\n' || ch == '\t') break;
                    Pos++;
                }
                string raw = _s.Substring(start, Pos - start);
                return raw == "null" ? "" : raw;
            }

            private void SkipStringFast()
            {
                Pos++;
                while (Pos < _len)
                {
                    char c = _s[Pos++];
                    if (c == '"') return;
                    if (c == '\\' && Pos < _len) Pos++;
                }
            }

            public void SkipValue()
            {
                SkipWs();
                if (Pos >= _len) return;
                char c = _s[Pos];
                if (c == '"')
                {
                    SkipStringFast();
                    return;
                }
                if (c == '{' || c == '[')
                {
                    int depth = 0;
                    while (Pos < _len)
                    {
                        char ch = _s[Pos];
                        if (ch == '"')
                        {
                            SkipStringFast();
                            continue;
                        }
                        if (ch == '{' || ch == '[') depth++;
                        else if (ch == '}' || ch == ']')
                        {
                            depth--;
                            if (depth <= 0)
                            {
                                Pos++;
                                return;
                            }
                        }
                        Pos++;
                    }
                    return;
                }
                while (Pos < _len)
                {
                    char ch = _s[Pos];
                    if (ch == ',' || ch == '}' || ch == ']') break;
                    Pos++;
                }
            }

            public void ForEachObjectPair(Action<string> onKey)
            {
                if (!TryConsume('{'))
                {
                    SkipValue();
                    return;
                }
                if (TryConsume('}')) return;
                while (Pos < _len)
                {
                    string key = ReadString();
                    if (key == null) break;
                    TryConsume(':');
                    onKey(key);
                    if (TryConsume(',')) continue;
                    TryConsume('}');
                    break;
                }
            }

            public void ForEachArrayItem(Action<int> onIndex)
            {
                if (!TryConsume('['))
                {
                    SkipValue();
                    return;
                }
                if (TryConsume(']')) return;
                int idx = 0;
                while (Pos < _len)
                {
                    onIndex(idx++);
                    if (TryConsume(',')) continue;
                    TryConsume(']');
                    break;
                }
            }
        }

        private static string StripParenTrim(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            if (s.IndexOf('(') < 0) return s.Trim();
            StringBuilder sb = new StringBuilder(s.Length);
            int depth = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '(') depth++;
                else if (c == ')' && depth > 0) depth--;
                else if (depth == 0) sb.Append(c);
            }
            return sb.ToString().Trim();
        }

        public void BuildFromJsonBytes(byte[] jsonBytes)
        {
            if (jsonBytes == null || jsonBytes.Length == 0) return;
            string json = Encoding.UTF8.GetString(jsonBytes);
            FastJsonCursor cur = new FastJsonCursor(json);
            if (cur.Peek() != '{') return;

            LexiconSnapshot snap = new LexiconSnapshot();
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
                AddPtEntry(snap, funcWords[i, 1], funcWords[i, 0], funcWords[i, 2], funcWords[i, 3], 45);
            }

            string[] persons = new string[] { "1ª Sg (-m)", "2ª Sg (-s)", "3ª Sg/Pl", "1ª Pl (-n)", "2ª Pl (-t)" };

            cur.ForEachObjectPair(topKey =>
            {
                if (topKey == "gnlt")
                {
                    // Pula capítulo textual GNLT sem alocar dicionários nem strings
                    cur.SkipValue();
                }
                else if (topKey == "substantivos")
                {
                    cur.ForEachObjectPair(lemma =>
                    {
                        string decl = "", sig = "", etym = "";
                        List<string> formasVal = new List<string>(20);
                        List<string> formasKey = new List<string>(20);
                        cur.ForEachObjectPair(fk =>
                        {
                            if (fk == "declinacao") decl = cur.ReadScalarAsString();
                            else if (fk == "significado") sig = cur.ReadScalarAsString();
                            else if (fk == "etimologia") etym = cur.ReadScalarAsString();
                            else if (fk == "formas")
                            {
                                cur.ForEachObjectPair(ck =>
                                {
                                    formasKey.Add(ck);
                                    formasVal.Add(cur.ReadScalarAsString());
                                });
                            }
                            else cur.SkipValue();
                        });
                        string cTag = "Substantivo (" + decl + "ª Decl.)";
                        AddPtEntry(snap, lemma, sig, cTag, etym, 10);
                        for (int i = 0; i < formasVal.Count; i++)
                        {
                            AddTrForm(snap.TrReverse, ref revCount, formasVal[i], new LexEntry { Treppio = lemma, PtMeaning = sig, ClassTag = cTag, Detail = formasKey[i] });
                        }
                    });
                }
                else if (topKey == "adjetivos")
                {
                    cur.ForEachObjectPair(adj =>
                    {
                        string sig = "", comp = "";
                        List<string> fKeys = new List<string>(16);
                        List<string> fVals = new List<string>(16);
                        cur.ForEachObjectPair(fk =>
                        {
                            string v = cur.ReadScalarAsString();
                            if (fk == "Significado") sig = v;
                            else
                            {
                                if (fk == "Comparativo") comp = v;
                                fKeys.Add(fk);
                                fVals.Add(v);
                            }
                        });
                        AddPtEntry(snap, adj, sig, "Adjetivo", "Comp: " + comp, 8);
                        for (int i = 0; i < fVals.Count; i++)
                        {
                            AddTrForm(snap.TrReverse, ref revCount, fVals[i], new LexEntry { Treppio = adj, PtMeaning = sig, ClassTag = "Adjetivo", Detail = fKeys[i] });
                        }
                    });
                }
                else if (topKey == "adverbios")
                {
                    cur.ForEachObjectPair(adv =>
                    {
                        string sig = "", subc = "", etym = "";
                        cur.ForEachObjectPair(fk =>
                        {
                            if (fk == "significado") sig = cur.ReadScalarAsString();
                            else if (fk == "subclasse") subc = cur.ReadScalarAsString();
                            else if (fk == "etimologia") etym = cur.ReadScalarAsString();
                            else cur.SkipValue();
                        });
                        AddPtEntry(snap, adv, sig, "Advérbio (" + subc + ")", etym, 6);
                        AddTrForm(snap.TrReverse, ref revCount, adv, new LexEntry { Treppio = adv, PtMeaning = sig, ClassTag = "Advérbio", Detail = subc });
                    });
                }
                else if (topKey == "pronomes")
                {
                    cur.ForEachObjectPair(pKey =>
                    {
                        string esfera = "", nomRaw = "";
                        bool hasEsfera = false;
                        List<string> cKeys = new List<string>(8);
                        List<string> cVals = new List<string>(8);
                        cur.ForEachObjectPair(fk =>
                        {
                            string v = cur.ReadScalarAsString();
                            if (fk == "esfera") { esfera = v; hasEsfera = true; }
                            else
                            {
                                if (fk == "Nom") nomRaw = v;
                                cKeys.Add(fk);
                                cVals.Add(v);
                            }
                        });
                        string desc = hasEsfera ? (pKey + ": " + esfera) : pKey;
                        string nomClean = StripParenTrim(nomRaw);
                        AddPtEntry(snap, string.IsNullOrEmpty(nomClean) ? pKey : nomClean, desc, "Pronome", "", 15);
                        for (int i = 0; i < cVals.Count; i++)
                        {
                            string[] parts = cVals[i].Split('/');
                            for (int p = 0; p < parts.Length; p++)
                            {
                                string tok = StripParenTrim(parts[p]);
                                AddTrForm(snap.TrReverse, ref revCount, tok, new LexEntry { Treppio = pKey, PtMeaning = desc, ClassTag = "Pronome", Detail = cKeys[i] });
                            }
                        }
                    });
                }
                else if (topKey == "numerais")
                {
                    cur.ForEachObjectPair(numK =>
                    {
                        string card = "", ordRaw = "", comp = "";
                        List<string> nKeys = new List<string>(8);
                        List<string> nVals = new List<string>(8);
                        cur.ForEachObjectPair(fk =>
                        {
                            string v = cur.ReadScalarAsString();
                            if (fk == "cardinal") card = v;
                            else if (fk == "ordinal") ordRaw = v;
                            else if (fk == "compostos") { comp = v; return; }
                            nKeys.Add(fk);
                            nVals.Add(v);
                        });
                        string ord = StripParenTrim(ordRaw);
                        string desc = "numeral " + numK + " (" + card + ", " + ord + ")";
                        AddPtEntry(snap, card + " / " + ord, desc, "Numeral", comp, 14);
                        for (int i = 0; i < nVals.Count; i++)
                        {
                            string[] parts = nVals[i].Split('/');
                            for (int p = 0; p < parts.Length; p++)
                            {
                                string tok = StripParenTrim(parts[p]);
                                AddTrForm(snap.TrReverse, ref revCount, tok, new LexEntry { Treppio = card, PtMeaning = desc, ClassTag = "Numeral", Detail = numK + " (" + nKeys[i] + ")" });
                            }
                        }
                    });
                }
                else if (topKey == "particulas_e_afixos")
                {
                    cur.ForEachObjectPair(pTok =>
                    {
                        string desc = "", cls = "";
                        cur.ForEachObjectPair(fk =>
                        {
                            if (fk == "descricao") desc = cur.ReadScalarAsString();
                            else if (fk == "classe") cls = cur.ReadScalarAsString();
                            else cur.SkipValue();
                        });
                        AddPtEntry(snap, pTok, desc, cls, "", 18);
                        string[] toks = pTok.Split('/');
                        for (int i = 0; i < toks.Length; i++)
                        {
                            string t = StripParenTrim(toks[i]);
                            if (!string.IsNullOrEmpty(t) && !t.StartsWith("-") && !t.EndsWith("-"))
                            {
                                AddTrForm(snap.TrReverse, ref revCount, t, new LexEntry { Treppio = pTok, PtMeaning = desc, ClassTag = cls, Detail = "Invariável" });
                            }
                        }
                    });
                }
                else if (topKey == "registro_diacronico_e_variantes")
                {
                    cur.ForEachObjectPair(dTok =>
                    {
                        string analise = "", est = "", eq = "";
                        cur.ForEachObjectPair(fk =>
                        {
                            if (fk == "analise") analise = cur.ReadScalarAsString();
                            else if (fk == "estatuto") est = cur.ReadScalarAsString();
                            else if (fk == "equivalente_canonico") eq = cur.ReadScalarAsString();
                            else cur.SkipValue();
                        });
                        AddPtEntry(snap, dTok + " -> " + eq, analise, est, eq, 2);
                        string[] toks = dTok.Split('/');
                        for (int i = 0; i < toks.Length; i++)
                        {
                            AddTrForm(snap.TrReverse, ref revCount, toks[i].Trim(), new LexEntry { Treppio = dTok, PtMeaning = analise, ClassTag = est, Detail = eq });
                        }
                    });
                }
                else if (topKey == "verbos_quadripartite")
                {
                    cur.ForEachObjectPair(vRoot =>
                    {
                        cur.ForEachObjectPair(axKey =>
                        {
                            string mean = "", inf = "", imp = "", interr = "";
                            string cat = "Verbo [" + axKey + "]";
                            List<KeyValuePair<string, string>> pendingForms = new List<KeyValuePair<string, string>>(120);
                            List<string> pendingDetails = new List<string>(120);
                            bool[] pendingUseInf = new bool[120];

                            cur.ForEachObjectPair(ak =>
                            {
                                if (ak == "meaning") mean = cur.ReadScalarAsString();
                                else if (ak == "conjugation")
                                {
                                    cur.ForEachObjectPair(ck =>
                                    {
                                        char nxt = cur.Peek();
                                        if (nxt == '[')
                                        {
                                            cur.ForEachArrayItem(pIdx =>
                                            {
                                                string wf = cur.ReadScalarAsString();
                                                if (!string.IsNullOrEmpty(wf))
                                                {
                                                    string pLbl = pIdx < persons.Length ? persons[pIdx] : "";
                                                    int kIdx = pendingForms.Count;
                                                    if (kIdx < pendingUseInf.Length) pendingUseInf[kIdx] = true;
                                                    pendingForms.Add(new KeyValuePair<string, string>(wf, ck + " " + pLbl));
                                                }
                                            });
                                        }
                                        else if (nxt == '{')
                                        {
                                            cur.ForEachObjectPair(sdk =>
                                            {
                                                string wf = cur.ReadScalarAsString();
                                                if (!string.IsNullOrEmpty(wf))
                                                {
                                                    pendingForms.Add(new KeyValuePair<string, string>(wf, ck + ": " + sdk));
                                                }
                                            });
                                        }
                                        else
                                        {
                                            string sv = cur.ReadScalarAsString();
                                            if (ck == "Infinitivo(-ur)") inf = sv;
                                            else if (ck == "Imperativo(Raiz)") imp = sv;
                                            else if (ck == "Interrogativo.2Pl(-ka)") interr = sv;
                                        }
                                    });
                                }
                                else cur.SkipValue();
                            });

                            AddPtEntry(snap, inf, mean, cat, "Raiz " + vRoot + "- | Imp: " + imp, axKey.StartsWith("1.") ? 12 : 4);
                            AddTrForm(snap.TrReverse, ref revCount, inf, new LexEntry { Treppio = vRoot + "-", PtMeaning = mean, ClassTag = cat, Detail = "Infinitivo" });
                            AddTrForm(snap.TrReverse, ref revCount, imp, new LexEntry { Treppio = vRoot + "-", PtMeaning = mean, ClassTag = cat, Detail = "Imperativo" });
                            AddTrForm(snap.TrReverse, ref revCount, interr, new LexEntry { Treppio = vRoot + "-", PtMeaning = mean, ClassTag = cat, Detail = "Interrogativo 2ª Pl" });

                            for (int f = 0; f < pendingForms.Count; f++)
                            {
                                string lemmaForm = (f < pendingUseInf.Length && pendingUseInf[f]) ? inf : (vRoot + "-");
                                AddTrForm(snap.TrReverse, ref revCount, pendingForms[f].Key, new LexEntry
                                {
                                    Treppio = lemmaForm,
                                    PtMeaning = mean,
                                    ClassTag = cat,
                                    Detail = pendingForms[f].Value
                                });
                            }
                        });
                    });
                }
                else if (topKey == "corpus_canonico")
                {
                    cur.ForEachArrayItem(_ =>
                    {
                        string tr = "", pt = "", tit = "";
                        cur.ForEachObjectPair(fk =>
                        {
                            if (fk == "treppio") tr = cur.ReadScalarAsString();
                            else if (fk == "portugues") pt = cur.ReadScalarAsString();
                            else if (fk == "titulo") tit = cur.ReadScalarAsString();
                            else cur.SkipValue();
                        });
                        if (!string.IsNullOrEmpty(tr) && !string.IsNullOrEmpty(pt))
                        {
                            snap.CorpusByTreppio[tr] = tit + ": " + pt;
                            AddPtEntry(snap, tr, pt, "Corpus Canônico", tit, 5);
                        }
                    });
                }
                else
                {
                    cur.SkipValue();
                }
            });

            snap.IndexedFormsCount = revCount;
            snap.IndexedLemmasCount = snap.PtEntries.Count;
            snap.Generation = Interlocked.Increment(ref _generationSeq);
            snap.IsReady = true;
            _snap = snap;
        }

        private class ScoredLex
        {
            public int Score;
            public LexEntry Entry;
        }

        private static int ScorePtItem(LexEntry item, string q, string qStem)
        {
            if (item.PtNorm == q) return 140;
            if (item.PtHead == q) return 128;

            string[] hWords = item.HeadWords;
            for (int h = 0; h < hWords.Length; h++)
            {
                if (hWords[h] == q) return 105 - Math.Min(20, item.Words.Length);
            }

            string[] words = item.Words;
            bool stemMatch = false;
            for (int w = 0; w < words.Length; w++)
            {
                string wrd = words[w];
                if (wrd == q) return 85 - Math.Min(25, words.Length * 2);
                if (qStem.Length >= 3 && (wrd == qStem || wrd.StartsWith(qStem, StringComparison.Ordinal)))
                {
                    stemMatch = true;
                }
            }
            if (stemMatch) return 62 - Math.Min(20, words.Length);
            if (q.Length >= 3 && item.PtNorm.IndexOf(q, StringComparison.Ordinal) >= 0) return 40;
            return 0;
        }

        public List<LexEntry> SearchPtToken(string ptToken, int limit)
        {
            LexiconSnapshot snap = _snap;
            string q = StripAccents(ptToken).Trim();
            List<LexEntry> outList = new List<LexEntry>();
            if (string.IsNullOrEmpty(q) || snap.PtEntries.Count == 0) return outList;

            string qStem = ComputePtStem(q);
            List<ScoredLex> scored = new List<ScoredLex>(32);
            HashSet<int> candidateIdx = new HashSet<int>();

            List<int> bucket;
            if (snap.PtTokenMap.TryGetValue(q, out bucket))
            {
                for (int i = 0; i < bucket.Count; i++) candidateIdx.Add(bucket[i]);
            }
            if (!string.IsNullOrEmpty(qStem) && qStem != q && snap.PtTokenMap.TryGetValue(qStem, out bucket))
            {
                for (int i = 0; i < bucket.Count; i++) candidateIdx.Add(bucket[i]);
            }
            if (qStem.Length >= 3 && snap.PtStemMap.TryGetValue(qStem.Substring(0, 3), out bucket))
            {
                for (int i = 0; i < bucket.Count; i++) candidateIdx.Add(bucket[i]);
            }

            if (candidateIdx.Count > 0)
            {
                foreach (int idx in candidateIdx)
                {
                    LexEntry item = snap.PtEntries[idx];
                    int sc = ScorePtItem(item, q, qStem);
                    if (sc > 0) scored.Add(new ScoredLex { Score = sc + item.Boost, Entry = item });
                }
            }

            // Fallback de substring caso nenhum token exato/radical tenha atingido o limite
            if (scored.Count < limit && q.Length >= 3)
            {
                List<LexEntry> all = snap.PtEntries;
                for (int i = 0; i < all.Count; i++)
                {
                    if (candidateIdx.Contains(i)) continue;
                    LexEntry item = all[i];
                    if (item.PtNorm.IndexOf(q, StringComparison.Ordinal) >= 0)
                    {
                        scored.Add(new ScoredLex { Score = 40 + item.Boost, Entry = item });
                    }
                }
            }

            scored.Sort((a, b) => b.Score.CompareTo(a.Score));
            HashSet<string> seen = new HashSet<string>(StringComparer.Ordinal);
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
            LexiconSnapshot snap = _snap;
            if (!snap.IsReady) return "Indexando banco de dados em segundo plano... tente em 2 segundos.";
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
            LexiconSnapshot snap = _snap;
            if (!snap.IsReady) return "Indexando banco de dados em segundo plano... tente em 2 segundos.";
            string qRaw = (query ?? "").Trim();
            if (string.IsNullOrEmpty(qRaw)) return "Digite palavras ou frases em Tréppio.";

            Dictionary<string, List<LexEntry>> revSnap = snap.TrReverse;
            Dictionary<string, string> corpSnap = snap.CorpusByTreppio;

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

        public static string EscapeJsonValue(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            StringBuilder sb = new StringBuilder(s.Length + 8);
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '\\') sb.Append("\\\\");
                else if (c == '"') sb.Append("\\\"");
                else if (c == '\r') sb.Append("\\r");
                else if (c == '\n') sb.Append("\\n");
                else if (c == '\t') sb.Append("\\t");
                else if (c < 0x20) sb.AppendFormat("\\u{0:x4}", (int)c);
                else sb.Append(c);
            }
            return sb.ToString();
        }

        public string BuildIpaJson(string query)
        {
            string q = (query ?? "").Trim();
            List<IpaWordInfo> words = AnalyzeSentenceIpa(q);
            StringBuilder sb = new StringBuilder(512);
            sb.Append("{\"ok\":true,\"query\":\"");
            sb.Append(EscapeJsonValue(q));
            sb.Append("\",\"ttsPtBr\":\"");
            sb.Append(EscapeJsonValue(ToTtsPtBr(q)));
            sb.Append("\",\"words\":[");
            for (int i = 0; i < words.Count; i++)
            {
                if (i > 0) sb.Append(',');
                IpaWordInfo w = words[i];
                sb.Append("{\"word\":\"");
                sb.Append(EscapeJsonValue(w.Word));
                sb.Append("\",\"syllables\":\"");
                sb.Append(EscapeJsonValue(w.SyllablesJoined));
                sb.Append("\",\"ipa\":\"");
                sb.Append(EscapeJsonValue(w.Ipa));
                sb.Append("\",\"notes\":\"");
                sb.Append(EscapeJsonValue(w.Notes));
                sb.Append("\"}");
            }
            sb.Append("]}");
            return sb.ToString();
        }

        public string BuildTranslateJson(string dir, string query)
        {
            string d = (dir ?? "pt-tr").Trim().ToLowerInvariant();
            string q = (query ?? "").Trim();
            string primary = "";
            string report;
            if (d == "tr-pt")
            {
                report = TranslateTrToPtReport(q);
                IpaWordInfo ipa = AnalyzeWordIpa(q);
                primary = ipa != null ? ipa.Word : q;
            }
            else
            {
                d = "pt-tr";
                report = TranslatePtToTrReport(q, out primary);
            }
            StringBuilder sb = new StringBuilder(1024);
            sb.Append("{\"ok\":true,\"ready\":");
            sb.Append(_snap.IsReady ? "true" : "false");
            sb.Append(",\"dir\":\"");
            sb.Append(EscapeJsonValue(d));
            sb.Append("\",\"query\":\"");
            sb.Append(EscapeJsonValue(q));
            sb.Append("\",\"primary\":\"");
            sb.Append(EscapeJsonValue(primary));
            sb.Append("\",\"report\":\"");
            sb.Append(EscapeJsonValue(report));
            sb.Append("\"}");
            return sb.ToString();
        }

        public string BuildSearchJson(string query, int limit)
        {
            LexiconSnapshot snap = _snap;
            string q = (query ?? "").Trim();
            int lim = Math.Max(1, Math.Min(30, limit));
            StringBuilder sb = new StringBuilder(1024);
            sb.Append("{\"ok\":true,\"ready\":");
            sb.Append(snap.IsReady ? "true" : "false");
            sb.Append(",\"query\":\"");
            sb.Append(EscapeJsonValue(q));
            sb.Append("\",\"reverseMatches\":[");

            if (!string.IsNullOrEmpty(q) && snap.IsReady)
            {
                string clean = q.Replace("!", "").Replace("?", "").Trim().ToLowerInvariant();
                List<LexEntry> revList;
                if (snap.TrReverse.TryGetValue(clean, out revList) && revList != null)
                {
                    int n = Math.Min(lim, revList.Count);
                    for (int i = 0; i < n; i++)
                    {
                        if (i > 0) sb.Append(',');
                        LexEntry e = revList[i];
                        sb.Append("{\"treppio\":\"");
                        sb.Append(EscapeJsonValue(e.Treppio));
                        sb.Append("\",\"classTag\":\"");
                        sb.Append(EscapeJsonValue(e.ClassTag));
                        sb.Append("\",\"detail\":\"");
                        sb.Append(EscapeJsonValue(e.Detail));
                        sb.Append("\",\"pt\":\"");
                        sb.Append(EscapeJsonValue(e.PtMeaning));
                        sb.Append("\"}");
                    }
                }
            }

            sb.Append("],\"ptMatches\":[");
            if (!string.IsNullOrEmpty(q) && snap.IsReady)
            {
                List<LexEntry> ptList = SearchPtToken(q, lim);
                for (int i = 0; i < ptList.Count; i++)
                {
                    if (i > 0) sb.Append(',');
                    LexEntry e = ptList[i];
                    sb.Append("{\"treppio\":\"");
                    sb.Append(EscapeJsonValue(e.Treppio));
                    sb.Append("\",\"classTag\":\"");
                    sb.Append(EscapeJsonValue(e.ClassTag));
                    sb.Append("\",\"detail\":\"");
                    sb.Append(EscapeJsonValue(e.Detail));
                    sb.Append("\",\"pt\":\"");
                    sb.Append(EscapeJsonValue(e.PtMeaning));
                    sb.Append("\"}");
                }
            }
            sb.Append("]}");
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

    public sealed class EmbeddedServer
    {
        private sealed class StaticAssetEntry
        {
            public byte[] RawBytes;
            public byte[] GzipBytes;
            public string ContentType;
            public string ETag;
            public string CacheControl;
        }

        private sealed class PayloadSnapshot
        {
            public byte[] HtmlRaw;
            public byte[] HtmlGzip;
            public string HtmlETag;

            public byte[] JsonRaw;
            public byte[] JsonGzip;
            public string JsonETag;

            public byte[] DadosJsRaw;
            public byte[] DadosJsGzip;
            public string DadosJsETag;

            public Dictionary<string, StaticAssetEntry> Assets = new Dictionary<string, StaticAssetEntry>(StringComparer.OrdinalIgnoreCase);
            public string ActiveSource;
        }

        private sealed class CachedBytePair
        {
            public byte[] Raw;
            public byte[] Gzip;
        }

        private sealed class BoundedLruCache
        {
            private readonly int _capacity;
            private readonly object _sync = new object();
            private readonly Dictionary<string, LinkedListNode<KeyValuePair<string, CachedBytePair>>> _map;
            private readonly LinkedList<KeyValuePair<string, CachedBytePair>> _order;

            public BoundedLruCache(int capacity)
            {
                _capacity = Math.Max(64, capacity);
                _map = new Dictionary<string, LinkedListNode<KeyValuePair<string, CachedBytePair>>>(StringComparer.Ordinal);
                _order = new LinkedList<KeyValuePair<string, CachedBytePair>>();
            }

            public bool TryGet(string key, out CachedBytePair val)
            {
                lock (_sync)
                {
                    LinkedListNode<KeyValuePair<string, CachedBytePair>> node;
                    if (_map.TryGetValue(key, out node))
                    {
                        _order.Remove(node);
                        _order.AddFirst(node);
                        val = node.Value.Value;
                        return true;
                    }
                    val = null;
                    return false;
                }
            }

            public void Put(string key, CachedBytePair val)
            {
                lock (_sync)
                {
                    LinkedListNode<KeyValuePair<string, CachedBytePair>> existing;
                    if (_map.TryGetValue(key, out existing))
                    {
                        _order.Remove(existing);
                        existing.Value = new KeyValuePair<string, CachedBytePair>(key, val);
                        _order.AddFirst(existing);
                        return;
                    }
                    if (_map.Count >= _capacity && _order.Last != null)
                    {
                        LinkedListNode<KeyValuePair<string, CachedBytePair>> oldest = _order.Last;
                        _order.RemoveLast();
                        _map.Remove(oldest.Value.Key);
                    }
                    LinkedListNode<KeyValuePair<string, CachedBytePair>> node = new LinkedListNode<KeyValuePair<string, CachedBytePair>>(
                        new KeyValuePair<string, CachedBytePair>(key, val)
                    );
                    _order.AddFirst(node);
                    _map[key] = node;
                }
            }
        }

        private sealed class HttpParsedRequest
        {
            public string Method;
            public string Path;
            public string Query;
            public bool KeepAlive;
            public bool AcceptsGzip;
            public string IfNoneMatch;
            public string Body;
        }

        private Socket _listenerV4;
        private Socket _listenerV6;
        private volatile bool _running;
        private int _activeConnections;
        private const int MaxConcurrentConnections = 2500;
        private const int KeepAliveIdleTimeoutMs = 8000;
        private const int MaxKeepAliveRequests = 1000;

        public int Port { get; private set; }
        public int PreferredPort { get; set; }
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

        private PayloadSnapshot _snapshot;
        private readonly BoundedLruCache _apiLru = new BoundedLruCache(2048);
        private readonly ConcurrentBag<byte[]> _bufferPool = new ConcurrentBag<byte[]>();
        private readonly SemaphoreSlim _recompileGate = new SemaphoreSlim(1, 1);

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

        private byte[] RentBuffer()
        {
            byte[] buf;
            if (_bufferPool.TryTake(out buf)) return buf;
            return new byte[8192];
        }

        private void ReturnBuffer(byte[] buf)
        {
            if (buf != null && _bufferPool.Count < 1024)
            {
                _bufferPool.Add(buf);
            }
        }

        private static byte[] CompressGzip(byte[] raw)
        {
            if (raw == null || raw.Length == 0) return new byte[0];
            using (MemoryStream ms = new MemoryStream())
            {
                using (GZipStream gz = new GZipStream(ms, CompressionLevel.Optimal, true))
                {
                    gz.Write(raw, 0, raw.Length);
                }
                return ms.ToArray();
            }
        }

        private static byte[] DecompressGzip(byte[] gzBytes)
        {
            if (gzBytes == null || gzBytes.Length == 0) return new byte[0];
            using (MemoryStream src = new MemoryStream(gzBytes))
            using (GZipStream gz = new GZipStream(src, CompressionMode.Decompress))
            using (MemoryStream dst = new MemoryStream())
            {
                gz.CopyTo(dst);
                return dst.ToArray();
            }
        }

        private static string ComputeETag(byte[] data)
        {
            if (data == null) return "\"0\"";
            using (SHA256 sha = SHA256.Create())
            {
                byte[] h = sha.ComputeHash(data);
                StringBuilder sb = new StringBuilder(20);
                sb.Append('"');
                for (int i = 0; i < 8; i++) sb.Append(h[i].ToString("x2", CultureInfo.InvariantCulture));
                sb.Append('"');
                return sb.ToString();
            }
        }

        private static byte[] BuildDadosJsBytes(byte[] jsonBytes)
        {
            byte[] prefix = Encoding.UTF8.GetBytes("window.CONDE_DB = ");
            byte[] suffix = Encoding.UTF8.GetBytes(";\n");
            byte[] res = new byte[prefix.Length + jsonBytes.Length + suffix.Length];
            Buffer.BlockCopy(prefix, 0, res, 0, prefix.Length);
            Buffer.BlockCopy(jsonBytes, 0, res, prefix.Length, jsonBytes.Length);
            Buffer.BlockCopy(suffix, 0, res, prefix.Length + jsonBytes.Length, suffix.Length);
            return res;
        }

        private StaticAssetEntry LoadAssetEntry(string fileName, string contentType, string cacheControl)
        {
            byte[] raw = null;
            string diskPath = Path.Combine(_localUiDir, fileName);
            if (File.Exists(diskPath))
            {
                raw = File.ReadAllBytes(diskPath);
            }
            else
            {
                raw = ReadEmbeddedResourceOrNull(fileName);
            }
            if (raw == null) return null;
            bool compress = !fileName.EndsWith(".png", StringComparison.OrdinalIgnoreCase) && raw.Length >= 256;
            return new StaticAssetEntry
            {
                RawBytes = raw,
                GzipBytes = compress ? CompressGzip(raw) : null,
                ContentType = contentType,
                ETag = ComputeETag(raw),
                CacheControl = cacheControl
            };
        }

        public void ReloadPayloads()
        {
            byte[] htmlRaw = File.Exists(_localCondeHtmlPath)
                ? File.ReadAllBytes(_localCondeHtmlPath)
                : ReadEmbeddedResource("index.html");

            byte[] jsonRaw;
            string sourceLabel;
            if (File.Exists(_localCondeDbPath))
            {
                jsonRaw = File.ReadAllBytes(_localCondeDbPath);
                sourceLabel = "Base Local Oficial (D:\\Conde_Treppio)";
            }
            else if (File.Exists(_cachedDbPath))
            {
                jsonRaw = File.ReadAllBytes(_cachedDbPath);
                sourceLabel = "Banco Sincronizado da Nuvem (Git/Drive)";
            }
            else
            {
                byte[] embGz = ReadEmbeddedResourceOrNull("dicionario_formas_expandidas.json.gz");
                if (embGz != null)
                {
                    jsonRaw = DecompressGzip(embGz);
                }
                else
                {
                    jsonRaw = ReadEmbeddedResource("dicionario_formas_expandidas.json");
                }
                sourceLabel = "Banco Embutido no Executavel (Offline)";
            }

            SwapPayloadSnapshot(htmlRaw, jsonRaw, sourceLabel);
        }

        private void SwapPayloadSnapshot(byte[] htmlRaw, byte[] jsonRaw, string sourceLabel)
        {
            ActiveSource = sourceLabel;
            ParseMetadataMetrics(jsonRaw);

            PayloadSnapshot next = new PayloadSnapshot();
            next.ActiveSource = sourceLabel;
            next.HtmlRaw = htmlRaw ?? new byte[0];
            next.HtmlGzip = CompressGzip(next.HtmlRaw);
            next.HtmlETag = ComputeETag(next.HtmlRaw);

            next.JsonRaw = jsonRaw ?? Encoding.UTF8.GetBytes("{}");
            next.JsonGzip = CompressGzip(next.JsonRaw);
            next.JsonETag = ComputeETag(next.JsonRaw);

            next.DadosJsRaw = BuildDadosJsBytes(next.JsonRaw);
            next.DadosJsGzip = CompressGzip(next.DadosJsRaw);
            next.DadosJsETag = ComputeETag(next.DadosJsRaw);

            AddStaticIfPresent(next, "manifest.json", "application/manifest+json; charset=utf-8", "public, max-age=300");
            AddStaticIfPresent(next, "sw.js", "application/javascript; charset=utf-8", "no-cache");
            AddStaticIfPresent(next, "icon-512.png", "image/png", "public, max-age=86400");
            AddStaticIfPresent(next, "icon-192.png", "image/png", "public, max-age=86400");
            AddStaticIfPresent(next, "icon-maskable-512.png", "image/png", "public, max-age=86400");
            AddStaticIfPresent(next, "favicon.ico", "image/x-icon", "public, max-age=86400");

            Interlocked.Exchange(ref _snapshot, next);
            StartBackgroundIndexBuild(next.JsonRaw);
        }

        private void AddStaticIfPresent(PayloadSnapshot snap, string name, string mime, string cacheControl)
        {
            StaticAssetEntry entry = LoadAssetEntry(name, mime, cacheControl);
            if (entry != null) snap.Assets[name] = entry;
        }

        public void StartBackgroundIndexBuild()
        {
            PayloadSnapshot snap = _snapshot;
            if (snap != null) StartBackgroundIndexBuild(snap.JsonRaw);
        }

        private void StartBackgroundIndexBuild(byte[] snapshotJson)
        {
            ThreadPool.QueueUserWorkItem(_ =>
            {
                try
                {
                    Lexicon.BuildFromJsonBytes(snapshotJson);
                    Action handler = LexiconUpdated;
                    if (handler != null) handler();
                }
                catch { }
            });
        }

        private void ParseMetadataMetrics(byte[] jsonBytes)
        {
            TotalForms = 246737;
            NounsCount = 2109;
            VerbsCount = 1768;
            AdjsCount = 446;
            AdvsCount = 1202;

            try
            {
                if (jsonBytes == null || jsonBytes.Length == 0) return;
                int scanLen = Math.Min(jsonBytes.Length, 4096);
                string head = Encoding.UTF8.GetString(jsonBytes, 0, scanLen);

                TotalForms = ExtractIntMetric(head, "total_expanded_word_forms", TotalForms);
                NounsCount = ExtractIntMetric(head, "nouns_count", NounsCount);
                VerbsCount = ExtractIntMetric(head, "verb_stems_quadripartite", VerbsCount);
                AdjsCount = ExtractIntMetric(head, "adjectives_count", AdjsCount);
                AdvsCount = ExtractIntMetric(head, "adverbs_count", AdvsCount);

                if (TotalForms == 246737 && jsonBytes.Length > 4096)
                {
                    string tail = Encoding.UTF8.GetString(jsonBytes, jsonBytes.Length - 4096, 4096);
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

        private static byte[] ReadEmbeddedResourceOrNull(string resourceName)
        {
            Assembly asm = Assembly.GetExecutingAssembly();
            using (Stream s = asm.GetManifestResourceStream(resourceName))
            {
                if (s == null) return null;
                using (MemoryStream ms = new MemoryStream())
                {
                    s.CopyTo(ms);
                    return ms.ToArray();
                }
            }
        }

        private byte[] ReadEmbeddedResource(string resourceName)
        {
            byte[] data = ReadEmbeddedResourceOrNull(resourceName);
            return data ?? Encoding.UTF8.GetBytes("{}");
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
                    wc.Headers.Add("User-Agent", "CondeTreppioLauncher/8.5");
                    string json = wc.DownloadString(directUrl);
                    if (!json.Contains("\"substantivos\""))
                    {
                        message = "O arquivo baixado nao contem um banco de dados valido do /conde.";
                        return false;
                    }
                    File.WriteAllText(_cachedDbPath, json, Encoding.UTF8);
                    File.WriteAllText(_cloudConfigPath, directUrl, Encoding.UTF8);
                    CloudUrl = directUrl;

                    PayloadSnapshot cur = _snapshot;
                    byte[] htmlRaw = cur != null ? cur.HtmlRaw : ReadEmbeddedResource("index.html");
                    SwapPayloadSnapshot(htmlRaw, Encoding.UTF8.GetBytes(json), "Nuvem Sincronizada (Git/Google Drive)");
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
            if (!_recompileGate.Wait(0))
            {
                _recompileGate.Wait();
                _recompileGate.Release();
                message = "Recompilacao em andamento aproveitada (" + TotalForms.ToString("N0", new CultureInfo("pt-BR")) + " formas).";
                return true;
            }

            try
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
            finally
            {
                _recompileGate.Release();
            }
        }

        public void Start()
        {
            int minW, minC;
            ThreadPool.GetMinThreads(out minW, out minC);
            ThreadPool.SetMinThreads(Math.Max(minW, 128), Math.Max(minC, 128));

            List<int> candidatePorts = new List<int>();
            if (PreferredPort > 0) candidatePorts.Add(PreferredPort);
            candidatePorts.Add(8766);
            candidatePorts.Add(8767);
            candidatePorts.Add(8768);
            candidatePorts.Add(0);

            for (int i = 0; i < candidatePorts.Count; i++)
            {
                int p = candidatePorts[i];
                Socket sock = null;
                try
                {
                    sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                    sock.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
                    sock.Bind(new IPEndPoint(IPAddress.Loopback, p));
                    sock.Listen(2048);
                    _listenerV4 = sock;
                    Port = ((IPEndPoint)sock.LocalEndPoint).Port;
                    break;
                }
                catch
                {
                    if (sock != null) { try { sock.Close(); } catch { } }
                }
            }

            if (_listenerV4 == null)
            {
                throw new InvalidOperationException("Nao foi possivel vincular o servidor HTTP local.");
            }

            try
            {
                Socket sock6 = new Socket(AddressFamily.InterNetworkV6, SocketType.Stream, ProtocolType.Tcp);
                sock6.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
                sock6.Bind(new IPEndPoint(IPAddress.IPv6Loopback, Port));
                sock6.Listen(2048);
                _listenerV6 = sock6;
            }
            catch
            {
                _listenerV6 = null;
            }

            _running = true;
            StartAcceptLoop(_listenerV4);
            if (_listenerV6 != null) StartAcceptLoop(_listenerV6);
        }

        public void Stop()
        {
            _running = false;
            try { if (_listenerV4 != null) _listenerV4.Close(); } catch { }
            try { if (_listenerV6 != null) _listenerV6.Close(); } catch { }
        }

        private void StartAcceptLoop(Socket listener)
        {
            Task.Run(async () =>
            {
                while (_running)
                {
                    Socket client = null;
                    try
                    {
                        client = await Task.Factory.FromAsync<Socket>(listener.BeginAccept, listener.EndAccept, null).ConfigureAwait(false);
                    }
                    catch
                    {
                        if (!_running) break;
                        continue;
                    }
                    if (client == null) continue;
                    Task _unused = HandleSocketAsync(client);
                }
            });
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

        private static int FindHeaderEnd(byte[] buf, int len)
        {
            for (int i = 0; i <= len - 4; i++)
            {
                if (buf[i] == 13 && buf[i + 1] == 10 && buf[i + 2] == 13 && buf[i + 3] == 10)
                {
                    return i;
                }
            }
            return -1;
        }

        private async Task<int> ReadWithTimeoutAsync(NetworkStream ns, byte[] buf, int offset, int count, int timeoutMs)
        {
            Task<int> readTask = ns.ReadAsync(buf, offset, count);
            Task delayTask = Task.Delay(timeoutMs);
            Task completed = await Task.WhenAny(readTask, delayTask).ConfigureAwait(false);
            if (completed != readTask) return -2;
            return await readTask.ConfigureAwait(false);
        }

        private async Task<HttpParsedRequest> ReadHttpRequestAsync(NetworkStream ns, byte[] buf)
        {
            int filled = 0;
            int headerEnd = -1;

            while (headerEnd < 0)
            {
                if (filled >= buf.Length) return null;
                int n = await ReadWithTimeoutAsync(ns, buf, filled, buf.Length - filled, KeepAliveIdleTimeoutMs).ConfigureAwait(false);
                if (n <= 0) return null;
                filled += n;
                headerEnd = FindHeaderEnd(buf, filled);
            }

            string headerText = Encoding.ASCII.GetString(buf, 0, headerEnd);
            string[] lines = headerText.Split(new string[] { "\r\n" }, StringSplitOptions.None);
            if (lines.Length == 0) return null;

            string[] first = lines[0].Split(' ');
            if (first.Length < 2) return null;

            HttpParsedRequest req = new HttpParsedRequest();
            req.Method = first[0].ToUpperInvariant();
            string rawTarget = first[1];
            int qIdx = rawTarget.IndexOf('?');
            req.Path = qIdx >= 0 ? rawTarget.Substring(0, qIdx) : rawTarget;
            req.Query = qIdx >= 0 ? rawTarget.Substring(qIdx + 1) : "";

            bool isHttp10 = first.Length >= 3 && first[2].Equals("HTTP/1.0", StringComparison.OrdinalIgnoreCase);
            bool hasConnKeepAlive = false;
            bool hasConnClose = false;
            int contentLength = 0;

            for (int i = 1; i < lines.Length; i++)
            {
                string line = lines[i];
                int colon = line.IndexOf(':');
                if (colon <= 0) continue;
                string hName = line.Substring(0, colon).Trim();
                string hVal = line.Substring(colon + 1).Trim();

                if (hName.Equals("Connection", StringComparison.OrdinalIgnoreCase))
                {
                    if (hVal.IndexOf("close", StringComparison.OrdinalIgnoreCase) >= 0) hasConnClose = true;
                    if (hVal.IndexOf("keep-alive", StringComparison.OrdinalIgnoreCase) >= 0) hasConnKeepAlive = true;
                }
                else if (hName.Equals("Accept-Encoding", StringComparison.OrdinalIgnoreCase))
                {
                    if (hVal.IndexOf("gzip", StringComparison.OrdinalIgnoreCase) >= 0) req.AcceptsGzip = true;
                }
                else if (hName.Equals("If-None-Match", StringComparison.OrdinalIgnoreCase))
                {
                    req.IfNoneMatch = hVal;
                }
                else if (hName.Equals("Content-Length", StringComparison.OrdinalIgnoreCase))
                {
                    int cl;
                    if (int.TryParse(hVal, out cl) && cl > 0) contentLength = Math.Min(cl, 1024 * 1024);
                }
            }

            req.KeepAlive = isHttp10 ? (hasConnKeepAlive && !hasConnClose) : !hasConnClose;

            int bodyOffset = headerEnd + 4;
            int alreadyHave = filled - bodyOffset;
            if (contentLength > 0)
            {
                byte[] bodyBytes = new byte[contentLength];
                int copyLen = Math.Min(alreadyHave, contentLength);
                if (copyLen > 0) Buffer.BlockCopy(buf, bodyOffset, bodyBytes, 0, copyLen);
                int got = copyLen;
                while (got < contentLength)
                {
                    int n = await ReadWithTimeoutAsync(ns, bodyBytes, got, contentLength - got, KeepAliveIdleTimeoutMs).ConfigureAwait(false);
                    if (n <= 0) break;
                    got += n;
                }
                req.Body = Encoding.UTF8.GetString(bodyBytes, 0, got);
            }
            else
            {
                req.Body = "";
            }

            return req;
        }

        private static string GetQueryParam(string queryString, string key)
        {
            if (string.IsNullOrEmpty(queryString)) return "";
            string[] pairs = queryString.Split('&');
            for (int i = 0; i < pairs.Length; i++)
            {
                string p = pairs[i];
                int eq = p.IndexOf('=');
                string k = eq >= 0 ? p.Substring(0, eq) : p;
                if (k.Equals(key, StringComparison.OrdinalIgnoreCase))
                {
                    string v = eq >= 0 ? p.Substring(eq + 1) : "";
                    return Uri.UnescapeDataString(v.Replace('+', ' '));
                }
            }
            return "";
        }

        private byte[] BuildHealthJsonBytes()
        {
            StringBuilder sb = new StringBuilder(256);
            sb.Append("{\"ok\":true,\"version\":\"8.5.0\",\"port\":");
            sb.Append(Port);
            sb.Append(",\"lexiconReady\":");
            sb.Append(Lexicon.IsReady ? "true" : "false");
            sb.Append(",\"totalForms\":");
            sb.Append(TotalForms);
            sb.Append(",\"nounsCount\":");
            sb.Append(NounsCount);
            sb.Append(",\"verbsCount\":");
            sb.Append(VerbsCount);
            sb.Append(",\"adjsCount\":");
            sb.Append(AdjsCount);
            sb.Append(",\"advsCount\":");
            sb.Append(AdvsCount);
            sb.Append(",\"indexedForms\":");
            sb.Append(Lexicon.IndexedFormsCount);
            sb.Append(",\"indexedLemmas\":");
            sb.Append(Lexicon.IndexedLemmasCount);
            sb.Append(",\"activeConnections\":");
            sb.Append(Thread.VolatileRead(ref _activeConnections));
            sb.Append(",\"activeSource\":\"");
            sb.Append(TreppioLexiconEngine.EscapeJsonValue(ActiveSource));
            sb.Append("\"}");
            return Encoding.UTF8.GetBytes(sb.ToString());
        }

        private CachedBytePair GetOrBuildCachedApiResponse(string cacheKey, Func<string> jsonBuilder)
        {
            CachedBytePair pair;
            if (_apiLru.TryGet(cacheKey, out pair)) return pair;

            string json = jsonBuilder();
            byte[] raw = Encoding.UTF8.GetBytes(json);
            byte[] gz = raw.Length >= 256 ? CompressGzip(raw) : null;
            if (gz != null && gz.Length >= raw.Length) gz = null;

            pair = new CachedBytePair { Raw = raw, Gzip = gz };
            _apiLru.Put(cacheKey, pair);
            return pair;
        }

        private async Task HandleSocketAsync(Socket sock)
        {
            int curConns = Interlocked.Increment(ref _activeConnections);
            byte[] readBuf = null;
            try
            {
                sock.NoDelay = true;
                using (sock)
                using (NetworkStream ns = new NetworkStream(sock, false))
                {
                    if (curConns > MaxConcurrentConnections)
                    {
                        byte[] busy = Encoding.UTF8.GetBytes("Server busy");
                        await WriteHttpResponseAsync(ns, "503 Service Unavailable", "text/plain; charset=utf-8", busy, false, null, "no-store", false, false).ConfigureAwait(false);
                        return;
                    }

                    readBuf = RentBuffer();
                    int reqCount = 0;

                    while (_running && reqCount < MaxKeepAliveRequests)
                    {
                        HttpParsedRequest req = await ReadHttpRequestAsync(ns, readBuf).ConfigureAwait(false);
                        if (req == null) break;
                        reqCount++;

                        bool keepAlive = req.KeepAlive && reqCount < MaxKeepAliveRequests;
                        bool isHead = req.Method == "HEAD";
                        PayloadSnapshot snap = _snapshot;
                        string path = req.Path;

                        if (path == "/api/health")
                        {
                            byte[] healthBytes = BuildHealthJsonBytes();
                            await WriteHttpResponseAsync(ns, "200 OK", "application/json; charset=utf-8", healthBytes, false, null, "no-store", keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/api/ipa")
                        {
                            string q = GetQueryParam(req.Query, "q");
                            if (string.IsNullOrEmpty(q)) q = "Haly'itror giza in oxej";
                            string key = "ipa|" + q;
                            CachedBytePair pair = GetOrBuildCachedApiResponse(key, () => Lexicon.BuildIpaJson(q));
                            await WriteNegotiatedAsync(ns, "200 OK", "application/json; charset=utf-8", pair.Raw, pair.Gzip, req.AcceptsGzip, null, req.IfNoneMatch, "no-cache", keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/api/traduzir")
                        {
                            string dir = GetQueryParam(req.Query, "dir");
                            if (string.IsNullOrEmpty(dir)) dir = "pt-tr";
                            string q = GetQueryParam(req.Query, "q");
                            string key = Lexicon.Generation + "|tr|" + dir + "|" + q;
                            CachedBytePair pair = GetOrBuildCachedApiResponse(key, () => Lexicon.BuildTranslateJson(dir, q));
                            await WriteNegotiatedAsync(ns, "200 OK", "application/json; charset=utf-8", pair.Raw, pair.Gzip, req.AcceptsGzip, null, req.IfNoneMatch, "no-cache", keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/api/search")
                        {
                            string q = GetQueryParam(req.Query, "q");
                            int limit = 12;
                            string limStr = GetQueryParam(req.Query, "limit");
                            int parsedLim;
                            if (int.TryParse(limStr, out parsedLim) && parsedLim > 0) limit = parsedLim;
                            string key = Lexicon.Generation + "|sr|" + limit + "|" + q;
                            CachedBytePair pair = GetOrBuildCachedApiResponse(key, () => Lexicon.BuildSearchJson(q, limit));
                            await WriteNegotiatedAsync(ns, "200 OK", "application/json; charset=utf-8", pair.Raw, pair.Gzip, req.AcceptsGzip, null, req.IfNoneMatch, "no-cache", keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/api/db" || path.EndsWith("/dicionario_formas_expandidas.json", StringComparison.OrdinalIgnoreCase))
                        {
                            await WriteNegotiatedAsync(ns, "200 OK", "application/json; charset=utf-8", snap.JsonRaw, snap.JsonGzip, req.AcceptsGzip, snap.JsonETag, req.IfNoneMatch, "no-cache", keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/dados_dicionario_conde.js")
                        {
                            await WriteNegotiatedAsync(ns, "200 OK", "application/javascript; charset=utf-8", snap.DadosJsRaw, snap.DadosJsGzip, req.AcceptsGzip, snap.DadosJsETag, req.IfNoneMatch, "public, max-age=60", keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/" || path == "/index.html")
                        {
                            await WriteNegotiatedAsync(ns, "200 OK", "text/html; charset=utf-8", snap.HtmlRaw, snap.HtmlGzip, req.AcceptsGzip, snap.HtmlETag, req.IfNoneMatch, "no-cache", keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/api/recompilar" && req.Method == "POST")
                        {
                            string msg;
                            RecompileLocalConde(out msg);
                            PayloadSnapshot updated = _snapshot;
                            byte[] prefix = Encoding.UTF8.GetBytes("{\"status\":\"ok\",\"source\":\"" + TreppioLexiconEngine.EscapeJsonValue(updated.ActiveSource) + "\",\"db\":");
                            byte[] suffix = Encoding.UTF8.GetBytes("}");
                            byte[] combined = new byte[prefix.Length + updated.JsonRaw.Length + suffix.Length];
                            Buffer.BlockCopy(prefix, 0, combined, 0, prefix.Length);
                            Buffer.BlockCopy(updated.JsonRaw, 0, combined, prefix.Length, updated.JsonRaw.Length);
                            Buffer.BlockCopy(suffix, 0, combined, prefix.Length + updated.JsonRaw.Length, suffix.Length);
                            byte[] gzCombined = req.AcceptsGzip ? CompressGzip(combined) : null;
                            await WriteNegotiatedAsync(ns, "200 OK", "application/json; charset=utf-8", combined, gzCombined, req.AcceptsGzip, null, null, "no-store", keepAlive, false).ConfigureAwait(false);
                        }
                        else if (path == "/api/cloud-config" && req.Method == "POST")
                        {
                            if (!string.IsNullOrEmpty(req.Body))
                            {
                                Match m = Regex.Match(req.Body, "\"cloud_url\"\\s*:\\s*\"([^\"]+)\"");
                                if (m.Success)
                                {
                                    string msg;
                                    SyncFromCloud(m.Groups[1].Value, out msg);
                                }
                            }
                            byte[] okBytes = Encoding.UTF8.GetBytes("{\"status\":\"ok\"}");
                            await WriteHttpResponseAsync(ns, "200 OK", "application/json; charset=utf-8", okBytes, false, null, "no-store", keepAlive, false).ConfigureAwait(false);
                        }
                        else if (path.StartsWith("/", StringComparison.Ordinal) && snap.Assets.ContainsKey(path.TrimStart('/')))
                        {
                            StaticAssetEntry asset = snap.Assets[path.TrimStart('/')];
                            await WriteNegotiatedAsync(ns, "200 OK", asset.ContentType, asset.RawBytes, asset.GzipBytes, req.AcceptsGzip, asset.ETag, req.IfNoneMatch, asset.CacheControl, keepAlive, isHead).ConfigureAwait(false);
                        }
                        else if (path == "/Codice_Treppio_Conde.exe" || path == "/Codice_Treppio_Conde.apk" || path == "/dist/Codice_Treppio_Portatil.html")
                        {
                            string diskPath = ResolveDownloadArtifact(path.TrimStart('/').Replace('/', Path.DirectorySeparatorChar));
                            if (diskPath != null)
                            {
                                string mime = path.EndsWith(".html", StringComparison.OrdinalIgnoreCase) ? "text/html; charset=utf-8" : "application/octet-stream";
                                await StreamFileResponseAsync(ns, diskPath, mime, keepAlive, isHead).ConfigureAwait(false);
                            }
                            else
                            {
                                byte[] nf = Encoding.UTF8.GetBytes("Artifact not found");
                                await WriteHttpResponseAsync(ns, "404 Not Found", "text/plain; charset=utf-8", nf, false, null, "no-store", keepAlive, isHead).ConfigureAwait(false);
                            }
                        }
                        else
                        {
                            byte[] nf = Encoding.UTF8.GetBytes("Not found");
                            await WriteHttpResponseAsync(ns, "404 Not Found", "text/plain; charset=utf-8", nf, false, null, "no-store", keepAlive, isHead).ConfigureAwait(false);
                        }

                        if (!keepAlive) break;
                    }
                }
            }
            catch { }
            finally
            {
                ReturnBuffer(readBuf);
                Interlocked.Decrement(ref _activeConnections);
            }
        }

        private static bool MatchesIfNoneMatch(string ifNoneMatch, string etag)
        {
            if (string.IsNullOrEmpty(ifNoneMatch) || string.IsNullOrEmpty(etag)) return false;
            string trim = ifNoneMatch.Trim();
            if (trim == "*" || trim == etag) return true;
            return trim.IndexOf(etag, StringComparison.Ordinal) >= 0;
        }

        private static Task WriteNegotiatedAsync(
            NetworkStream ns,
            string status,
            string contentType,
            byte[] rawBody,
            byte[] gzipBody,
            bool acceptsGzip,
            string etag,
            string ifNoneMatch,
            string cacheControl,
            bool keepAlive,
            bool isHead)
        {
            if (MatchesIfNoneMatch(ifNoneMatch, etag))
            {
                return WriteNotModifiedAsync(ns, etag, cacheControl, keepAlive);
            }

            bool useGzip = acceptsGzip && gzipBody != null && gzipBody.Length < rawBody.Length;
            byte[] payload = useGzip ? gzipBody : rawBody;
            return WriteHttpResponseAsync(ns, status, contentType, payload, useGzip, etag, cacheControl, keepAlive, isHead);
        }

        private static async Task WriteNotModifiedAsync(NetworkStream ns, string etag, string cacheControl, bool keepAlive)
        {
            StringBuilder sb = new StringBuilder(256);
            sb.Append("HTTP/1.1 304 Not Modified\r\n");
            if (!string.IsNullOrEmpty(etag)) { sb.Append("ETag: "); sb.Append(etag); sb.Append("\r\n"); }
            sb.Append("Cache-Control: "); sb.Append(cacheControl ?? "no-cache"); sb.Append("\r\n");
            sb.Append("Vary: Accept-Encoding\r\n");
            sb.Append("Access-Control-Allow-Origin: *\r\n");
            sb.Append("Connection: "); sb.Append(keepAlive ? "keep-alive\r\n\r\n" : "close\r\n\r\n");
            byte[] hdr = Encoding.ASCII.GetBytes(sb.ToString());
            await ns.WriteAsync(hdr, 0, hdr.Length).ConfigureAwait(false);
        }

        private static async Task WriteHttpResponseAsync(
            NetworkStream ns,
            string status,
            string contentType,
            byte[] body,
            bool isGzip,
            string etag,
            string cacheControl,
            bool keepAlive,
            bool isHead)
        {
            byte[] safeBody = body ?? new byte[0];
            StringBuilder sb = new StringBuilder(320);
            sb.Append("HTTP/1.1 "); sb.Append(status); sb.Append("\r\n");
            sb.Append("Content-Type: "); sb.Append(contentType); sb.Append("\r\n");
            sb.Append("Content-Length: "); sb.Append(safeBody.Length); sb.Append("\r\n");
            if (isGzip) sb.Append("Content-Encoding: gzip\r\n");
            sb.Append("Vary: Accept-Encoding\r\n");
            if (!string.IsNullOrEmpty(etag)) { sb.Append("ETag: "); sb.Append(etag); sb.Append("\r\n"); }
            sb.Append("Cache-Control: "); sb.Append(cacheControl ?? "no-cache"); sb.Append("\r\n");
            sb.Append("Access-Control-Allow-Origin: *\r\n");
            sb.Append("Connection: "); sb.Append(keepAlive ? "keep-alive\r\n\r\n" : "close\r\n\r\n");

            byte[] headerBytes = Encoding.ASCII.GetBytes(sb.ToString());
            await ns.WriteAsync(headerBytes, 0, headerBytes.Length).ConfigureAwait(false);
            if (!isHead && safeBody.Length > 0)
            {
                await ns.WriteAsync(safeBody, 0, safeBody.Length).ConfigureAwait(false);
            }
        }

        private static async Task StreamFileResponseAsync(NetworkStream ns, string diskPath, string contentType, bool keepAlive, bool isHead)
        {
            FileInfo fi = new FileInfo(diskPath);
            StringBuilder sb = new StringBuilder(256);
            sb.Append("HTTP/1.1 200 OK\r\n");
            sb.Append("Content-Type: "); sb.Append(contentType); sb.Append("\r\n");
            sb.Append("Content-Length: "); sb.Append(fi.Length); sb.Append("\r\n");
            sb.Append("Cache-Control: no-cache\r\n");
            sb.Append("Access-Control-Allow-Origin: *\r\n");
            sb.Append("Connection: "); sb.Append(keepAlive ? "keep-alive\r\n\r\n" : "close\r\n\r\n");

            byte[] headerBytes = Encoding.ASCII.GetBytes(sb.ToString());
            await ns.WriteAsync(headerBytes, 0, headerBytes.Length).ConfigureAwait(false);
            if (!isHead)
            {
                using (FileStream fs = new FileStream(diskPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, 65536, FileOptions.Asynchronous | FileOptions.SequentialScan))
                {
                    await fs.CopyToAsync(ns, 65536).ConfigureAwait(false);
                }
            }
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

        internal static Icon TryLoadFormIcon()
        {
            try
            {
                Assembly asm = Assembly.GetExecutingAssembly();
                using (Stream s = asm.GetManifestResourceStream("conde_form_gdi.ico"))
                {
                    if (s != null)
                    {
                        return new Icon(s);
                    }
                }
                string diskIco = @"D:\Conde_Treppio\sandbox\launcher_exe\conde_form_gdi.ico";
                if (File.Exists(diskIco)) return new Icon(diskIco);
                return Icon.ExtractAssociatedIcon(Application.ExecutablePath);
            }
            catch
            {
                return null;
            }
        }

        internal static Image TryLoadCrestImage()
        {
            try
            {
                Assembly asm = Assembly.GetExecutingAssembly();
                using (Stream s = asm.GetManifestResourceStream("conde_crest_header.png"))
                {
                    if (s != null)
                    {
                        using (MemoryStream ms = new MemoryStream())
                        {
                            s.CopyTo(ms);
                            ms.Position = 0;
                            return new Bitmap(ms);
                        }
                    }
                }
                string diskPng = @"D:\Conde_Treppio\sandbox\launcher_exe\conde_crest_header.png";
                if (File.Exists(diskPng)) return Image.FromFile(diskPng);
            }
            catch { }
            return null;
        }

        public LauncherForm(EmbeddedServer server)
        {
            _server = server;
            _tts = new TreppioTtsService();
            DoubleBuffered = true;

            AutoScaleMode = AutoScaleMode.Dpi;
            Text = "Códice Lexicográfico Imperial — Língua Tréppia (Era Clássica V8.5 | /conde)";
            Icon formIco = TryLoadFormIcon();
            if (formIco != null) Icon = formIco;

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

            Control crestControl;
            Image crestImg = TryLoadCrestImage();
            if (crestImg != null)
            {
                crestControl = new PictureBox
                {
                    Image = crestImg,
                    SizeMode = PictureBoxSizeMode.Zoom,
                    BackColor = Color.Transparent,
                    Size = new Size(52, 52),
                    Location = new Point(20, 13)
                };
            }
            else
            {
                crestControl = new Label
                {
                    Text = "C",
                    Font = new Font("Segoe UI", 18f, FontStyle.Bold),
                    ForeColor = Color.Gold,
                    BackColor = Color.FromArgb(26, 26, 32),
                    TextAlign = ContentAlignment.MiddleCenter,
                    Size = new Size(48, 48),
                    Location = new Point(22, 15)
                };
            }
            Label lblTitle = new Label
            {
                Text = "CÓDICE LEXICOGRÁFICO IMPERIAL DO TRÉPPIO (V8.5)",
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
            headerPanel.Controls.Add(crestControl);
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

            bool testHeadless = false;
            bool serveOnly = false;
            int requestedPort = 0;

            if (args != null)
            {
                for (int i = 0; i < args.Length; i++)
                {
                    if (args[i] == "--test-headless") testHeadless = true;
                    else if (args[i] == "--serve-only") serveOnly = true;
                    else if (args[i] == "--port" && i + 1 < args.Length)
                    {
                        int p;
                        if (int.TryParse(args[++i], out p) && p >= 0) requestedPort = p;
                    }
                }
            }

            EmbeddedServer server = new EmbeddedServer();
            if (requestedPort > 0) server.PreferredPort = requestedPort;
            server.Start();

            if (serveOnly)
            {
                for (int waitMs = 0; waitMs < 20000 && !server.Lexicon.IsReady; waitMs += 25)
                {
                    Thread.Sleep(25);
                }
                Console.WriteLine(string.Format(
                    "SERVE_ONLY_READY PORT={0} READY={1} FORMS={2} LEMMAS={3}",
                    server.Port, server.Lexicon.IsReady, server.Lexicon.IndexedFormsCount, server.Lexicon.IndexedLemmasCount
                ));
                Console.Out.Flush();

                using (ManualResetEventSlim stopGate = new ManualResetEventSlim(false))
                {
                    Console.CancelKeyPress += (s, e) =>
                    {
                        e.Cancel = true;
                        stopGate.Set();
                    };
                    stopGate.Wait();
                }
                server.Stop();
                return 0;
            }

            if (testHeadless)
            {
                try
                {
                    for (int waitMs = 0; waitMs < 20000 && !server.Lexicon.IsReady; waitMs += 25)
                    {
                        Thread.Sleep(25);
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

                    bool iconOk = false;
                    using (Icon fIco = LauncherForm.TryLoadFormIcon())
                    {
                        iconOk = (fIco != null && fIco.Width >= 16);
                    }
                    bool crestOk = false;
                    using (Image crImg = LauncherForm.TryLoadCrestImage())
                    {
                        crestOk = (crImg != null && crImg.Width >= 32);
                    }

                    using (WebClient wc = new WebClient())
                    {
                        wc.Encoding = Encoding.UTF8;
                        string baseUrl = "http://127.0.0.1:" + server.Port;
                        string dbJson = wc.DownloadString(baseUrl + "/api/db");
                        bool validDb = dbJson.Contains("\"substantivos\"") && dbJson.Contains("\"verbos_quadripartite\"");

                        string healthJson = wc.DownloadString(baseUrl + "/api/health");
                        string ipaJson = wc.DownloadString(baseUrl + "/api/ipa?q=vevar");
                        string apiTransJson = wc.DownloadString(baseUrl + "/api/traduzir?dir=pt-tr&q=" + Uri.EscapeDataString("pão"));
                        string apiSearchJson = wc.DownloadString(baseUrl + "/api/search?q=falde&limit=5");
                        bool apisOk = healthJson.Contains("\"ok\":true")
                                   && ipaJson.Contains("\"ipa\"")
                                   && apiTransJson.Contains("falde")
                                   && apiSearchJson.Contains("falde");

                        HttpWebRequest gzReq = (HttpWebRequest)WebRequest.Create(baseUrl + "/dados_dicionario_conde.js");
                        gzReq.Headers.Add("Accept-Encoding", "gzip");
                        string etag = "";
                        bool gzipJsOk = false;
                        using (HttpWebResponse gzResp = (HttpWebResponse)gzReq.GetResponse())
                        {
                            etag = gzResp.Headers["ETag"] ?? "";
                            gzipJsOk = gzResp.StatusCode == HttpStatusCode.OK && (gzResp.ContentEncoding ?? "").IndexOf("gzip", StringComparison.OrdinalIgnoreCase) >= 0;
                        }

                        bool etag304Ok = false;
                        if (!string.IsNullOrEmpty(etag))
                        {
                            HttpWebRequest req304 = (HttpWebRequest)WebRequest.Create(baseUrl + "/dados_dicionario_conde.js");
                            req304.Headers.Add("If-None-Match", etag);
                            try
                            {
                                using (HttpWebResponse resp304 = (HttpWebResponse)req304.GetResponse())
                                {
                                    etag304Ok = ((int)resp304.StatusCode == 304);
                                }
                            }
                            catch (WebException wex304)
                            {
                                HttpWebResponse r304 = wex304.Response as HttpWebResponse;
                                if (r304 != null && (int)r304.StatusCode == 304) etag304Ok = true;
                            }
                        }

                        bool notFoundOk = false;
                        try
                        {
                            wc.DownloadString(baseUrl + "/nao_existe_404.png");
                        }
                        catch (WebException wex)
                        {
                            HttpWebResponse resp = wex.Response as HttpWebResponse;
                            if (resp != null && (int)resp.StatusCode == 404) notFoundOk = true;
                        }

                        bool allOk = validDb && hapOk && transOk && iconOk && crestOk && apisOk && gzipJsOk && etag304Ok && notFoundOk;
                        string msg = string.Format(
                            "TEST_HEADLESS_OK={0} DB={1} HAPLO_TTS={2} TRANS={3} ICON={4} CREST={5} APIS={6} GZIP_JS={7} ETAG304={8} HTTP404={9} PORT={10} BYTES={11} FORMS={12} LEMMAS={13} SOURCE={14}",
                            allOk, validDb, hapOk, transOk, iconOk, crestOk, apisOk, gzipJsOk, etag304Ok, notFoundOk, server.Port, dbJson.Length, server.TotalForms, server.Lexicon.IndexedLemmasCount, server.ActiveSource
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
