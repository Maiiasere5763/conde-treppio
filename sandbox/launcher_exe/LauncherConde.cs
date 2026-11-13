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
using System.Runtime;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Speech.Synthesis;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

[assembly: AssemblyTitle("Codice Imperial da Lingua Treppia")]
[assembly: AssemblyDescription("Codice Treppio - Dicionario, Gramatica, Pronuncia IPA e Tradutor Bilingue")]
[assembly: AssemblyCompany("Chancelaria Imperial de Treppenia")]
[assembly: AssemblyProduct("Codice Imperial Treppio")]
[assembly: AssemblyVersion("10.0.0.0")]

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

        private struct LemmaRecord
        {
            public int TreppioLoc;
            public int TreppioLen;
            public int AltTreppioLoc;
            public int AltTreppioLen;
            public int PtLoc;
            public int PtLen;
            public int PtNormLoc;
            public int PtNormLen;
            public int PtHeadLen;
            public int ClassLoc;
            public int ClassLen;
            public int DetailLoc;
            public int DetailLen;
            public int Boost;
        }

        private sealed class PagedIntArray
        {
            private const int PageSize = 16384; // 64 KB (< 85 KB LOH threshold)
            private const int PageShift = 14;
            private const int PageMask = 0x3FFF;
            private readonly List<int[]> _pages = new List<int[]>();
            private int _count;

            public int Count { get { return _count; } }

            public PagedIntArray() { }

            public PagedIntArray(int fixedSize)
            {
                InitZero(fixedSize);
            }

            public void InitZero(int fixedSize)
            {
                _pages.Clear();
                int numPages = (fixedSize + PageMask) >> PageShift;
                for (int i = 0; i < numPages; i++)
                {
                    _pages.Add(new int[PageSize]);
                }
                _count = fixedSize;
            }

            public int this[int index]
            {
                get { return _pages[index >> PageShift][index & PageMask]; }
                set { _pages[index >> PageShift][index & PageMask] = value; }
            }

            public int Add(int value)
            {
                int idx = _count;
                int pageIdx = idx >> PageShift;
                if (pageIdx >= _pages.Count)
                {
                    _pages.Add(new int[PageSize]);
                }
                _pages[pageIdx][idx & PageMask] = value;
                _count = idx + 1;
                return idx;
            }
        }

        private sealed class PagedByteArena
        {
            private const int BlockSize = 65536; // 64 KB (< 85 KB LOH threshold)
            private readonly List<byte[]> _blocks = new List<byte[]>();
            private int _curBlock = -1;
            private int _curOff = BlockSize;

            public int AppendRaw(byte[] src, int srcOff, int len)
            {
                if (src == null || len <= 0) return -1;
                if (_curBlock < 0 || len > BlockSize - _curOff)
                {
                    byte[] nb = new byte[len > BlockSize ? len : BlockSize];
                    _blocks.Add(nb);
                    _curBlock = _blocks.Count - 1;
                    _curOff = 0;
                }
                int loc = (_curBlock << 16) | _curOff;
                Buffer.BlockCopy(src, srcOff, _blocks[_curBlock], _curOff, len);
                _curOff = (len > BlockSize) ? BlockSize : (_curOff + len);
                return loc;
            }

            public int AppendLenPrefixed(byte[] src, int srcOff, int len, out int storedLen)
            {
                storedLen = 0;
                if (src == null || len <= 0) return -1;
                int safeLen = len > 254 ? 254 : len;
                int need = safeLen + 1;
                if (_curBlock < 0 || need > BlockSize - _curOff)
                {
                    _blocks.Add(new byte[BlockSize]);
                    _curBlock = _blocks.Count - 1;
                    _curOff = 0;
                }
                int loc = (_curBlock << 16) | _curOff;
                byte[] blk = _blocks[_curBlock];
                blk[_curOff] = (byte)safeLen;
                Buffer.BlockCopy(src, srcOff, blk, _curOff + 1, safeLen);
                _curOff += need;
                storedLen = safeLen;
                return loc;
            }

            public string Decode(int loc, int len)
            {
                if (loc < 0 || len <= 0) return "";
                return Encoding.UTF8.GetString(_blocks[loc >> 16], loc & 0xFFFF, len);
            }

            public void GetSlice(int loc, out byte[] block, out int offset)
            {
                block = _blocks[loc >> 16];
                offset = loc & 0xFFFF;
            }

            public bool RawEquals(int loc, int locLen, byte[] other, int off, int len)
            {
                if (locLen != len) return false;
                byte[] blk = _blocks[loc >> 16];
                int p = loc & 0xFFFF;
                for (int i = 0; i < len; i++)
                {
                    if (blk[p + i] != other[off + i]) return false;
                }
                return true;
            }

            public bool KeyEquals(int loc, byte[] q, int qOff, int qLen)
            {
                byte[] blk = _blocks[loc >> 16];
                int p = loc & 0xFFFF;
                if (blk[p] != qLen) return false;
                p++;
                for (int i = 0; i < qLen; i++)
                {
                    if (blk[p + i] != q[qOff + i]) return false;
                }
                return true;
            }

            public uint HashFormAt(int loc)
            {
                byte[] blk = _blocks[loc >> 16];
                int p = loc & 0xFFFF;
                return ComputeFnv1a(blk, p + 1, blk[p]);
            }
        }

        private static uint ComputeFnv1a(byte[] b, int off, int len)
        {
            uint h = 2166136261u;
            int end = off + len;
            for (int i = off; i < end; i++)
            {
                h ^= b[i];
                h *= 16777619u;
            }
            return h;
        }

        private sealed class LexiconSnapshot
        {
            public readonly PagedByteArena TextArena = new PagedByteArena();
            public readonly PagedByteArena FormArena = new PagedByteArena();
            public readonly List<LemmaRecord> Lemmas = new List<LemmaRecord>();

            public readonly Dictionary<string, int> PtTokenHead = new Dictionary<string, int>(StringComparer.Ordinal);
            public readonly Dictionary<string, int> PtStemHead = new Dictionary<string, int>(StringComparer.Ordinal);
            public readonly PagedIntArray PtPostLemma = new PagedIntArray();
            public readonly PagedIntArray PtPostNext = new PagedIntArray();

            public PagedIntArray TrBucketHead = new PagedIntArray(1024);
            public int TrBucketMask = 1023;
            public readonly PagedIntArray TrKeyNext = new PagedIntArray();
            public readonly PagedIntArray TrKeyFormLoc = new PagedIntArray();
            public readonly PagedIntArray TrKeyHitHeadAndCount = new PagedIntArray(); // bits 28..31 = count (0..8), bits 0..27 = hitId + 1
            public int TrUniqueKeysCount;

            public readonly PagedIntArray HitLemmaAndAlt = new PagedIntArray(); // bit 31 = useAltTreppio, bits 0..30 = lemmaIdx
            public readonly PagedIntArray HitDetailLoc = new PagedIntArray();
            public readonly PagedIntArray HitDetailLen = new PagedIntArray();
            public readonly PagedIntArray HitNext = new PagedIntArray(); // hitId + 1

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

        private struct TempPostList
        {
            public int Head;
            public int Tail;
        }

        private sealed class Utf8StringPool
        {
            private readonly PagedByteArena _arena;
            private int[] _buckets;
            private int[] _next;
            private int[] _locs;
            private int[] _lens;
            private int _count;

            public Utf8StringPool(PagedByteArena arena)
            {
                _arena = arena;
                _buckets = new int[4096];
                _next = new int[4096];
                _locs = new int[4096];
                _lens = new int[4096];
            }

            public void InternBytes(byte[] src, int off, int len, out int outLoc, out int outLen)
            {
                if (src == null || len <= 0)
                {
                    outLoc = -1;
                    outLen = 0;
                    return;
                }
                uint h = ComputeFnv1a(src, off, len);
                int mask = _buckets.Length - 1;
                int b = (int)(h & (uint)mask);
                int cur = _buckets[b];
                while (cur != 0)
                {
                    int idx = cur - 1;
                    if (_arena.RawEquals(_locs[idx], _lens[idx], src, off, len))
                    {
                        outLoc = _locs[idx];
                        outLen = _lens[idx];
                        return;
                    }
                    cur = _next[idx];
                }

                if (_count >= _next.Length)
                {
                    int newCap = _next.Length << 1;
                    Array.Resize(ref _next, newCap);
                    Array.Resize(ref _locs, newCap);
                    Array.Resize(ref _lens, newCap);
                }
                if (_count * 10 > _buckets.Length * 7)
                {
                    int newBuckCap = _buckets.Length << 1;
                    int[] nb = new int[newBuckCap];
                    int nMask = newBuckCap - 1;
                    for (int i = 0; i < _count; i++)
                    {
                        byte[] blk;
                        int p;
                        _arena.GetSlice(_locs[i], out blk, out p);
                        uint ih = ComputeFnv1a(blk, p, _lens[i]);
                        int ib = (int)(ih & (uint)nMask);
                        _next[i] = nb[ib];
                        nb[ib] = i + 1;
                    }
                    _buckets = nb;
                    mask = nMask;
                    b = (int)(h & (uint)mask);
                }

                int loc = _arena.AppendRaw(src, off, len);
                int id = _count++;
                _locs[id] = loc;
                _lens[id] = len;
                _next[id] = _buckets[b];
                _buckets[b] = id + 1;
                outLoc = loc;
                outLen = len;
            }

            public void InternString(string s, ref byte[] scratch, out int outLoc, out int outLen)
            {
                if (string.IsNullOrEmpty(s))
                {
                    outLoc = -1;
                    outLen = 0;
                    return;
                }
                int maxBytes = Encoding.UTF8.GetMaxByteCount(s.Length);
                if (scratch == null || scratch.Length < maxBytes) scratch = new byte[Math.Max(256, maxBytes)];
                int len = Encoding.UTF8.GetBytes(s, 0, s.Length, scratch, 0);
                InternBytes(scratch, 0, len, out outLoc, out outLen);
            }
        }

        private static void IndexPtPost(
            LexiconSnapshot snap,
            Dictionary<string, TempPostList> buildMap,
            Dictionary<string, int> headMap,
            string key,
            int lemmaIdx)
        {
            if (string.IsNullOrEmpty(key)) return;
            TempPostList lst;
            if (!buildMap.TryGetValue(key, out lst))
            {
                int pid = snap.PtPostLemma.Add(lemmaIdx);
                snap.PtPostNext.Add(0);
                int pPlus1 = pid + 1;
                lst.Head = pPlus1;
                lst.Tail = pPlus1;
                buildMap[key] = lst;
                headMap[key] = pPlus1;
                return;
            }
            int tailIdx = lst.Tail - 1;
            if (snap.PtPostLemma[tailIdx] != lemmaIdx)
            {
                int pid = snap.PtPostLemma.Add(lemmaIdx);
                snap.PtPostNext.Add(0);
                int pPlus1 = pid + 1;
                snap.PtPostNext[tailIdx] = pPlus1;
                lst.Tail = pPlus1;
                buildMap[key] = lst;
            }
        }

        private static int AddPtEntry(
            LexiconSnapshot snap,
            Utf8StringPool pool,
            Dictionary<string, TempPostList> buildTokenMap,
            Dictionary<string, TempPostList> buildStemMap,
            ref byte[] scratch,
            string treppio,
            string altTreppio,
            string ptMeaning,
            string classTag,
            string detail,
            int boost)
        {
            if (string.IsNullOrEmpty(treppio) || string.IsNullOrEmpty(ptMeaning)) return -1;
            string norm = StripAccents(ptMeaning).Trim();
            int sepIdx = norm.IndexOfAny(new char[] { ',', ';', '(' });
            string head = (sepIdx >= 0 ? norm.Substring(0, sepIdx) : norm).Trim();

            int trLoc, trLen, altLoc, altLen, ptLoc, ptLen, normLoc, normLen, clLoc, clLen, dtLoc, dtLen;
            pool.InternString(treppio, ref scratch, out trLoc, out trLen);
            if (string.IsNullOrEmpty(altTreppio) || altTreppio == treppio)
            {
                altLoc = trLoc;
                altLen = trLen;
            }
            else
            {
                pool.InternString(altTreppio, ref scratch, out altLoc, out altLen);
            }
            pool.InternString(ptMeaning, ref scratch, out ptLoc, out ptLen);
            pool.InternString(norm, ref scratch, out normLoc, out normLen);
            int headByteLen = string.IsNullOrEmpty(head) ? 0 : Encoding.UTF8.GetByteCount(head);
            if (headByteLen > normLen) headByteLen = normLen;

            pool.InternString(classTag, ref scratch, out clLoc, out clLen);
            pool.InternString(detail ?? "", ref scratch, out dtLoc, out dtLen);

            int idx = snap.Lemmas.Count;
            snap.Lemmas.Add(new LemmaRecord
            {
                TreppioLoc = trLoc,
                TreppioLen = trLen,
                AltTreppioLoc = altLoc,
                AltTreppioLen = altLen,
                PtLoc = ptLoc,
                PtLen = ptLen,
                PtNormLoc = normLoc,
                PtNormLen = normLen,
                PtHeadLen = headByteLen,
                ClassLoc = clLoc,
                ClassLen = clLen,
                DetailLoc = dtLoc,
                DetailLen = dtLen,
                Boost = boost
            });

            IndexPtPost(snap, buildTokenMap, snap.PtTokenHead, norm, idx);
            if (!string.IsNullOrEmpty(head)) IndexPtPost(snap, buildTokenMap, snap.PtTokenHead, head, idx);

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
                    string w = norm.Substring(start, i - start);
                    IndexPtPost(snap, buildTokenMap, snap.PtTokenHead, w, idx);
                    if (w.Length >= 3) IndexPtPost(snap, buildStemMap, snap.PtStemHead, w.Substring(0, 3), idx);
                    start = -1;
                }
            }
            if (start >= 0)
            {
                string w = norm.Substring(start);
                IndexPtPost(snap, buildTokenMap, snap.PtTokenHead, w, idx);
                if (w.Length >= 3) IndexPtPost(snap, buildStemMap, snap.PtStemHead, w.Substring(0, 3), idx);
            }
            return idx;
        }

        private static int NormalizeFormKeyUtf8(byte[] src, int srcOff, int srcLen, ref byte[] dst)
        {
            if (src == null || srcLen <= 0) return 0;
            if (dst == null || dst.Length < srcLen + 16) dst = new byte[Math.Max(256, srcLen + 32)];
            int s = srcOff;
            int e = srcOff + srcLen;
            while (s < e && (src[s] <= 0x20 || src[s] == (byte)'!' || src[s] == (byte)'?')) s++;
            while (e > s && (src[e - 1] <= 0x20 || src[e - 1] == (byte)'!' || src[e - 1] == (byte)'?')) e--;
            if (s >= e) return 0;

            int o = 0;
            for (int i = s; i < e; i++)
            {
                byte b = src[i];
                if (b == (byte)'!' || b == (byte)'?') continue;
                if (b >= (byte)'A' && b <= (byte)'Z')
                {
                    dst[o++] = (byte)(b + 32);
                }
                else if (b < 0x80)
                {
                    dst[o++] = b;
                }
                else if (b == 0xC3 && i + 1 < e)
                {
                    byte b2 = src[i + 1];
                    dst[o++] = 0xC3;
                    if (b2 >= 0x80 && b2 <= 0x9E && b2 != 0x97) dst[o++] = (byte)(b2 + 0x20);
                    else dst[o++] = b2;
                    i++;
                }
                else
                {
                    // Rare non-Latin-1 multibyte char: fallback to full Unicode lowercasing
                    string cleaned = Encoding.UTF8.GetString(src, s, e - s).Replace("!", "").Replace("?", "").Trim().ToLowerInvariant();
                    if (string.IsNullOrEmpty(cleaned)) return 0;
                    int need = Encoding.UTF8.GetMaxByteCount(cleaned.Length);
                    if (dst.Length < need) dst = new byte[need];
                    o = Encoding.UTF8.GetBytes(cleaned, 0, cleaned.Length, dst, 0);
                    return o > 254 ? 254 : o;
                }
            }
            while (o > 0 && dst[o - 1] <= 0x20) o--;
            return o > 254 ? 254 : o;
        }

        private static void RehashTrBuckets(LexiconSnapshot snap)
        {
            int newCap = (snap.TrBucketMask + 1) << 1;
            int newMask = newCap - 1;
            PagedIntArray nextBuckets = new PagedIntArray(newCap);
            for (int k = 0; k < snap.TrUniqueKeysCount; k++)
            {
                uint h = snap.FormArena.HashFormAt(snap.TrKeyFormLoc[k]);
                int b = (int)(h & (uint)newMask);
                snap.TrKeyNext[k] = nextBuckets[b];
                nextBuckets[b] = k + 1;
            }
            snap.TrBucketHead = nextBuckets;
            snap.TrBucketMask = newMask;
        }

        private static void AddTrFormBytes(
            LexiconSnapshot snap,
            PagedIntArray keyHitTail,
            ref int revCount,
            ref byte[] normBuf,
            byte[] formBytes,
            int formOff,
            int formLen,
            int lemmaIdx,
            bool useAlt,
            int detailLoc,
            int detailLen)
        {
            if (lemmaIdx < 0 || formBytes == null || formLen <= 0) return;
            int nLen = NormalizeFormKeyUtf8(formBytes, formOff, formLen, ref normBuf);
            if (nLen <= 0) return;

            uint h = ComputeFnv1a(normBuf, 0, nLen);
            int bucket = (int)(h & (uint)snap.TrBucketMask);
            int cur = snap.TrBucketHead[bucket];
            int keyId = -1;
            while (cur != 0)
            {
                int k = cur - 1;
                if (snap.FormArena.KeyEquals(snap.TrKeyFormLoc[k], normBuf, 0, nLen))
                {
                    keyId = k;
                    break;
                }
                cur = snap.TrKeyNext[k];
            }

            if (keyId < 0)
            {
                if ((snap.TrUniqueKeysCount + 1) * 10 > (snap.TrBucketMask + 1) * 7)
                {
                    RehashTrBuckets(snap);
                    bucket = (int)(h & (uint)snap.TrBucketMask);
                }
                int storedLen;
                int formLoc = snap.FormArena.AppendLenPrefixed(normBuf, 0, nLen, out storedLen);
                keyId = snap.TrUniqueKeysCount++;
                snap.TrKeyFormLoc.Add(formLoc);
                snap.TrKeyHitHeadAndCount.Add(0);
                keyHitTail.Add(0);
                snap.TrKeyNext.Add(snap.TrBucketHead[bucket]);
                snap.TrBucketHead[bucket] = keyId + 1;
            }

            int headAndCnt = snap.TrKeyHitHeadAndCount[keyId];
            int cnt = (headAndCnt >> 28) & 0xF;
            if (cnt >= 8) return;

            int hitId = snap.HitLemmaAndAlt.Add((useAlt ? int.MinValue : 0) | (lemmaIdx & 0x7FFFFFFF));
            snap.HitDetailLoc.Add(detailLoc);
            snap.HitDetailLen.Add(detailLen);
            snap.HitNext.Add(0);

            int tailPlus1 = keyHitTail[keyId];
            if (tailPlus1 == 0)
            {
                snap.TrKeyHitHeadAndCount[keyId] = (1 << 28) | ((hitId + 1) & 0x0FFFFFFF);
            }
            else
            {
                snap.HitNext[tailPlus1 - 1] = hitId + 1;
                snap.TrKeyHitHeadAndCount[keyId] = ((cnt + 1) << 28) | (headAndCnt & 0x0FFFFFFF);
            }
            keyHitTail[keyId] = hitId + 1;
            revCount++;
        }

        private static void AddTrFormString(
            LexiconSnapshot snap,
            PagedIntArray keyHitTail,
            ref int revCount,
            ref byte[] scratch,
            ref byte[] normBuf,
            string formStr,
            int lemmaIdx,
            bool useAlt,
            int detailLoc,
            int detailLen)
        {
            if (string.IsNullOrEmpty(formStr)) return;
            int maxB = Encoding.UTF8.GetMaxByteCount(formStr.Length);
            if (scratch == null || scratch.Length < maxB) scratch = new byte[Math.Max(256, maxB)];
            int len = Encoding.UTF8.GetBytes(formStr, 0, formStr.Length, scratch, 0);
            AddTrFormBytes(snap, keyHitTail, ref revCount, ref normBuf, scratch, 0, len, lemmaIdx, useAlt, detailLoc, detailLen);
        }

        private sealed class Utf8JsonCursor
        {
            private readonly byte[] _b;
            private readonly int _len;
            public int Pos;
            private byte[] _scratch = new byte[4096];
            private char[] _charScratch = new char[256];

            public Utf8JsonCursor(byte[] jsonBytes)
            {
                _b = jsonBytes ?? new byte[0];
                _len = _b.Length;
                Pos = (_len >= 3 && _b[0] == 0xEF && _b[1] == 0xBB && _b[2] == 0xBF) ? 3 : 0;
            }

            public void SkipWs()
            {
                while (Pos < _len)
                {
                    byte c = _b[Pos];
                    if (c == (byte)' ' || c == (byte)'\t' || c == (byte)'\r' || c == (byte)'\n') Pos++;
                    else break;
                }
            }

            public char Peek()
            {
                SkipWs();
                return Pos < _len ? (char)_b[Pos] : '\0';
            }

            public bool TryConsume(byte expected)
            {
                SkipWs();
                if (Pos < _len && _b[Pos] == expected)
                {
                    Pos++;
                    return true;
                }
                return false;
            }

            public bool ReadStringSlice(out byte[] buf, out int start, out int len)
            {
                SkipWs();
                if (Pos >= _len || _b[Pos] != (byte)'"')
                {
                    buf = null;
                    start = 0;
                    len = 0;
                    return false;
                }
                Pos++;
                int s = Pos;
                bool hasEscape = false;
                while (Pos < _len)
                {
                    byte c = _b[Pos];
                    if (c == (byte)'"')
                    {
                        int end = Pos;
                        Pos++;
                        if (!hasEscape)
                        {
                            buf = _b;
                            start = s;
                            len = end - s;
                            return true;
                        }
                        len = UnescapeIntoScratch(s, end);
                        buf = _scratch;
                        start = 0;
                        return true;
                    }
                    if (c == (byte)'\\')
                    {
                        hasEscape = true;
                        Pos += 2;
                    }
                    else
                    {
                        Pos++;
                    }
                }
                buf = _b;
                start = s;
                len = _len - s;
                return true;
            }

            public string ReadString()
            {
                byte[] buf;
                int s, len;
                if (!ReadStringSlice(out buf, out s, out len)) return null;
                if (len == 0) return "";
                return Encoding.UTF8.GetString(buf, s, len);
            }

            private void EnsureScratch(int need)
            {
                if (_scratch.Length < need)
                {
                    int cap = _scratch.Length << 1;
                    while (cap < need) cap <<= 1;
                    Array.Resize(ref _scratch, cap);
                }
            }

            private void FlushChars(int charCount, ref int outLen)
            {
                if (charCount <= 0) return;
                EnsureScratch(outLen + Encoding.UTF8.GetMaxByteCount(charCount));
                outLen += Encoding.UTF8.GetBytes(_charScratch, 0, charCount, _scratch, outLen);
            }

            private static int ParseHex4(byte[] b, int p)
            {
                int val = 0;
                for (int i = 0; i < 4; i++)
                {
                    byte c = b[p + i];
                    int d;
                    if (c >= (byte)'0' && c <= (byte)'9') d = c - '0';
                    else if (c >= (byte)'a' && c <= (byte)'f') d = 10 + (c - 'a');
                    else if (c >= (byte)'A' && c <= (byte)'F') d = 10 + (c - 'A');
                    else return -1;
                    val = (val << 4) | d;
                }
                return val;
            }

            private int UnescapeIntoScratch(int s, int end)
            {
                EnsureScratch((end - s) + 8);
                int outLen = 0;
                int charLen = 0;
                for (int i = s; i < end; i++)
                {
                    byte c = _b[i];
                    if (c == (byte)'\\' && i + 1 < end)
                    {
                        byte n = _b[++i];
                        if (n == (byte)'u' && i + 4 < end)
                        {
                            int code = ParseHex4(_b, i + 1);
                            if (code >= 0)
                            {
                                if (charLen >= _charScratch.Length) Array.Resize(ref _charScratch, _charScratch.Length << 1);
                                _charScratch[charLen++] = (char)code;
                                i += 4;
                                continue;
                            }
                        }
                        if (charLen > 0)
                        {
                            FlushChars(charLen, ref outLen);
                            charLen = 0;
                        }
                        EnsureScratch(outLen + 4);
                        if (n == (byte)'"' || n == (byte)'\\' || n == (byte)'/') _scratch[outLen++] = n;
                        else if (n == (byte)'n') _scratch[outLen++] = (byte)'\n';
                        else if (n == (byte)'r') _scratch[outLen++] = (byte)'\r';
                        else if (n == (byte)'t') _scratch[outLen++] = (byte)'\t';
                        else if (n == (byte)'b') _scratch[outLen++] = (byte)'\b';
                        else if (n == (byte)'f') _scratch[outLen++] = (byte)'\f';
                        else _scratch[outLen++] = n;
                    }
                    else
                    {
                        if (charLen > 0)
                        {
                            FlushChars(charLen, ref outLen);
                            charLen = 0;
                        }
                        EnsureScratch(outLen + 4);
                        _scratch[outLen++] = c;
                    }
                }
                if (charLen > 0) FlushChars(charLen, ref outLen);
                return outLen;
            }

            public bool ReadScalarAsSlice(out byte[] buf, out int start, out int len)
            {
                SkipWs();
                if (Pos >= _len)
                {
                    buf = null;
                    start = 0;
                    len = 0;
                    return false;
                }
                byte c = _b[Pos];
                if (c == (byte)'"') return ReadStringSlice(out buf, out start, out len);
                if (c == (byte)'{' || c == (byte)'[')
                {
                    SkipValue();
                    buf = null;
                    start = 0;
                    len = 0;
                    return false;
                }
                int s = Pos;
                while (Pos < _len)
                {
                    byte ch = _b[Pos];
                    if (ch == (byte)',' || ch == (byte)'}' || ch == (byte)']' || ch <= 0x20) break;
                    Pos++;
                }
                int rawLen = Pos - s;
                if (rawLen == 4 && _b[s] == (byte)'n' && _b[s + 1] == (byte)'u' && _b[s + 2] == (byte)'l' && _b[s + 3] == (byte)'l')
                {
                    buf = null;
                    start = 0;
                    len = 0;
                    return false;
                }
                buf = _b;
                start = s;
                len = rawLen;
                return rawLen > 0;
            }

            public string ReadScalarAsString()
            {
                byte[] buf;
                int s, len;
                if (!ReadScalarAsSlice(out buf, out s, out len) || len == 0) return "";
                return Encoding.UTF8.GetString(buf, s, len);
            }

            private void SkipStringFast()
            {
                Pos++;
                while (Pos < _len)
                {
                    byte c = _b[Pos++];
                    if (c == (byte)'"') return;
                    if (c == (byte)'\\' && Pos < _len) Pos++;
                }
            }

            public void SkipValue()
            {
                SkipWs();
                if (Pos >= _len) return;
                byte c = _b[Pos];
                if (c == (byte)'"')
                {
                    SkipStringFast();
                    return;
                }
                if (c == (byte)'{' || c == (byte)'[')
                {
                    int depth = 0;
                    while (Pos < _len)
                    {
                        byte ch = _b[Pos];
                        if (ch == (byte)'"')
                        {
                            SkipStringFast();
                            continue;
                        }
                        if (ch == (byte)'{' || ch == (byte)'[') depth++;
                        else if (ch == (byte)'}' || ch == (byte)']')
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
                    byte ch = _b[Pos];
                    if (ch == (byte)',' || ch == (byte)'}' || ch == (byte)']') break;
                    Pos++;
                }
            }

            public void ForEachObjectPair(Action<string> onKey)
            {
                if (!TryConsume((byte)'{'))
                {
                    SkipValue();
                    return;
                }
                if (TryConsume((byte)'}')) return;
                while (Pos < _len)
                {
                    string key = ReadString();
                    if (key == null) break;
                    TryConsume((byte)':');
                    onKey(key);
                    if (TryConsume((byte)',')) continue;
                    TryConsume((byte)'}');
                    break;
                }
            }

            public void ForEachArrayItem(Action<int> onIndex)
            {
                if (!TryConsume((byte)'['))
                {
                    SkipValue();
                    return;
                }
                if (TryConsume((byte)']')) return;
                int idx = 0;
                while (Pos < _len)
                {
                    onIndex(idx++);
                    if (TryConsume((byte)',')) continue;
                    TryConsume((byte)']');
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

        private struct PendingVerbForm
        {
            public int BufOff;
            public int BufLen;
            public int DetailLoc;
            public int DetailLen;
            public bool UseInf;
        }

        private struct CachedLocLen
        {
            public int Loc;
            public int Len;
        }

        public void BuildFromJsonBytes(byte[] jsonBytes)
        {
            if (jsonBytes == null || jsonBytes.Length == 0) return;
            Utf8JsonCursor cur = new Utf8JsonCursor(jsonBytes);
            if (cur.Peek() != '{') return;

            LexiconSnapshot snap = new LexiconSnapshot();
            snap.TrBucketHead = new PagedIntArray(32768);
            snap.TrBucketMask = 32767;

            Utf8StringPool pool = new Utf8StringPool(snap.TextArena);
            PagedIntArray keyHitTail = new PagedIntArray();
            Dictionary<string, TempPostList> buildTokenMap = new Dictionary<string, TempPostList>(8192, StringComparer.Ordinal);
            Dictionary<string, TempPostList> buildStemMap = new Dictionary<string, TempPostList>(2048, StringComparer.Ordinal);
            Dictionary<string, CachedLocLen> detailCache = new Dictionary<string, CachedLocLen>(512, StringComparer.Ordinal);

            byte[] scratch = new byte[512];
            byte[] normBuf = new byte[512];
            byte[] verbBuf = new byte[16384];
            int verbBufUsed = 0;
            List<PendingVerbForm> pendingForms = new List<PendingVerbForm>(160);
            int revCount = 0;

            Func<string, CachedLocLen> getDetail = delegate(string detStr)
            {
                string key = detStr ?? "";
                CachedLocLen cached;
                if (detailCache.TryGetValue(key, out cached)) return cached;
                int dl, dlen;
                pool.InternString(key, ref scratch, out dl, out dlen);
                cached = new CachedLocLen { Loc = dl, Len = dlen };
                detailCache[key] = cached;
                return cached;
            };

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
                AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, funcWords[i, 1], null, funcWords[i, 0], funcWords[i, 2], funcWords[i, 3], 45);
            }

            string[] persons = new string[] { "1ª Sg (-m)", "2ª Sg (-s)", "3ª Sg/Pl", "1ª Pl (-n)", "2ª Pl (-t)" };
            CachedLocLen detInvar = getDetail("Invariável");
            CachedLocLen detInf = getDetail("Infinitivo");
            CachedLocLen detImp = getDetail("Imperativo");
            CachedLocLen detInterr = getDetail("Interrogativo 2ª Pl");

            cur.ForEachObjectPair(topKey =>
            {
                if (topKey == "gnlt")
                {
                    // Pula capítulo textual GNLT sem alocar dicionários nem strings
                    cur.SkipValue();
                }
                else if (topKey == "substantivos")
                {
                    List<string> formasVal = new List<string>(24);
                    List<string> formasKey = new List<string>(24);
                    cur.ForEachObjectPair(lemma =>
                    {
                        string decl = "", sig = "", etym = "";
                        formasVal.Clear();
                        formasKey.Clear();
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
                        int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, lemma, null, sig, cTag, etym, 10);
                        for (int i = 0; i < formasVal.Count; i++)
                        {
                            CachedLocLen dl = getDetail(formasKey[i]);
                            AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, formasVal[i], lIdx, false, dl.Loc, dl.Len);
                        }
                    });
                }
                else if (topKey == "adjetivos")
                {
                    List<string> fKeys = new List<string>(16);
                    List<string> fVals = new List<string>(16);
                    cur.ForEachObjectPair(adj =>
                    {
                        string sig = "", comp = "";
                        fKeys.Clear();
                        fVals.Clear();
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
                        int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, adj, null, sig, "Adjetivo", "Comp: " + comp, 8);
                        for (int i = 0; i < fVals.Count; i++)
                        {
                            CachedLocLen dl = getDetail(fKeys[i]);
                            AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, fVals[i], lIdx, false, dl.Loc, dl.Len);
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
                        int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, adv, null, sig, "Advérbio (" + subc + ")", etym, 6);
                        CachedLocLen dl = getDetail(subc);
                        AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, adv, lIdx, false, dl.Loc, dl.Len);
                    });
                }
                else if (topKey == "pronomes")
                {
                    List<string> cKeys = new List<string>(10);
                    List<string> cVals = new List<string>(10);
                    cur.ForEachObjectPair(pKey =>
                    {
                        string esfera = "", nomRaw = "";
                        bool hasEsfera = false;
                        cKeys.Clear();
                        cVals.Clear();
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
                        int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, string.IsNullOrEmpty(nomClean) ? pKey : nomClean, pKey, desc, "Pronome", "", 15);
                        for (int i = 0; i < cVals.Count; i++)
                        {
                            CachedLocLen dl = getDetail(cKeys[i]);
                            string[] parts = cVals[i].Split('/');
                            for (int p = 0; p < parts.Length; p++)
                            {
                                string tok = StripParenTrim(parts[p]);
                                AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, tok, lIdx, true, dl.Loc, dl.Len);
                            }
                        }
                    });
                }
                else if (topKey == "numerais")
                {
                    List<string> nKeys = new List<string>(10);
                    List<string> nVals = new List<string>(10);
                    cur.ForEachObjectPair(numK =>
                    {
                        string card = "", ordRaw = "", comp = "";
                        nKeys.Clear();
                        nVals.Clear();
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
                        int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, card + " / " + ord, card, desc, "Numeral", comp, 14);
                        for (int i = 0; i < nVals.Count; i++)
                        {
                            CachedLocLen dl = getDetail(numK + " (" + nKeys[i] + ")");
                            string[] parts = nVals[i].Split('/');
                            for (int p = 0; p < parts.Length; p++)
                            {
                                string tok = StripParenTrim(parts[p]);
                                AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, tok, lIdx, true, dl.Loc, dl.Len);
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
                        int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, pTok, null, desc, cls, "", 18);
                        string[] toks = pTok.Split('/');
                        for (int i = 0; i < toks.Length; i++)
                        {
                            string t = StripParenTrim(toks[i]);
                            if (!string.IsNullOrEmpty(t) && !t.StartsWith("-") && !t.EndsWith("-"))
                            {
                                AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, t, lIdx, false, detInvar.Loc, detInvar.Len);
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
                        int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, dTok + " -> " + eq, dTok, analise, est, eq, 2);
                        CachedLocLen dl = getDetail(eq);
                        string[] toks = dTok.Split('/');
                        for (int i = 0; i < toks.Length; i++)
                        {
                            AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, toks[i].Trim(), lIdx, true, dl.Loc, dl.Len);
                        }
                    });
                }
                else if (topKey == "verbos_quadripartite")
                {
                    cur.ForEachObjectPair(vRoot =>
                    {
                        string rootDash = vRoot + "-";
                        cur.ForEachObjectPair(axKey =>
                        {
                            string mean = "", inf = "", imp = "", interr = "";
                            string cat = "Verbo [" + axKey + "]";
                            pendingForms.Clear();
                            verbBufUsed = 0;

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
                                                byte[] fBuf;
                                                int fOff, fLen;
                                                if (cur.ReadScalarAsSlice(out fBuf, out fOff, out fLen) && fLen > 0)
                                                {
                                                    string pLbl = pIdx < persons.Length ? persons[pIdx] : "";
                                                    CachedLocLen dl = getDetail(ck + " " + pLbl);
                                                    if (verbBufUsed + fLen > verbBuf.Length)
                                                    {
                                                        Array.Resize(ref verbBuf, Math.Max(verbBuf.Length << 1, verbBufUsed + fLen));
                                                    }
                                                    Buffer.BlockCopy(fBuf, fOff, verbBuf, verbBufUsed, fLen);
                                                    pendingForms.Add(new PendingVerbForm
                                                    {
                                                        BufOff = verbBufUsed,
                                                        BufLen = fLen,
                                                        DetailLoc = dl.Loc,
                                                        DetailLen = dl.Len,
                                                        UseInf = (pendingForms.Count < 120)
                                                    });
                                                    verbBufUsed += fLen;
                                                }
                                            });
                                        }
                                        else if (nxt == '{')
                                        {
                                            cur.ForEachObjectPair(sdk =>
                                            {
                                                byte[] fBuf;
                                                int fOff, fLen;
                                                if (cur.ReadScalarAsSlice(out fBuf, out fOff, out fLen) && fLen > 0)
                                                {
                                                    CachedLocLen dl = getDetail(ck + ": " + sdk);
                                                    if (verbBufUsed + fLen > verbBuf.Length)
                                                    {
                                                        Array.Resize(ref verbBuf, Math.Max(verbBuf.Length << 1, verbBufUsed + fLen));
                                                    }
                                                    Buffer.BlockCopy(fBuf, fOff, verbBuf, verbBufUsed, fLen);
                                                    pendingForms.Add(new PendingVerbForm
                                                    {
                                                        BufOff = verbBufUsed,
                                                        BufLen = fLen,
                                                        DetailLoc = dl.Loc,
                                                        DetailLen = dl.Len,
                                                        UseInf = false
                                                    });
                                                    verbBufUsed += fLen;
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

                            int lIdx = AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, inf, rootDash, mean, cat, "Raiz " + vRoot + "- | Imp: " + imp, axKey.StartsWith("1.") ? 12 : 4);
                            AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, inf, lIdx, true, detInf.Loc, detInf.Len);
                            AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, imp, lIdx, true, detImp.Loc, detImp.Len);
                            AddTrFormString(snap, keyHitTail, ref revCount, ref scratch, ref normBuf, interr, lIdx, true, detInterr.Loc, detInterr.Len);

                            for (int f = 0; f < pendingForms.Count; f++)
                            {
                                PendingVerbForm pf = pendingForms[f];
                                AddTrFormBytes(snap, keyHitTail, ref revCount, ref normBuf, verbBuf, pf.BufOff, pf.BufLen, lIdx, !pf.UseInf, pf.DetailLoc, pf.DetailLen);
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
                            AddPtEntry(snap, pool, buildTokenMap, buildStemMap, ref scratch, tr, null, pt, "Corpus Canônico", tit, 5);
                        }
                    });
                }
                else
                {
                    cur.SkipValue();
                }
            });

            snap.Lemmas.TrimExcess();
            snap.IndexedFormsCount = revCount;
            snap.IndexedLemmasCount = snap.Lemmas.Count;
            snap.Generation = Interlocked.Increment(ref _generationSeq);
            snap.IsReady = true;
            _snap = snap;

            // Limpa arrays temporarios de indexacao / LOH imediatamente apos trocar snapshot
            pool = null;
            keyHitTail = null;
            buildTokenMap = null;
            buildStemMap = null;
            detailCache = null;
            try
            {
                GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce;
                GC.Collect(2, GCCollectionMode.Forced, true, true);
            }
            catch { }
        }

        private struct ScoredIdx
        {
            public int Score;
            public int LemmaIdx;
        }

        private static LexEntry MaterializeLemma(LexiconSnapshot snap, int lemmaIdx, bool useAltTreppio, int overrideDetailLoc, int overrideDetailLen, bool includeNorm)
        {
            LemmaRecord r = snap.Lemmas[lemmaIdx];
            string tr = useAltTreppio
                ? snap.TextArena.Decode(r.AltTreppioLoc, r.AltTreppioLen)
                : snap.TextArena.Decode(r.TreppioLoc, r.TreppioLen);
            string det = (overrideDetailLoc >= 0 && overrideDetailLen > 0)
                ? snap.TextArena.Decode(overrideDetailLoc, overrideDetailLen)
                : snap.TextArena.Decode(r.DetailLoc, r.DetailLen);
            return new LexEntry
            {
                Treppio = tr,
                PtMeaning = snap.TextArena.Decode(r.PtLoc, r.PtLen),
                PtNorm = includeNorm ? snap.TextArena.Decode(r.PtNormLoc, r.PtNormLen) : "",
                ClassTag = snap.TextArena.Decode(r.ClassLoc, r.ClassLen),
                Detail = det,
                Boost = r.Boost
            };
        }

        private static bool BytesEqual(byte[] a, int aOff, byte[] b, int len)
        {
            for (int i = 0; i < len; i++)
            {
                if (a[aOff + i] != b[i]) return false;
            }
            return true;
        }

        private static bool ContainsBytes(byte[] hay, int hayOff, int hayLen, byte[] needle)
        {
            int nLen = needle.Length;
            if (nLen == 0) return true;
            if (nLen > hayLen) return false;
            int limit = hayOff + hayLen - nLen;
            byte first = needle[0];
            for (int i = hayOff; i <= limit; i++)
            {
                if (hay[i] == first)
                {
                    bool eq = true;
                    for (int j = 1; j < nLen; j++)
                    {
                        if (hay[i + j] != needle[j]) { eq = false; break; }
                    }
                    if (eq) return true;
                }
            }
            return false;
        }

        private static int ScorePtRecord(LexiconSnapshot snap, LemmaRecord rec, byte[] qBytes, byte[] qStemBytes)
        {
            if (rec.PtNormLoc < 0 || rec.PtNormLen <= 0) return 0;
            byte[] blk;
            int normOff;
            snap.TextArena.GetSlice(rec.PtNormLoc, out blk, out normOff);
            int normLen = rec.PtNormLen;
            int qLen = qBytes.Length;

            if (normLen == qLen && BytesEqual(blk, normOff, qBytes, qLen)) return 140;
            if (rec.PtHeadLen == qLen && BytesEqual(blk, normOff, qBytes, qLen)) return 128;

            bool headWordExact = false;
            bool anyWordExact = false;
            bool stemMatch = false;
            int totalWords = 0;
            int headEnd = normOff + rec.PtHeadLen;
            int normEnd = normOff + normLen;
            int wStart = -1;

            for (int i = normOff; i <= normEnd; i++)
            {
                bool isAlnum = false;
                if (i < normEnd)
                {
                    byte b = blk[i];
                    isAlnum = (b >= (byte)'a' && b <= (byte)'z') || (b >= (byte)'0' && b <= (byte)'9');
                }
                if (isAlnum)
                {
                    if (wStart < 0) wStart = i;
                }
                else if (wStart >= 0)
                {
                    totalWords++;
                    int wLen = i - wStart;
                    if (wLen == qLen && BytesEqual(blk, wStart, qBytes, qLen))
                    {
                        anyWordExact = true;
                        if (wStart < headEnd) headWordExact = true;
                    }
                    if (!stemMatch && qStemBytes.Length >= 3 && wLen >= qStemBytes.Length && BytesEqual(blk, wStart, qStemBytes, qStemBytes.Length))
                    {
                        stemMatch = true;
                    }
                    wStart = -1;
                }
            }

            if (headWordExact) return 105 - Math.Min(20, totalWords);
            if (anyWordExact) return 85 - Math.Min(25, totalWords * 2);
            if (stemMatch) return 62 - Math.Min(20, totalWords);
            if (qLen >= 3 && ContainsBytes(blk, normOff, normLen, qBytes)) return 40;
            return 0;
        }

        private static void CollectPtCandidates(LexiconSnapshot snap, Dictionary<string, int> headMap, string key, HashSet<int> candidateIdx)
        {
            int postPlus1;
            if (string.IsNullOrEmpty(key) || !headMap.TryGetValue(key, out postPlus1)) return;
            while (postPlus1 != 0)
            {
                int pid = postPlus1 - 1;
                candidateIdx.Add(snap.PtPostLemma[pid]);
                postPlus1 = snap.PtPostNext[pid];
            }
        }

        public List<LexEntry> SearchPtToken(string ptToken, int limit)
        {
            LexiconSnapshot snap = _snap;
            string q = StripAccents(ptToken).Trim();
            List<LexEntry> outList = new List<LexEntry>();
            if (string.IsNullOrEmpty(q) || snap.Lemmas.Count == 0) return outList;

            string qStem = ComputePtStem(q);
            byte[] qBytes = Encoding.UTF8.GetBytes(q);
            byte[] qStemBytes = qStem == q ? qBytes : Encoding.UTF8.GetBytes(qStem);

            List<ScoredIdx> scored = new List<ScoredIdx>(32);
            HashSet<int> candidateIdx = new HashSet<int>();

            CollectPtCandidates(snap, snap.PtTokenHead, q, candidateIdx);
            if (!string.IsNullOrEmpty(qStem) && qStem != q)
            {
                CollectPtCandidates(snap, snap.PtTokenHead, qStem, candidateIdx);
            }
            if (qStem.Length >= 3)
            {
                CollectPtCandidates(snap, snap.PtStemHead, qStem.Substring(0, 3), candidateIdx);
            }

            if (candidateIdx.Count > 0)
            {
                foreach (int idx in candidateIdx)
                {
                    LemmaRecord rec = snap.Lemmas[idx];
                    int sc = ScorePtRecord(snap, rec, qBytes, qStemBytes);
                    if (sc > 0) scored.Add(new ScoredIdx { Score = sc + rec.Boost, LemmaIdx = idx });
                }
            }

            // Fallback de substring caso nenhum token exato/radical tenha atingido o limite
            if (scored.Count < limit && qBytes.Length >= 3)
            {
                List<LemmaRecord> all = snap.Lemmas;
                for (int i = 0; i < all.Count; i++)
                {
                    if (candidateIdx.Contains(i)) continue;
                    LemmaRecord rec = all[i];
                    if (rec.PtNormLoc >= 0 && rec.PtNormLen >= qBytes.Length)
                    {
                        byte[] blk;
                        int off;
                        snap.TextArena.GetSlice(rec.PtNormLoc, out blk, out off);
                        if (ContainsBytes(blk, off, rec.PtNormLen, qBytes))
                        {
                            scored.Add(new ScoredIdx { Score = 40 + rec.Boost, LemmaIdx = i });
                        }
                    }
                }
            }

            scored.Sort((a, b) => b.Score.CompareTo(a.Score));
            HashSet<string> seen = new HashSet<string>(StringComparer.Ordinal);
            for (int i = 0; i < scored.Count && outList.Count < limit; i++)
            {
                LexEntry e = MaterializeLemma(snap, scored[i].LemmaIdx, false, -1, 0, true);
                string key = e.Treppio + "|" + e.ClassTag;
                if (seen.Add(key)) outList.Add(e);
            }
            return outList;
        }

        private static bool LookupTrReverse(LexiconSnapshot snap, string formRaw, int maxHits, List<LexEntry> dest)
        {
            dest.Clear();
            if (string.IsNullOrEmpty(formRaw) || snap.TrUniqueKeysCount == 0) return false;
            byte[] src = Encoding.UTF8.GetBytes(formRaw);
            byte[] normBuf = null;
            int nLen = NormalizeFormKeyUtf8(src, 0, src.Length, ref normBuf);
            if (nLen <= 0) return false;

            uint h = ComputeFnv1a(normBuf, 0, nLen);
            int bucket = (int)(h & (uint)snap.TrBucketMask);
            int cur = snap.TrBucketHead[bucket];
            while (cur != 0)
            {
                int keyId = cur - 1;
                if (snap.FormArena.KeyEquals(snap.TrKeyFormLoc[keyId], normBuf, 0, nLen))
                {
                    int headAndCnt = snap.TrKeyHitHeadAndCount[keyId];
                    int hitPlus1 = headAndCnt & 0x0FFFFFFF;
                    while (hitPlus1 != 0 && dest.Count < maxHits)
                    {
                        int hitId = hitPlus1 - 1;
                        int packed = snap.HitLemmaAndAlt[hitId];
                        bool useAlt = (packed & int.MinValue) != 0;
                        int lemmaIdx = packed & 0x7FFFFFFF;
                        int dLoc = snap.HitDetailLoc[hitId];
                        int dLen = snap.HitDetailLen[hitId];
                        dest.Add(MaterializeLemma(snap, lemmaIdx, useAlt, dLoc, dLen, false));
                        hitPlus1 = snap.HitNext[hitId];
                    }
                    return dest.Count > 0;
                }
                cur = snap.TrKeyNext[keyId];
            }
            return false;
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
            sb.AppendLine("EQUIVALENTE EM TRÉPPIO");
            sb.AppendLine("Tréppio: " + primaryTreppio);
            if (ipa != null) sb.AppendLine("IPA: " + ipa.Ipa);
            sb.AppendLine();
            sb.AppendLine("VERBETES CORRESPONDENTES");
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

            Dictionary<string, string> corpSnap = snap.CorpusByTreppio;

            StringBuilder sb = new StringBuilder();
            foreach (KeyValuePair<string, string> ckv in corpSnap)
            {
                if (ckv.Key.IndexOf(qRaw, StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    sb.AppendLine("PASSAGEM DO CORPUS");
                    sb.AppendLine(ckv.Value);
                    sb.AppendLine();
                    break;
                }
            }

            string[] tokens = Regex.Split(qRaw, @"\s+");
            List<string> glosses = new List<string>();
            List<LexEntry> list = new List<LexEntry>(4);
            StringBuilder detailSb = new StringBuilder();
            for (int i = 0; i < tokens.Length; i++)
            {
                string clean = Regex.Replace(tokens[i], @"[.,;:!?()\[\]""“”]", "");
                if (string.IsNullOrEmpty(clean)) continue;
                string hap = ApplyHaplology(clean);
                if (!LookupTrReverse(snap, clean, 3, list))
                {
                    LookupTrReverse(snap, hap, 3, list);
                }
                IpaWordInfo ipa = AnalyzeWordIpa(hap);
                if (list.Count > 0)
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

            sb.AppendLine("GLOSA EM PORTUGUÊS");
            sb.AppendLine(string.Join(" ", glosses.ToArray()));
            sb.AppendLine();
            sb.AppendLine("ANÁLISE PALAVRA A PALAVRA");
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
                List<LexEntry> revList = new List<LexEntry>(lim);
                if (LookupTrReverse(snap, q, lim, revList))
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
        private sealed class PreparedPayload
        {
            public byte[][] RawParts;
            public long RawLen;
            public byte[] HdrRawKeep;
            public byte[] HdrRawClose;
            public byte[] GzipBytes;
            public byte[] HdrGzKeep;
            public byte[] HdrGzClose;
            public string ETag;
            public byte[] Hdr304Keep;
            public byte[] Hdr304Close;
        }

        private sealed class StaticAssetEntry
        {
            public PreparedPayload Payload;
        }

        private sealed class PayloadSnapshot
        {
            public PreparedPayload Html;
            public PreparedPayload Json;
            public PreparedPayload DadosJs;
            public byte[] JsonRaw;
            public Dictionary<string, StaticAssetEntry> Assets = new Dictionary<string, StaticAssetEntry>(StringComparer.OrdinalIgnoreCase);
            public string ActiveSource;
        }

        private sealed class CachedBytePair
        {
            public PreparedPayload Payload;
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

        private struct SlabSlice
        {
            public byte[] Array;
            public int Offset;
            public bool IsPooled;
        }

        private sealed class BufferSlabPool
        {
            private const int SliceSize = 4096;
            private const int SlicesPerBlock = 16; // 16 * 4096 = 65536 bytes (< 85 KB LOH threshold)
            private const int MaxBlocks = 384;     // Up to 6144 pooled slices = 24 MB peak
            private ConcurrentStack<SlabSlice> _stack = new ConcurrentStack<SlabSlice>();
            private int _allocatedBlocks;
            private readonly object _growLock = new object();

            public SlabSlice Rent()
            {
                ConcurrentStack<SlabSlice> stk = _stack;
                SlabSlice slice;
                if (stk.TryPop(out slice)) return slice;
                if (Thread.VolatileRead(ref _allocatedBlocks) < MaxBlocks)
                {
                    lock (_growLock)
                    {
                        stk = _stack;
                        if (stk.TryPop(out slice)) return slice;
                        if (_allocatedBlocks < MaxBlocks)
                        {
                            int toAdd = Math.Min(16, MaxBlocks - _allocatedBlocks);
                            for (int b = 0; b < toAdd; b++)
                            {
                                byte[] blk = new byte[SliceSize * SlicesPerBlock];
                                for (int s = 0; s < SlicesPerBlock; s++)
                                {
                                    stk.Push(new SlabSlice { Array = blk, Offset = s * SliceSize, IsPooled = true });
                                }
                                _allocatedBlocks++;
                            }
                            if (stk.TryPop(out slice)) return slice;
                        }
                    }
                }
                return new SlabSlice { Array = new byte[SliceSize], Offset = 0, IsPooled = false };
            }

            public void Return(SlabSlice slice)
            {
                if (slice.IsPooled && slice.Array != null)
                {
                    _stack.Push(slice);
                }
            }

            public void TrimOnIdle()
            {
                lock (_growLock)
                {
                    if (_allocatedBlocks > 2)
                    {
                        _stack = new ConcurrentStack<SlabSlice>();
                        _allocatedBlocks = 0;
                    }
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
            public int ContentLength;
        }

        private const int PhaseFree = 0;
        private const int PhaseZeroWait = 1;
        private const int PhaseDataRead = 2;
        private const int PhaseBodyRead = 3;
        private const int PhaseProcessing = 4;
        private const int PhaseSending = 5;
        private const int PhaseStreamingFile = 6;
        private const int PhaseClosed = 7;

        private const int ModeStartRead = 0;
        private const int ModeReadCompleted = 1;
        private const int ModeWriteCompleted = 2;

        private const int SlabSliceSize = 4096;
        private const int MaxKeepAliveRequests = 1000;
        private const int MaxPooledConns = 1024;
        private const int IdleRetainConns = 32;
        private const int ConnShardCount = 16;

        private sealed class ConnState
        {
            public long ConnId;
            public Socket Sock;
            public readonly SocketAsyncEventArgs ReadSaea;
            public readonly SocketAsyncEventArgs WriteSaea;
            public readonly HttpParsedRequest CurReq = new HttpParsedRequest();
            public readonly List<ArraySegment<byte>> SendSegs = new List<ArraySegment<byte>>(4);
            public readonly List<ArraySegment<byte>> SendActiveList = new List<ArraySegment<byte>>(4);

            public SlabSlice ReadSlice;
            public int ReadLen;
            public int ReadOffset;

            public byte[] BodyBuf;
            public int BodyGot;
            public int BodyLen;

            public int Phase;
            public int ReqCount;
            public bool KeepAliveAfterSend;
            public int SendSegIdx;
            public int SendSegOff;
            public long SendBatchBytes;

            public FileStream ActiveFileStream;
            public long FileRemaining;
            public byte[] FileChunkBuf;

            public long LastActivityTs;
            public int Closed;
            public int Counted;

            public ConnState(EventHandler<SocketAsyncEventArgs> readHandler, EventHandler<SocketAsyncEventArgs> writeHandler)
            {
                ReadSaea = new SocketAsyncEventArgs();
                ReadSaea.UserToken = this;
                ReadSaea.Completed += readHandler;

                WriteSaea = new SocketAsyncEventArgs();
                WriteSaea.UserToken = this;
                WriteSaea.Completed += writeHandler;
            }

            public void Touch()
            {
                Interlocked.Exchange(ref LastActivityTs, Stopwatch.GetTimestamp());
            }

            public void ResetForSocket(Socket s, long id)
            {
                Sock = s;
                ConnId = id;
                Phase = PhaseZeroWait;
                ReqCount = 0;
                ReadOffset = 0;
                ReadLen = 0;
                BodyBuf = null;
                BodyGot = 0;
                BodyLen = 0;
                KeepAliveAfterSend = false;
                SendSegs.Clear();
                SendActiveList.Clear();
                SendSegIdx = 0;
                SendSegOff = 0;
                SendBatchBytes = 0;
                ActiveFileStream = null;
                FileRemaining = 0;
                FileChunkBuf = null;
                Closed = 0;
                Counted = 1;
                Touch();
            }
        }

        private static readonly byte[] EmptyZeroBuffer = new byte[0];
        private static readonly byte[] DadosJsPrefix = Encoding.UTF8.GetBytes("window.CONDE_DB = ");
        private static readonly byte[] DadosJsSuffix = Encoding.UTF8.GetBytes(";\n");
        private static readonly byte[] BusyResponseBytes = Encoding.ASCII.GetBytes("HTTP/1.1 503 Service Unavailable\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 11\r\nConnection: close\r\n\r\nServer busy");
        private static readonly byte[] NotFoundBytes = Encoding.UTF8.GetBytes("Not found");
        private static readonly byte[] ArtifactNotFoundBytes = Encoding.UTF8.GetBytes("Artifact not found");
        private static readonly byte[] OkStatusBytes = Encoding.UTF8.GetBytes("{\"status\":\"ok\"}");
        private static readonly byte[] HeaderNotFoundKeep = BuildHeaderBytes("404 Not Found", "text/plain; charset=utf-8", NotFoundBytes.Length, false, null, "no-store", true);
        private static readonly byte[] HeaderNotFoundClose = BuildHeaderBytes("404 Not Found", "text/plain; charset=utf-8", NotFoundBytes.Length, false, null, "no-store", false);
        private static readonly byte[] HeaderArtNotFoundKeep = BuildHeaderBytes("404 Not Found", "text/plain; charset=utf-8", ArtifactNotFoundBytes.Length, false, null, "no-store", true);
        private static readonly byte[] HeaderArtNotFoundClose = BuildHeaderBytes("404 Not Found", "text/plain; charset=utf-8", ArtifactNotFoundBytes.Length, false, null, "no-store", false);
        private static readonly byte[] HeaderOkKeep = BuildHeaderBytes("200 OK", "application/json; charset=utf-8", OkStatusBytes.Length, false, null, "no-store", true);
        private static readonly byte[] HeaderOkClose = BuildHeaderBytes("200 OK", "application/json; charset=utf-8", OkStatusBytes.Length, false, null, "no-store", false);

        private readonly List<Socket> _listeners = new List<Socket>();
        private volatile bool _running;
        private int _activeConnections;
        private long _connIdSeq;
        private int _connPoolCount;
        private int _peakSinceIdleTrim;
        private int _idleStableTicks;
        private int _reaperRunning;
        private System.Threading.Timer _reaperTimer;

        private readonly object[] _shardLocks = new object[ConnShardCount];
        private readonly Dictionary<long, ConnState>[] _connShards = new Dictionary<long, ConnState>[ConnShardCount];
        private readonly ConcurrentStack<ConnState> _connPool = new ConcurrentStack<ConnState>();
        private readonly ConcurrentBag<SocketAsyncEventArgs> _acceptSaeas = new ConcurrentBag<SocketAsyncEventArgs>();
        private readonly BufferSlabPool _slabPool = new BufferSlabPool();

        public int Port { get; private set; }
        public int PreferredPort { get; set; }
        public bool BindMultiLoopback { get; set; }
        public int MaxConcurrentConnections { get; set; }
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
        private readonly string _localCondeDbCompactGzPath = @"D:\Conde_Treppio\sandbox\dicionario_exaustivo\dicionario_formas_expandidas.compact.json.gz";
        private readonly string _localCondeHtmlPath = @"D:\Conde_Treppio\sandbox\ui_dicionario\index.html";
        private readonly string _localUiDir = @"D:\Conde_Treppio\sandbox\ui_dicionario";

        private PayloadSnapshot _snapshot;
        private readonly BoundedLruCache _apiLru = new BoundedLruCache(2048);
        private readonly SemaphoreSlim _recompileGate = new SemaphoreSlim(1, 1);

        public EmbeddedServer()
        {
            MaxConcurrentConnections = 120000;
            for (int i = 0; i < ConnShardCount; i++)
            {
                _shardLocks[i] = new object();
                _connShards[i] = new Dictionary<long, ConnState>();
            }
            Lexicon = new TreppioLexiconEngine();
            _appDataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "CondeTreppio");
            Directory.CreateDirectory(_appDataDir);
            _cachedDbPath = Path.Combine(_appDataDir, "dicionario_formas_expandidas.json");
            _cloudConfigPath = Path.Combine(_appDataDir, "cloud_url.txt");

            CloudUrl = File.Exists(_cloudConfigPath) ? File.ReadAllText(_cloudConfigPath, Encoding.UTF8).Trim() : "";
            ReloadPayloads();
        }

        private static byte[] CompressGzipSegments(params byte[][] segs)
        {
            if (segs == null || segs.Length == 0) return new byte[0];
            using (MemoryStream ms = new MemoryStream())
            {
                using (GZipStream gz = new GZipStream(ms, CompressionLevel.Optimal, true))
                {
                    for (int i = 0; i < segs.Length; i++)
                    {
                        byte[] s = segs[i];
                        if (s != null && s.Length > 0) gz.Write(s, 0, s.Length);
                    }
                }
                return ms.ToArray();
            }
        }

        private static byte[] DecompressGzip(byte[] gzBytes)
        {
            if (gzBytes == null || gzBytes.Length == 0) return new byte[0];
            int initCap = 0;
            if (gzBytes.Length >= 18)
            {
                int isize = BitConverter.ToInt32(gzBytes, gzBytes.Length - 4);
                if (isize >= 1024 && isize <= 64 * 1024 * 1024) initCap = isize;
            }
            using (MemoryStream src = new MemoryStream(gzBytes))
            using (GZipStream gz = new GZipStream(src, CompressionMode.Decompress))
            using (MemoryStream dst = initCap > 0 ? new MemoryStream(initCap) : new MemoryStream())
            {
                gz.CopyTo(dst, 65536);
                if (dst.Length == dst.Capacity)
                {
                    return dst.GetBuffer();
                }
                return dst.ToArray();
            }
        }

        private static string ComputeETagSegments(params byte[][] segs)
        {
            if (segs == null || segs.Length == 0) return "\"0\"";
            using (SHA256 sha = SHA256.Create())
            {
                for (int i = 0; i < segs.Length; i++)
                {
                    byte[] d = segs[i];
                    if (d != null && d.Length > 0) sha.TransformBlock(d, 0, d.Length, null, 0);
                }
                sha.TransformFinalBlock(EmptyZeroBuffer, 0, 0);
                byte[] h = sha.Hash;
                StringBuilder sb = new StringBuilder(20);
                sb.Append('"');
                for (int i = 0; i < 8; i++) sb.Append(h[i].ToString("x2", CultureInfo.InvariantCulture));
                sb.Append('"');
                return sb.ToString();
            }
        }

        private static byte[] BuildHeaderBytes(string status, string contentType, long contentLength, bool isGzip, string etag, string cacheControl, bool keepAlive)
        {
            StringBuilder sb = new StringBuilder(320);
            sb.Append("HTTP/1.1 "); sb.Append(status); sb.Append("\r\n");
            sb.Append("Content-Type: "); sb.Append(contentType); sb.Append("\r\n");
            sb.Append("Content-Length: "); sb.Append(contentLength); sb.Append("\r\n");
            if (isGzip) sb.Append("Content-Encoding: gzip\r\n");
            sb.Append("Vary: Accept-Encoding\r\n");
            if (!string.IsNullOrEmpty(etag)) { sb.Append("ETag: "); sb.Append(etag); sb.Append("\r\n"); }
            sb.Append("Cache-Control: "); sb.Append(cacheControl ?? "no-cache"); sb.Append("\r\n");
            sb.Append("Access-Control-Allow-Origin: *\r\n");
            sb.Append("Connection: "); sb.Append(keepAlive ? "keep-alive\r\n\r\n" : "close\r\n\r\n");
            return Encoding.ASCII.GetBytes(sb.ToString());
        }

        private static byte[] BuildNotModifiedBytes(string etag, string cacheControl, bool keepAlive)
        {
            StringBuilder sb = new StringBuilder(224);
            sb.Append("HTTP/1.1 304 Not Modified\r\n");
            if (!string.IsNullOrEmpty(etag)) { sb.Append("ETag: "); sb.Append(etag); sb.Append("\r\n"); }
            sb.Append("Cache-Control: "); sb.Append(cacheControl ?? "no-cache"); sb.Append("\r\n");
            sb.Append("Vary: Accept-Encoding\r\n");
            sb.Append("Access-Control-Allow-Origin: *\r\n");
            sb.Append("Connection: "); sb.Append(keepAlive ? "keep-alive\r\n\r\n" : "close\r\n\r\n");
            return Encoding.ASCII.GetBytes(sb.ToString());
        }

        private static PreparedPayload BuildPreparedPayload(string contentType, string cacheControl, bool computeGzip, bool computeEtag, params byte[][] rawParts)
        {
            long rawLen = 0;
            for (int i = 0; i < rawParts.Length; i++)
            {
                if (rawParts[i] != null) rawLen += rawParts[i].Length;
            }
            string etag = computeEtag ? ComputeETagSegments(rawParts) : null;
            byte[] gz = (computeGzip && rawLen >= 256) ? CompressGzipSegments(rawParts) : null;
            if (gz != null && gz.Length >= rawLen) gz = null;

            return new PreparedPayload
            {
                RawParts = rawParts,
                RawLen = rawLen,
                HdrRawKeep = BuildHeaderBytes("200 OK", contentType, rawLen, false, etag, cacheControl, true),
                HdrRawClose = BuildHeaderBytes("200 OK", contentType, rawLen, false, etag, cacheControl, false),
                GzipBytes = gz,
                HdrGzKeep = gz != null ? BuildHeaderBytes("200 OK", contentType, gz.Length, true, etag, cacheControl, true) : null,
                HdrGzClose = gz != null ? BuildHeaderBytes("200 OK", contentType, gz.Length, true, etag, cacheControl, false) : null,
                ETag = etag,
                Hdr304Keep = !string.IsNullOrEmpty(etag) ? BuildNotModifiedBytes(etag, cacheControl, true) : null,
                Hdr304Close = !string.IsNullOrEmpty(etag) ? BuildNotModifiedBytes(etag, cacheControl, false) : null
            };
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
            bool compress = !fileName.EndsWith(".png", StringComparison.OrdinalIgnoreCase)
                         && !fileName.EndsWith(".ico", StringComparison.OrdinalIgnoreCase)
                         && raw.Length >= 256;
            return new StaticAssetEntry
            {
                Payload = BuildPreparedPayload(contentType, cacheControl, compress, true, raw)
            };
        }

        public void ReloadPayloads()
        {
            byte[] htmlRaw = File.Exists(_localCondeHtmlPath)
                ? File.ReadAllBytes(_localCondeHtmlPath)
                : ReadEmbeddedResource("index.html");

            byte[] jsonRaw;
            string sourceLabel;
            if (File.Exists(_localCondeDbCompactGzPath) &&
                (!File.Exists(_localCondeDbPath) || File.GetLastWriteTimeUtc(_localCondeDbCompactGzPath) >= File.GetLastWriteTimeUtc(_localCondeDbPath).AddSeconds(-2)))
            {
                jsonRaw = DecompressGzip(File.ReadAllBytes(_localCondeDbCompactGzPath));
                sourceLabel = "Base Local Compacta (D:\\Conde_Treppio)";
            }
            else if (File.Exists(_localCondeDbPath))
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

            byte[] safeHtml = htmlRaw ?? EmptyZeroBuffer;
            byte[] safeJson = jsonRaw ?? Encoding.UTF8.GetBytes("{}");

            PayloadSnapshot next = new PayloadSnapshot();
            next.ActiveSource = sourceLabel;
            next.JsonRaw = safeJson;
            next.Html = BuildPreparedPayload("text/html; charset=utf-8", "no-cache", true, true, safeHtml);
            next.Json = BuildPreparedPayload("application/json; charset=utf-8", "no-cache", true, true, safeJson);
            next.DadosJs = BuildPreparedPayload("application/javascript; charset=utf-8", "public, max-age=60", true, true, DadosJsPrefix, safeJson, DadosJsSuffix);

            AddStaticIfPresent(next, "brasao_conde.svg", "image/svg+xml; charset=utf-8", "public, max-age=86400");
            AddStaticIfPresent(next, "manifest.json", "application/manifest+json; charset=utf-8", "public, max-age=300");
            AddStaticIfPresent(next, "sw.js", "application/javascript; charset=utf-8", "no-cache");
            AddStaticIfPresent(next, "icon-512.png", "image/png", "public, max-age=86400");
            AddStaticIfPresent(next, "icon-192.png", "image/png", "public, max-age=86400");
            AddStaticIfPresent(next, "icon-maskable-512.png", "image/png", "public, max-age=86400");
            AddStaticIfPresent(next, "favicon.ico", "image/x-icon", "public, max-age=86400");

            Interlocked.Exchange(ref _snapshot, next);
            StartBackgroundIndexBuild(safeJson);
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
                    wc.Headers.Add("User-Agent", "CondeTreppioLauncher/9.0");
                    string json = wc.DownloadString(directUrl);
                    if (!json.Contains("\"substantivos\""))
                    {
                        message = "O arquivo baixado nao contem um banco de dados valido.";
                        return false;
                    }
                    File.WriteAllText(_cachedDbPath, json, Encoding.UTF8);
                    File.WriteAllText(_cloudConfigPath, directUrl, Encoding.UTF8);
                    CloudUrl = directUrl;

                    PayloadSnapshot cur = _snapshot;
                    byte[] htmlRaw = (cur != null && cur.Html != null && cur.Html.RawParts != null && cur.Html.RawParts.Length > 0)
                        ? cur.Html.RawParts[0]
                        : ReadEmbeddedResource("index.html");
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
                ActiveSource = "Base Local Recompilada";
                message = "Base local recompilada (" + TotalForms.ToString("N0", new CultureInfo("pt-BR")) + " formas).";
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
            ThreadPool.SetMinThreads(Math.Max(minW, 64), Math.Max(minC, 128));

            List<int> candidatePorts = new List<int>();
            if (PreferredPort > 0) candidatePorts.Add(PreferredPort);
            candidatePorts.Add(8766);
            candidatePorts.Add(8767);
            candidatePorts.Add(8768);
            candidatePorts.Add(0);

            Socket primaryV4 = null;
            for (int i = 0; i < candidatePorts.Count; i++)
            {
                int p = candidatePorts[i];
                Socket sock = null;
                try
                {
                    sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                    sock.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
                    sock.Bind(new IPEndPoint(IPAddress.Loopback, p));
                    sock.Listen(65535);
                    primaryV4 = sock;
                    Port = ((IPEndPoint)sock.LocalEndPoint).Port;
                    _listeners.Add(sock);
                    break;
                }
                catch
                {
                    if (sock != null) { try { sock.Close(); } catch { } }
                }
            }

            if (primaryV4 == null)
            {
                throw new InvalidOperationException("Nao foi possivel vincular o servidor HTTP local.");
            }

            if (BindMultiLoopback)
            {
                for (int octet = 2; octet <= 32; octet++)
                {
                    Socket extra = null;
                    try
                    {
                        IPAddress ip = IPAddress.Parse("127.0.0." + octet.ToString(CultureInfo.InvariantCulture));
                        extra = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                        extra.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
                        extra.Bind(new IPEndPoint(ip, Port));
                        extra.Listen(65535);
                        _listeners.Add(extra);
                    }
                    catch
                    {
                        if (extra != null) { try { extra.Close(); } catch { } }
                    }
                }
            }

            try
            {
                Socket sock6 = new Socket(AddressFamily.InterNetworkV6, SocketType.Stream, ProtocolType.Tcp);
                sock6.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
                sock6.Bind(new IPEndPoint(IPAddress.IPv6Loopback, Port));
                sock6.Listen(65535);
                _listeners.Add(sock6);
            }
            catch { }

            _running = true;
            _reaperTimer = new System.Threading.Timer(OnReaperTick, null, 1000, 1000);

            int acceptSlotsPerListener = _listeners.Count > 4 ? 16 : 64;
            for (int i = 0; i < _listeners.Count; i++)
            {
                Socket listener = _listeners[i];
                for (int s = 0; s < acceptSlotsPerListener; s++)
                {
                    SocketAsyncEventArgs saea = new SocketAsyncEventArgs();
                    saea.UserToken = listener;
                    saea.Completed += OnAcceptCompleted;
                    _acceptSaeas.Add(saea);
                    StartAccept(listener, saea);
                }
            }
        }

        public void Stop()
        {
            _running = false;
            try
            {
                System.Threading.Timer t = _reaperTimer;
                _reaperTimer = null;
                if (t != null) t.Dispose();
            }
            catch { }

            for (int i = 0; i < _listeners.Count; i++)
            {
                try { _listeners[i].Close(); } catch { }
            }
            _listeners.Clear();

            List<Socket> toClose = new List<Socket>();
            for (int s = 0; s < ConnShardCount; s++)
            {
                lock (_shardLocks[s])
                {
                    foreach (KeyValuePair<long, ConnState> kv in _connShards[s])
                    {
                        Socket sock = kv.Value.Sock;
                        if (sock != null) toClose.Add(sock);
                    }
                    _connShards[s].Clear();
                }
            }
            for (int i = 0; i < toClose.Count; i++)
            {
                try { toClose[i].Close(); } catch { }
            }
        }

        private void OnReaperTick(object state)
        {
            if (!_running) return;
            if (Interlocked.CompareExchange(ref _reaperRunning, 1, 0) != 0) return;
            try
            {
                int active = Thread.VolatileRead(ref _activeConnections);
                long ttlMs = 8000;
                if (active >= 60000) ttlMs = 1200;
                else if (active >= 25000) ttlMs = 2500;
                else if (active >= 10000) ttlMs = 5000;

                long freq = Stopwatch.Frequency;
                long maxIdleTicks = (ttlMs * freq) / 1000L;
                long maxSendHangTicks = (30000L * freq) / 1000L;
                long nowTs = Stopwatch.GetTimestamp();

                List<Socket> expired = null;
                for (int s = 0; s < ConnShardCount; s++)
                {
                    lock (_shardLocks[s])
                    {
                        if (_connShards[s].Count == 0) continue;
                        foreach (KeyValuePair<long, ConnState> kv in _connShards[s])
                        {
                            ConnState c = kv.Value;
                            long elapsed = nowTs - Interlocked.Read(ref c.LastActivityTs);
                            int phase = Volatile.Read(ref c.Phase);
                            long limit = (phase >= PhaseSending) ? maxSendHangTicks : maxIdleTicks;
                            if (elapsed >= limit)
                            {
                                Socket sock = c.Sock;
                                if (sock != null)
                                {
                                    if (expired == null) expired = new List<Socket>(64);
                                    expired.Add(sock);
                                }
                            }
                        }
                    }
                }
                if (expired != null)
                {
                    for (int i = 0; i < expired.Count; i++)
                    {
                        try { expired[i].Close(); } catch { }
                    }
                }

                if (active <= 2)
                {
                    int idleT = Interlocked.Increment(ref _idleStableTicks);
                    if (idleT >= 2 && Volatile.Read(ref _peakSinceIdleTrim) >= 100)
                    {
                        Volatile.Write(ref _peakSinceIdleTrim, 0);
                        Interlocked.Exchange(ref _idleStableTicks, 0);
                        while (Volatile.Read(ref _connPoolCount) > IdleRetainConns)
                        {
                            ConnState evicted;
                            if (!_connPool.TryPop(out evicted)) break;
                            Interlocked.Decrement(ref _connPoolCount);
                            try { evicted.ReadSaea.Dispose(); } catch { }
                            try { evicted.WriteSaea.Dispose(); } catch { }
                        }
                        _slabPool.TrimOnIdle();
                        GCSettings.LargeObjectHeapCompactionMode = GCLargeObjectHeapCompactionMode.CompactOnce;
                        GC.Collect(2, GCCollectionMode.Forced, true, true);
                        GC.WaitForPendingFinalizers();
                        GC.Collect(2, GCCollectionMode.Forced, true, true);
                    }
                }
                else
                {
                    Interlocked.Exchange(ref _idleStableTicks, 0);
                }
            }
            catch { }
            finally
            {
                Interlocked.Exchange(ref _reaperRunning, 0);
            }
        }

        private void StartAccept(Socket listener, SocketAsyncEventArgs saea)
        {
            while (_running)
            {
                saea.AcceptSocket = null;
                bool pending;
                try
                {
                    pending = listener.AcceptAsync(saea);
                }
                catch
                {
                    break;
                }
                if (pending) return;
                HandleAccepted(saea);
            }
        }

        private void OnAcceptCompleted(object sender, SocketAsyncEventArgs saea)
        {
            HandleAccepted(saea);
            Socket listener = saea.UserToken as Socket;
            if (listener != null && _running)
            {
                StartAccept(listener, saea);
            }
        }

        private void HandleAccepted(SocketAsyncEventArgs saea)
        {
            Socket client = saea.AcceptSocket;
            saea.AcceptSocket = null;
            if (saea.SocketError != SocketError.Success || client == null || !_running)
            {
                if (client != null) { try { client.Close(); } catch { } }
                return;
            }

            int curConns = Interlocked.Increment(ref _activeConnections);
            if (curConns > MaxConcurrentConnections)
            {
                Interlocked.Decrement(ref _activeConnections);
                try { client.SendTimeout = 250; client.Send(BusyResponseBytes); } catch { }
                try { client.Close(); } catch { }
                return;
            }

            try { client.NoDelay = true; } catch { }
            ConnState conn;
            if (_connPool.TryPop(out conn))
            {
                Interlocked.Decrement(ref _connPoolCount);
            }
            else
            {
                conn = new ConnState(OnReadCompleted, OnWriteCompleted);
            }
            int prevPeak = Volatile.Read(ref _peakSinceIdleTrim);
            if (curConns > prevPeak) Interlocked.CompareExchange(ref _peakSinceIdleTrim, curConns, prevPeak);
            long id = Interlocked.Increment(ref _connIdSeq);
            conn.ResetForSocket(client, id);

            int shard = (int)(id & (ConnShardCount - 1));
            lock (_shardLocks[shard])
            {
                _connShards[shard][id] = conn;
            }

            RunConnectionLoop(conn, ModeStartRead);
        }

        private void EnsureReadSlice(ConnState conn)
        {
            if (conn.ReadSlice.Array == null)
            {
                conn.ReadSlice = _slabPool.Rent();
                conn.ReadLen = 0;
                conn.ReadOffset = 0;
            }
        }

        private void ReleaseReadSlice(ConnState conn)
        {
            if (conn.ReadSlice.Array != null)
            {
                _slabPool.Return(conn.ReadSlice);
                conn.ReadSlice = default(SlabSlice);
            }
            conn.ReadLen = 0;
            conn.ReadOffset = 0;
        }

        private void CloseAndRecycle(ConnState conn)
        {
            if (Interlocked.Exchange(ref conn.Closed, 1) != 0) return;

            Volatile.Write(ref conn.Phase, PhaseClosed);
            long cid = conn.ConnId;
            if (cid > 0)
            {
                int shard = (int)(cid & (ConnShardCount - 1));
                lock (_shardLocks[shard])
                {
                    _connShards[shard].Remove(cid);
                }
            }

            Socket sock = Interlocked.Exchange(ref conn.Sock, null);
            if (sock != null)
            {
                try { sock.Close(); } catch { }
            }

            ReleaseReadSlice(conn);
            conn.BodyBuf = null;
            conn.BodyGot = 0;
            conn.BodyLen = 0;
            conn.SendSegs.Clear();
            conn.SendActiveList.Clear();

            FileStream fs = conn.ActiveFileStream;
            conn.ActiveFileStream = null;
            conn.FileChunkBuf = null;
            if (fs != null) { try { fs.Dispose(); } catch { } }

            if (Interlocked.Exchange(ref conn.Counted, 0) != 0)
            {
                Interlocked.Decrement(ref _activeConnections);
            }

            conn.ConnId = 0;
            conn.Phase = PhaseFree;
            try
            {
                conn.ReadSaea.BufferList = null;
                conn.ReadSaea.SetBuffer(null, 0, 0);
                conn.WriteSaea.BufferList = null;
                conn.WriteSaea.SetBuffer(null, 0, 0);
            }
            catch { }

            if (Interlocked.Increment(ref _connPoolCount) <= MaxPooledConns)
            {
                _connPool.Push(conn);
            }
            else
            {
                Interlocked.Decrement(ref _connPoolCount);
                try { conn.ReadSaea.Dispose(); } catch { }
                try { conn.WriteSaea.Dispose(); } catch { }
            }
        }

        private void OnReadCompleted(object sender, SocketAsyncEventArgs saea)
        {
            ConnState conn = saea.UserToken as ConnState;
            if (conn != null) RunConnectionLoop(conn, ModeReadCompleted);
        }

        private void OnWriteCompleted(object sender, SocketAsyncEventArgs saea)
        {
            ConnState conn = saea.UserToken as ConnState;
            if (conn != null) RunConnectionLoop(conn, ModeWriteCompleted);
        }

        private void RunConnectionLoop(ConnState conn, int mode)
        {
            while (true)
            {
                if (Thread.VolatileRead(ref conn.Closed) != 0 || conn.Sock == null)
                {
                    CloseAndRecycle(conn);
                    return;
                }

                if (mode == ModeStartRead)
                {
                    if (!_running || conn.ReqCount >= MaxKeepAliveRequests)
                    {
                        CloseAndRecycle(conn);
                        return;
                    }
                    if (conn.ReadSlice.Array != null && conn.ReadOffset < conn.ReadLen)
                    {
                        mode = TryParseAndDispatch(conn);
                        if (mode < 0) return;
                        continue;
                    }
                    ReleaseReadSlice(conn);
                    Volatile.Write(ref conn.Phase, PhaseZeroWait);
                    conn.Touch();
                    conn.ReadSaea.BufferList = null;
                    conn.ReadSaea.SetBuffer(EmptyZeroBuffer, 0, 0);
                    bool pending;
                    try { pending = conn.Sock.ReceiveAsync(conn.ReadSaea); }
                    catch { CloseAndRecycle(conn); return; }
                    if (pending) return;
                    mode = ModeReadCompleted;
                    continue;
                }
                else if (mode == ModeReadCompleted)
                {
                    if (conn.ReadSaea.SocketError != SocketError.Success)
                    {
                        CloseAndRecycle(conn);
                        return;
                    }
                    int phase = Volatile.Read(ref conn.Phase);
                    if (phase == PhaseZeroWait)
                    {
                        EnsureReadSlice(conn);
                        Volatile.Write(ref conn.Phase, PhaseDataRead);
                        conn.Touch();
                        conn.ReadSaea.BufferList = null;
                        conn.ReadSaea.SetBuffer(conn.ReadSlice.Array, conn.ReadSlice.Offset, SlabSliceSize);
                        bool pending;
                        try { pending = conn.Sock.ReceiveAsync(conn.ReadSaea); }
                        catch { CloseAndRecycle(conn); return; }
                        if (pending) return;
                        continue;
                    }
                    else if (phase == PhaseDataRead)
                    {
                        int n = conn.ReadSaea.BytesTransferred;
                        if (n <= 0)
                        {
                            CloseAndRecycle(conn);
                            return;
                        }
                        conn.ReadLen += n;
                        conn.Touch();
                        mode = TryParseAndDispatch(conn);
                        if (mode < 0) return;
                        continue;
                    }
                    else if (phase == PhaseBodyRead)
                    {
                        int n = conn.ReadSaea.BytesTransferred;
                        if (n <= 0)
                        {
                            CloseAndRecycle(conn);
                            return;
                        }
                        conn.BodyGot += n;
                        conn.Touch();
                        if (conn.BodyGot < conn.BodyLen)
                        {
                            conn.ReadSaea.BufferList = null;
                            conn.ReadSaea.SetBuffer(conn.BodyBuf, conn.BodyGot, conn.BodyLen - conn.BodyGot);
                            bool pending;
                            try { pending = conn.Sock.ReceiveAsync(conn.ReadSaea); }
                            catch { CloseAndRecycle(conn); return; }
                            if (pending) return;
                            continue;
                        }
                        string bodyStr = Encoding.UTF8.GetString(conn.BodyBuf, 0, conn.BodyLen);
                        conn.BodyBuf = null;
                        conn.BodyGot = 0;
                        conn.BodyLen = 0;
                        mode = DispatchParsedRequest(conn, bodyStr);
                        if (mode < 0) return;
                        continue;
                    }
                    else
                    {
                        CloseAndRecycle(conn);
                        return;
                    }
                }
                else if (mode == ModeWriteCompleted)
                {
                    if (conn.WriteSaea.SocketError != SocketError.Success || conn.WriteSaea.BytesTransferred <= 0)
                    {
                        CloseAndRecycle(conn);
                        return;
                    }
                    conn.Touch();
                    int nextMode;
                    if (AdvanceSendOrFinish(conn, conn.WriteSaea.BytesTransferred, out nextMode))
                    {
                        if (nextMode < 0) return;
                        mode = nextMode;
                        continue;
                    }
                    return;
                }
                else
                {
                    CloseAndRecycle(conn);
                    return;
                }
            }
        }

        private int TryParseAndDispatch(ConnState conn)
        {
            byte[] buf = conn.ReadSlice.Array;
            int baseOff = conn.ReadSlice.Offset;
            int avail = conn.ReadLen - conn.ReadOffset;
            int headerRelEnd = FindHeaderEnd(buf, baseOff + conn.ReadOffset, avail);

            if (headerRelEnd < 0)
            {
                if (conn.ReadOffset > 0 && avail > 0)
                {
                    Buffer.BlockCopy(buf, baseOff + conn.ReadOffset, buf, baseOff, avail);
                    conn.ReadLen = avail;
                    conn.ReadOffset = 0;
                }
                else if (conn.ReadOffset > 0)
                {
                    conn.ReadLen = 0;
                    conn.ReadOffset = 0;
                }

                if (conn.ReadLen >= SlabSliceSize)
                {
                    CloseAndRecycle(conn);
                    return -1;
                }

                Volatile.Write(ref conn.Phase, PhaseDataRead);
                conn.ReadSaea.BufferList = null;
                conn.ReadSaea.SetBuffer(buf, baseOff + conn.ReadLen, SlabSliceSize - conn.ReadLen);
                bool pending;
                try { pending = conn.Sock.ReceiveAsync(conn.ReadSaea); }
                catch { CloseAndRecycle(conn); return -1; }
                return pending ? -1 : ModeReadCompleted;
            }

            if (!ParseHttpHeaderBlock(buf, baseOff + conn.ReadOffset, headerRelEnd, conn.CurReq))
            {
                CloseAndRecycle(conn);
                return -1;
            }

            conn.ReadOffset += headerRelEnd + 4;
            int remaining = conn.ReadLen - conn.ReadOffset;
            int cl = conn.CurReq.ContentLength;

            if (cl <= 0)
            {
                if (remaining > 0)
                {
                    Buffer.BlockCopy(buf, baseOff + conn.ReadOffset, buf, baseOff, remaining);
                    conn.ReadLen = remaining;
                    conn.ReadOffset = 0;
                }
                else
                {
                    ReleaseReadSlice(conn);
                }
                return DispatchParsedRequest(conn, "");
            }

            if (remaining >= cl)
            {
                string bodyStr = Encoding.UTF8.GetString(buf, baseOff + conn.ReadOffset, cl);
                conn.ReadOffset += cl;
                int extra = conn.ReadLen - conn.ReadOffset;
                if (extra > 0)
                {
                    Buffer.BlockCopy(buf, baseOff + conn.ReadOffset, buf, baseOff, extra);
                    conn.ReadLen = extra;
                    conn.ReadOffset = 0;
                }
                else
                {
                    ReleaseReadSlice(conn);
                }
                return DispatchParsedRequest(conn, bodyStr);
            }

            byte[] bodyBuf = new byte[cl];
            if (remaining > 0) Buffer.BlockCopy(buf, baseOff + conn.ReadOffset, bodyBuf, 0, remaining);
            ReleaseReadSlice(conn);
            conn.BodyBuf = bodyBuf;
            conn.BodyGot = remaining;
            conn.BodyLen = cl;
            Volatile.Write(ref conn.Phase, PhaseBodyRead);
            conn.ReadSaea.BufferList = null;
            conn.ReadSaea.SetBuffer(conn.BodyBuf, conn.BodyGot, conn.BodyLen - conn.BodyGot);
            bool bodyPending;
            try { bodyPending = conn.Sock.ReceiveAsync(conn.ReadSaea); }
            catch { CloseAndRecycle(conn); return -1; }
            return bodyPending ? -1 : ModeReadCompleted;
        }

        private static bool ParseHttpHeaderBlock(byte[] buf, int offset, int len, HttpParsedRequest req)
        {
            string headerText = Encoding.ASCII.GetString(buf, offset, len);
            int firstCr = headerText.IndexOf('\n');
            string firstLine = (firstCr >= 0 ? headerText.Substring(0, firstCr) : headerText).TrimEnd('\r');
            int sp1 = firstLine.IndexOf(' ');
            if (sp1 <= 0) return false;
            int sp2 = firstLine.IndexOf(' ', sp1 + 1);
            string methodRaw = firstLine.Substring(0, sp1);
            string rawTarget = sp2 > sp1 ? firstLine.Substring(sp1 + 1, sp2 - sp1 - 1) : firstLine.Substring(sp1 + 1);
            string proto = sp2 > sp1 ? firstLine.Substring(sp2 + 1) : "HTTP/1.1";

            req.Method = methodRaw.ToUpperInvariant();
            int qIdx = rawTarget.IndexOf('?');
            req.Path = qIdx >= 0 ? rawTarget.Substring(0, qIdx) : rawTarget;
            req.Query = qIdx >= 0 ? rawTarget.Substring(qIdx + 1) : "";
            req.AcceptsGzip = false;
            req.IfNoneMatch = null;
            req.ContentLength = 0;

            bool isHttp10 = proto.Equals("HTTP/1.0", StringComparison.OrdinalIgnoreCase);
            bool hasKeep = false;
            bool hasClose = false;

            if (firstCr >= 0)
            {
                int pos = firstCr + 1;
                while (pos < headerText.Length)
                {
                    int nextNl = headerText.IndexOf('\n', pos);
                    int lineEnd = nextNl >= 0 ? nextNl : headerText.Length;
                    string line = headerText.Substring(pos, lineEnd - pos).TrimEnd('\r');
                    pos = lineEnd + 1;
                    int colon = line.IndexOf(':');
                    if (colon <= 0) continue;
                    string hName = line.Substring(0, colon).Trim();
                    string hVal = line.Substring(colon + 1).Trim();

                    if (hName.Equals("Connection", StringComparison.OrdinalIgnoreCase))
                    {
                        if (hVal.IndexOf("close", StringComparison.OrdinalIgnoreCase) >= 0) hasClose = true;
                        if (hVal.IndexOf("keep-alive", StringComparison.OrdinalIgnoreCase) >= 0) hasKeep = true;
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
                        if (int.TryParse(hVal, out cl) && cl > 0) req.ContentLength = Math.Min(cl, 1024 * 1024);
                    }
                }
            }

            req.KeepAlive = isHttp10 ? (hasKeep && !hasClose) : !hasClose;
            return true;
        }

        private int DispatchParsedRequest(ConnState conn, string body)
        {
            conn.ReqCount++;
            HttpParsedRequest req = conn.CurReq;
            bool keepAlive = req.KeepAlive && conn.ReqCount < MaxKeepAliveRequests;
            bool isHead = req.Method == "HEAD";
            PayloadSnapshot snap = _snapshot;
            string path = req.Path;

            Volatile.Write(ref conn.Phase, PhaseProcessing);

            if (path == "/api/health")
            {
                byte[] healthBytes = BuildHealthJsonBytes();
                byte[] hdr = BuildHeaderBytes("200 OK", "application/json; charset=utf-8", healthBytes.Length, false, null, "no-store", keepAlive);
                return StartSendSingle(conn, hdr, isHead ? null : healthBytes, keepAlive);
            }
            if (path == "/api/ipa")
            {
                string q = GetQueryParam(req.Query, "q");
                if (string.IsNullOrEmpty(q)) q = "Haly'itror giza in oxej";
                string key = "ipa|" + q;
                CachedBytePair pair = GetOrBuildCachedApiResponse(key, () => Lexicon.BuildIpaJson(q));
                return StartSendPrepared(conn, pair.Payload, req.AcceptsGzip, req.IfNoneMatch, keepAlive, isHead);
            }
            if (path == "/api/traduzir")
            {
                string dir = GetQueryParam(req.Query, "dir");
                if (string.IsNullOrEmpty(dir)) dir = "pt-tr";
                string q = GetQueryParam(req.Query, "q");
                string key = Lexicon.Generation + "|tr|" + dir + "|" + q;
                CachedBytePair pair = GetOrBuildCachedApiResponse(key, () => Lexicon.BuildTranslateJson(dir, q));
                return StartSendPrepared(conn, pair.Payload, req.AcceptsGzip, req.IfNoneMatch, keepAlive, isHead);
            }
            if (path == "/api/search")
            {
                string q = GetQueryParam(req.Query, "q");
                int limit = 12;
                string limStr = GetQueryParam(req.Query, "limit");
                int parsedLim;
                if (int.TryParse(limStr, out parsedLim) && parsedLim > 0) limit = parsedLim;
                string key = Lexicon.Generation + "|sr|" + limit + "|" + q;
                CachedBytePair pair = GetOrBuildCachedApiResponse(key, () => Lexicon.BuildSearchJson(q, limit));
                return StartSendPrepared(conn, pair.Payload, req.AcceptsGzip, req.IfNoneMatch, keepAlive, isHead);
            }
            if (path == "/api/db" || path.EndsWith("/dicionario_formas_expandidas.json", StringComparison.OrdinalIgnoreCase))
            {
                return StartSendPrepared(conn, snap.Json, req.AcceptsGzip, req.IfNoneMatch, keepAlive, isHead);
            }
            if (path == "/dados_dicionario_conde.js")
            {
                return StartSendPrepared(conn, snap.DadosJs, req.AcceptsGzip, req.IfNoneMatch, keepAlive, isHead);
            }
            if (path == "/" || path == "/index.html")
            {
                return StartSendPrepared(conn, snap.Html, req.AcceptsGzip, req.IfNoneMatch, keepAlive, isHead);
            }
            if (path == "/api/recompilar" && req.Method == "POST")
            {
                string msg;
                RecompileLocalConde(out msg);
                PayloadSnapshot updated = _snapshot;
                byte[] prefix = Encoding.UTF8.GetBytes("{\"status\":\"ok\",\"source\":\"" + TreppioLexiconEngine.EscapeJsonValue(updated.ActiveSource) + "\",\"db\":");
                byte[] suffix = Encoding.UTF8.GetBytes("}");
                if (req.AcceptsGzip)
                {
                    byte[] gz = CompressGzipSegments(prefix, updated.JsonRaw, suffix);
                    byte[] hdr = BuildHeaderBytes("200 OK", "application/json; charset=utf-8", gz.Length, true, null, "no-store", keepAlive);
                    return StartSendSingle(conn, hdr, gz, keepAlive);
                }
                else
                {
                    long totalLen = (long)prefix.Length + updated.JsonRaw.Length + suffix.Length;
                    byte[] hdr = BuildHeaderBytes("200 OK", "application/json; charset=utf-8", totalLen, false, null, "no-store", keepAlive);
                    conn.SendSegs.Clear();
                    conn.SendSegs.Add(new ArraySegment<byte>(hdr));
                    conn.SendSegs.Add(new ArraySegment<byte>(prefix));
                    conn.SendSegs.Add(new ArraySegment<byte>(updated.JsonRaw));
                    conn.SendSegs.Add(new ArraySegment<byte>(suffix));
                    return StartSendSegs(conn, keepAlive);
                }
            }
            if (path == "/api/cloud-config" && req.Method == "POST")
            {
                if (!string.IsNullOrEmpty(body))
                {
                    Match m = Regex.Match(body, "\"cloud_url\"\\s*:\\s*\"([^\"]+)\"");
                    if (m.Success)
                    {
                        string msg;
                        SyncFromCloud(m.Groups[1].Value, out msg);
                    }
                }
                return StartSendSingle(conn, keepAlive ? HeaderOkKeep : HeaderOkClose, OkStatusBytes, keepAlive);
            }
            if (path.StartsWith("/", StringComparison.Ordinal))
            {
                string keyName = path.TrimStart('/');
                StaticAssetEntry asset;
                if (snap.Assets.TryGetValue(keyName, out asset))
                {
                    return StartSendPrepared(conn, asset.Payload, req.AcceptsGzip, req.IfNoneMatch, keepAlive, isHead);
                }
            }
            if (path == "/Codice_Treppio_Conde.exe" || path == "/Codice_Treppio_Conde.apk" || path == "/dist/Codice_Treppio_Portatil.html")
            {
                string diskPath = ResolveDownloadArtifact(path.TrimStart('/').Replace('/', Path.DirectorySeparatorChar));
                if (diskPath != null)
                {
                    string mime = path.EndsWith(".html", StringComparison.OrdinalIgnoreCase) ? "text/html; charset=utf-8" : "application/octet-stream";
                    FileInfo fi = new FileInfo(diskPath);
                    long len = fi.Exists ? fi.Length : 0;
                    byte[] hdr = BuildHeaderBytes("200 OK", mime, len, false, null, "no-cache", keepAlive);
                    if (isHead || len == 0)
                    {
                        return StartSendSingle(conn, hdr, null, keepAlive);
                    }
                    try
                    {
                        FileStream fs = new FileStream(diskPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite, 65536, FileOptions.SequentialScan);
                        conn.ActiveFileStream = fs;
                        conn.FileRemaining = len;
                        conn.FileChunkBuf = new byte[65536];
                        conn.KeepAliveAfterSend = keepAlive;
                        Volatile.Write(ref conn.Phase, PhaseStreamingFile);
                        return SendSingleBufferAsync(conn, hdr, 0, hdr.Length);
                    }
                    catch { }
                }
                return StartSendSingle(conn, keepAlive ? HeaderArtNotFoundKeep : HeaderArtNotFoundClose, isHead ? null : ArtifactNotFoundBytes, keepAlive);
            }

            return StartSendSingle(conn, keepAlive ? HeaderNotFoundKeep : HeaderNotFoundClose, isHead ? null : NotFoundBytes, keepAlive);
        }

        private int StartSendPrepared(ConnState conn, PreparedPayload p, bool acceptsGzip, string ifNoneMatch, bool keepAlive, bool isHead)
        {
            if (MatchesIfNoneMatch(ifNoneMatch, p.ETag))
            {
                byte[] hdr304 = keepAlive ? p.Hdr304Keep : p.Hdr304Close;
                return StartSendSingle(conn, hdr304, null, keepAlive);
            }

            bool useGz = acceptsGzip && p.GzipBytes != null;
            if (useGz)
            {
                byte[] hdr = keepAlive ? p.HdrGzKeep : p.HdrGzClose;
                return StartSendSingle(conn, hdr, isHead ? null : p.GzipBytes, keepAlive);
            }

            byte[] rawHdr = keepAlive ? p.HdrRawKeep : p.HdrRawClose;
            if (isHead || p.RawParts == null || p.RawParts.Length == 0)
            {
                return StartSendSingle(conn, rawHdr, null, keepAlive);
            }

            conn.SendSegs.Clear();
            conn.SendSegs.Add(new ArraySegment<byte>(rawHdr));
            for (int i = 0; i < p.RawParts.Length; i++)
            {
                byte[] part = p.RawParts[i];
                if (part != null && part.Length > 0) conn.SendSegs.Add(new ArraySegment<byte>(part));
            }
            return StartSendSegs(conn, keepAlive);
        }

        private int StartSendSingle(ConnState conn, byte[] hdr, byte[] body, bool keepAlive)
        {
            conn.SendSegs.Clear();
            conn.SendSegs.Add(new ArraySegment<byte>(hdr));
            if (body != null && body.Length > 0) conn.SendSegs.Add(new ArraySegment<byte>(body));
            return StartSendSegs(conn, keepAlive);
        }

        private int SendSingleBufferAsync(ConnState conn, byte[] buf, int off, int count)
        {
            conn.SendSegs.Clear();
            conn.SendBatchBytes = count;
            conn.WriteSaea.BufferList = null;
            conn.WriteSaea.SetBuffer(buf, off, count);
            conn.Touch();
            bool pending;
            try { pending = conn.Sock.SendAsync(conn.WriteSaea); }
            catch { CloseAndRecycle(conn); return -1; }
            return pending ? -1 : ModeWriteCompleted;
        }

        private int StartSendSegs(ConnState conn, bool keepAlive)
        {
            conn.KeepAliveAfterSend = keepAlive;
            conn.SendSegIdx = 0;
            conn.SendSegOff = 0;
            Volatile.Write(ref conn.Phase, PhaseSending);

            if (conn.SendSegs.Count == 1)
            {
                ArraySegment<byte> seg = conn.SendSegs[0];
                conn.SendBatchBytes = seg.Count;
                conn.WriteSaea.BufferList = null;
                conn.WriteSaea.SetBuffer(seg.Array, seg.Offset, seg.Count);
            }
            else
            {
                conn.SendActiveList.Clear();
                long sum = 0;
                for (int i = 0; i < conn.SendSegs.Count; i++)
                {
                    conn.SendActiveList.Add(conn.SendSegs[i]);
                    sum += conn.SendSegs[i].Count;
                }
                conn.SendBatchBytes = sum;
                conn.WriteSaea.SetBuffer(null, 0, 0);
                conn.WriteSaea.BufferList = null;
                conn.WriteSaea.BufferList = conn.SendActiveList;
            }

            conn.Touch();
            bool pending;
            try { pending = conn.Sock.SendAsync(conn.WriteSaea); }
            catch { CloseAndRecycle(conn); return -1; }
            return pending ? -1 : ModeWriteCompleted;
        }

        private bool AdvanceSendOrFinish(ConnState conn, int bytesSent, out int nextMode)
        {
            nextMode = -1;
            int phase = Volatile.Read(ref conn.Phase);

            if (phase == PhaseStreamingFile)
            {
                if (conn.ActiveFileStream != null)
                {
                    if (conn.SendBatchBytes > 0 && bytesSent < conn.SendBatchBytes)
                    {
                        byte[] curBuf = conn.WriteSaea.Buffer;
                        int curOff = conn.WriteSaea.Offset + bytesSent;
                        int rem = (int)(conn.SendBatchBytes - bytesSent);
                        conn.SendBatchBytes = rem;
                        conn.WriteSaea.BufferList = null;
                        conn.WriteSaea.SetBuffer(curBuf, curOff, rem);
                        bool pPartial;
                        try { pPartial = conn.Sock.SendAsync(conn.WriteSaea); }
                        catch { CloseAndRecycle(conn); return false; }
                        nextMode = pPartial ? -1 : ModeWriteCompleted;
                        return true;
                    }

                    if (conn.FileRemaining > 0)
                    {
                        int toRead = (int)Math.Min(conn.FileChunkBuf.Length, conn.FileRemaining);
                        int readN = conn.ActiveFileStream.Read(conn.FileChunkBuf, 0, toRead);
                        if (readN > 0)
                        {
                            conn.FileRemaining -= readN;
                            conn.SendBatchBytes = readN;
                            conn.WriteSaea.BufferList = null;
                            conn.WriteSaea.SetBuffer(conn.FileChunkBuf, 0, readN);
                            bool pChunk;
                            try { pChunk = conn.Sock.SendAsync(conn.WriteSaea); }
                            catch { CloseAndRecycle(conn); return false; }
                            nextMode = pChunk ? -1 : ModeWriteCompleted;
                            return true;
                        }
                    }

                    try { conn.ActiveFileStream.Dispose(); } catch { }
                    conn.ActiveFileStream = null;
                    conn.FileChunkBuf = null;
                }
                if (!conn.KeepAliveAfterSend)
                {
                    CloseAndRecycle(conn);
                    return false;
                }
                nextMode = ModeStartRead;
                return true;
            }

            if (bytesSent < conn.SendBatchBytes)
            {
                int remSkip = bytesSent;
                while (remSkip > 0 && conn.SendSegIdx < conn.SendSegs.Count)
                {
                    ArraySegment<byte> seg = conn.SendSegs[conn.SendSegIdx];
                    int avail = seg.Count - conn.SendSegOff;
                    if (remSkip >= avail)
                    {
                        remSkip -= avail;
                        conn.SendSegIdx++;
                        conn.SendSegOff = 0;
                    }
                    else
                    {
                        conn.SendSegOff += remSkip;
                        remSkip = 0;
                    }
                }

                if (conn.SendSegIdx < conn.SendSegs.Count)
                {
                    conn.SendActiveList.Clear();
                    long remTotal = 0;
                    ArraySegment<byte> first = conn.SendSegs[conn.SendSegIdx];
                    int fLen = first.Count - conn.SendSegOff;
                    conn.SendActiveList.Add(new ArraySegment<byte>(first.Array, first.Offset + conn.SendSegOff, fLen));
                    remTotal += fLen;
                    for (int i = conn.SendSegIdx + 1; i < conn.SendSegs.Count; i++)
                    {
                        conn.SendActiveList.Add(conn.SendSegs[i]);
                        remTotal += conn.SendSegs[i].Count;
                    }
                    conn.SendBatchBytes = remTotal;
                    conn.WriteSaea.SetBuffer(null, 0, 0);
                    conn.WriteSaea.BufferList = null;
                    conn.WriteSaea.BufferList = conn.SendActiveList;
                    bool pRem;
                    try { pRem = conn.Sock.SendAsync(conn.WriteSaea); }
                    catch { CloseAndRecycle(conn); return false; }
                    nextMode = pRem ? -1 : ModeWriteCompleted;
                    return true;
                }
            }

            conn.SendSegs.Clear();
            conn.SendActiveList.Clear();
            if (!conn.KeepAliveAfterSend)
            {
                CloseAndRecycle(conn);
                return false;
            }
            nextMode = ModeStartRead;
            return true;
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

        private static int FindHeaderEnd(byte[] buf, int offset, int len)
        {
            int end = offset + len - 4;
            for (int i = offset; i <= end; i++)
            {
                if (buf[i] == 13 && buf[i + 1] == 10 && buf[i + 2] == 13 && buf[i + 3] == 10)
                {
                    return i - offset;
                }
            }
            return -1;
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
            sb.Append("{\"ok\":true,\"version\":\"9.0.0\",\"port\":");
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
            pair = new CachedBytePair
            {
                Payload = BuildPreparedPayload("application/json; charset=utf-8", "no-cache", true, false, raw)
            };
            _apiLru.Put(cacheKey, pair);
            return pair;
        }

        private static bool MatchesIfNoneMatch(string ifNoneMatch, string etag)
        {
            if (string.IsNullOrEmpty(ifNoneMatch) || string.IsNullOrEmpty(etag)) return false;
            string trim = ifNoneMatch.Trim();
            if (trim == "*" || trim == etag) return true;
            return trim.IndexOf(etag, StringComparison.Ordinal) >= 0;
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
        private Label _lblFeedback;

        private TextBox _txtIpaInput;
        private TextBox _txtIpaOutput;

        private RadioButton _rbPtToTr;
        private RadioButton _rbTrToPt;
        private TextBox _txtTransInput;
        private TextBox _txtTransOutput;
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
            Text = "Códice Imperial Tréppio";
            Icon formIco = TryLoadFormIcon();
            if (formIco != null) Icon = formIco;

            ClientSize = new Size(760, 520);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(9, 9, 11);
            ForeColor = Color.FromArgb(244, 244, 245);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;

            Font titleFont = new Font("Segoe UI", 13.5f, FontStyle.Bold);
            Font subFont = new Font("Segoe UI", 9f, FontStyle.Regular);
            Font boldFont = new Font("Segoe UI", 9.5f, FontStyle.Bold);
            Font monoFont = new Font("Consolas", 9.5f, FontStyle.Regular);

            Panel goldTopBar = new Panel { Dock = DockStyle.Top, Height = 2, Width = 760, BackColor = Color.FromArgb(212, 175, 55) };
            Panel headerPanel = new Panel { Dock = DockStyle.Top, Height = 74, Width = 760, BackColor = Color.FromArgb(17, 17, 21) };

            Control crestControl;
            Image crestImg = TryLoadCrestImage();
            if (crestImg != null)
            {
                crestControl = new PictureBox
                {
                    Image = crestImg,
                    SizeMode = PictureBoxSizeMode.Zoom,
                    BackColor = Color.Transparent,
                    Size = new Size(46, 46),
                    Location = new Point(20, 14)
                };
            }
            else
            {
                crestControl = new Label
                {
                    Text = "C",
                    Font = new Font("Segoe UI", 17f, FontStyle.Bold),
                    ForeColor = Color.Gold,
                    BackColor = Color.FromArgb(26, 26, 32),
                    TextAlign = ContentAlignment.MiddleCenter,
                    Size = new Size(46, 46),
                    Location = new Point(20, 14)
                };
            }
            Label lblTitle = new Label
            {
                Text = "CÓDICE TRÉPPIO",
                Font = titleFont,
                ForeColor = Color.White,
                AutoSize = true,
                Location = new Point(78, 14)
            };
            _lblSubtitle = new Label
            {
                Text = "Dicionário, Pronúncia e Tradutor",
                Font = subFont,
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = true,
                Location = new Point(80, 41)
            };
            Button btnSettings = CreateStyledButton(
                "Ajustes",
                new Point(656, 21),
                new Size(84, 32),
                Color.FromArgb(24, 24, 30),
                Color.FromArgb(228, 228, 231)
            );
            btnSettings.Font = new Font("Segoe UI", 8.8f, FontStyle.Bold);
            btnSettings.FlatAppearance.BorderColor = Color.FromArgb(63, 63, 74);
            btnSettings.Click += (s, e) => OpenSettingsDialog();
            headerPanel.Resize += (s, e) =>
            {
                btnSettings.Location = new Point(Math.Max(520, headerPanel.ClientSize.Width - btnSettings.Width - 20), 21);
            };

            headerPanel.Controls.Add(crestControl);
            headerPanel.Controls.Add(lblTitle);
            headerPanel.Controls.Add(_lblSubtitle);
            headerPanel.Controls.Add(btnSettings);

            _tabs = new TabControl
            {
                Dock = DockStyle.Fill,
                DrawMode = TabDrawMode.OwnerDrawFixed,
                SizeMode = TabSizeMode.Fixed,
                ItemSize = new Size(251, 36),
                Font = boldFont
            };
            _tabs.Resize += (s, e) =>
            {
                int w = Math.Max(160, (_tabs.ClientSize.Width - 6) / 3);
                if (_tabs.ItemSize.Width != w) _tabs.ItemSize = new Size(w, 36);
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
            TabPage page = new TabPage("  Principal  ")
            {
                BackColor = Color.FromArgb(9, 9, 11),
                ForeColor = Color.FromArgb(244, 244, 245),
                Padding = new Padding(16)
            };

            Label lblIntro = new Label
            {
                Text = "Acesse a edição completa no navegador ou pratique diálogos por voz.",
                Font = subFont,
                ForeColor = Color.FromArgb(161, 161, 170),
                AutoSize = false,
                TextAlign = ContentAlignment.MiddleCenter,
                Size = new Size(660, 28),
                Location = new Point(46, 86)
            };
            page.Controls.Add(lblIntro);

            Button btnOpenApp = CreateStyledButton(
                "Abrir Códice Completo",
                new Point(146, 134),
                new Size(460, 50),
                Color.White,
                Color.FromArgb(9, 9, 11)
            );
            btnOpenApp.Font = new Font("Segoe UI", 10.5f, FontStyle.Bold);
            btnOpenApp.FlatAppearance.BorderSize = 0;
            btnOpenApp.Click += (s, e) => LaunchDedicatedWindow();
            page.Controls.Add(btnOpenApp);

            Button btnVoiceWhisper = CreateStyledButton(
                "Conversar por Voz",
                new Point(146, 198),
                new Size(460, 44),
                Color.FromArgb(18, 24, 22),
                Color.FromArgb(52, 211, 153)
            );
            btnVoiceWhisper.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            btnVoiceWhisper.FlatAppearance.BorderColor = Color.FromArgb(52, 211, 153);
            btnVoiceWhisper.Click += (s, e) => LaunchWhisperVoiceGui();
            page.Controls.Add(btnVoiceWhisper);

            _lblFeedback = new Label
            {
                Text = "Pronto.",
                Font = subFont,
                ForeColor = Color.FromArgb(130, 130, 142),
                AutoSize = false,
                TextAlign = ContentAlignment.MiddleCenter,
                Size = new Size(660, 36),
                Location = new Point(46, 336)
            };
            page.Controls.Add(_lblFeedback);

            return page;
        }

        private TabPage BuildPhoneticsTab(Font subFont, Font boldFont, Font monoFont)
        {
            TabPage page = new TabPage("  Pronúncia  ")
            {
                BackColor = Color.FromArgb(9, 9, 11),
                ForeColor = Color.FromArgb(244, 244, 245),
                Padding = new Padding(16)
            };

            Label lblBanner = new Label
            {
                Text = "Regras essenciais: G = /ɡ/ (guitarra)   •   S = /s/ (sapato)   •   ' = corte silábico [ʔ]",
                Font = boldFont,
                ForeColor = Color.FromArgb(253, 226, 142),
                BackColor = Color.FromArgb(18, 18, 22),
                BorderStyle = BorderStyle.FixedSingle,
                TextAlign = ContentAlignment.MiddleLeft,
                Padding = new Padding(10, 0, 10, 0),
                Size = new Size(708, 34),
                Location = new Point(22, 16)
            };
            page.Controls.Add(lblBanner);

            _txtIpaInput = new TextBox
            {
                Location = new Point(22, 62),
                Size = new Size(548, 30),
                BackColor = Color.FromArgb(17, 17, 21),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = monoFont,
                Text = "Haly'itror giza in oxej: falde, Vé, rase, ve'ar et Tepy'atte"
            };
            _txtIpaInput.TextChanged += (s, e) => RunIpaAnalysis();
            page.Controls.Add(_txtIpaInput);

            Button btnSpeak = CreateStyledButton(
                "Analisar e Ouvir",
                new Point(580, 61),
                new Size(150, 32),
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
            Font chipFont = new Font("Consolas", 8.5f, FontStyle.Regular);
            for (int i = 0; i < samples.Length; i++)
            {
                string tok = samples[i];
                Button b = CreateStyledButton(tok, new Point(chipX, 102), new Size(84, 28), Color.FromArgb(24, 24, 28), Color.White);
                b.Font = chipFont;
                b.Click += (s, e) =>
                {
                    _txtIpaInput.Text = tok;
                    RunIpaAnalysis();
                    _tts.SpeakAsync(TreppioLexiconEngine.ApplyHaplology(tok));
                };
                page.Controls.Add(b);
                chipX += 89;
            }

            _txtIpaOutput = new TextBox
            {
                Location = new Point(22, 140),
                Size = new Size(708, 240),
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
            TabPage page = new TabPage("  Tradutor  ")
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
                Location = new Point(22, 16)
            };
            _rbTrToPt = new RadioButton
            {
                Text = "Tréppio -> Português",
                AutoSize = true,
                Font = boldFont,
                ForeColor = Color.FromArgb(244, 244, 245),
                Location = new Point(210, 16)
            };
            _rbPtToTr.CheckedChanged += (s, e) => { if (_rbPtToTr.Checked) RunTranslation(); };
            _rbTrToPt.CheckedChanged += (s, e) => { if (_rbTrToPt.Checked) RunTranslation(); };
            page.Controls.Add(_rbPtToTr);
            page.Controls.Add(_rbTrToPt);

            _txtTransInput = new TextBox
            {
                Location = new Point(22, 48),
                Size = new Size(468, 30),
                BackColor = Color.FromArgb(17, 17, 21),
                ForeColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle,
                Font = new Font("Segoe UI", 10.5f, FontStyle.Regular),
                Text = "pão e água na casa"
            };
            _txtTransInput.KeyDown += (s, e) => { if (e.KeyCode == Keys.Enter) { e.SuppressKeyPress = true; RunTranslation(); } };
            page.Controls.Add(_txtTransInput);

            Button btnTranslate = CreateStyledButton(
                "Traduzir",
                new Point(500, 47),
                new Size(110, 32),
                Color.White,
                Color.FromArgb(9, 9, 11)
            );
            btnTranslate.FlatAppearance.BorderSize = 0;
            btnTranslate.Click += (s, e) => RunTranslation();
            page.Controls.Add(btnTranslate);

            Button btnSpeakRes = CreateStyledButton(
                "Ouvir",
                new Point(620, 47),
                new Size(110, 32),
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
                Location = new Point(22, 90),
                Size = new Size(708, 290),
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
                RunTranslation();
                if (_lblFeedback != null && !_lblFeedback.IsDisposed)
                {
                    _lblFeedback.ForeColor = Color.FromArgb(130, 130, 142);
                    _lblFeedback.Text = "Pronto.";
                }
            }
            else
            {
                if (_lblFeedback != null && !_lblFeedback.IsDisposed)
                {
                    _lblFeedback.ForeColor = Color.FromArgb(161, 161, 170);
                    _lblFeedback.Text = "Carregando índice lexical...";
                }
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
            sb.AppendLine("Transcrição IPA:  [" + string.Join(" ", fullIpa.ToArray()) + "]");
            sb.AppendLine("Grafia Canônica:  " + string.Join(" ", normalizedWords.ToArray()));
            sb.AppendLine();
            sb.Append(cardSb.ToString());
            sb.AppendLine();
            sb.AppendLine("Guia Fonético:");
            sb.AppendLine("  G / g -> /ɡ/ (sempre gutural)    |  S / s -> /s/ (sempre surdo)");
            sb.AppendLine("  '     -> [ʔ] (corte silábico)    |  X / x -> /x/");
            sb.AppendLine("  R / r -> /ɾ/ vs rr -> /r/        |  Ë / ë -> /ə/");
            sb.AppendLine("  Y / y -> /i/                     |  J / j -> /j/");
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

        private void RefreshMetricsUi()
        {
            RefreshIndexStatusUi();
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

        private void OpenSettingsDialog()
        {
            LauncherForm owner = this;
            using (Form dlg = new Form())
            {
                dlg.Text = "Ajustes — Códice Tréppio";
                dlg.ClientSize = new Size(540, 260);
                dlg.StartPosition = FormStartPosition.CenterParent;
                dlg.FormBorderStyle = FormBorderStyle.FixedDialog;
                dlg.MaximizeBox = false;
                dlg.MinimizeBox = false;
                dlg.BackColor = Color.FromArgb(14, 14, 18);
                dlg.ForeColor = Color.FromArgb(244, 244, 245);
                dlg.HandleCreated += (s, e) => EnableDarkMode(dlg.Handle);

                Font subFont = new Font("Segoe UI", 9f, FontStyle.Regular);
                Font monoFont = new Font("Consolas", 9.5f, FontStyle.Regular);

                Label lblCloud = new Label
                {
                    Text = "URL de Sincronização Online:",
                    Font = subFont,
                    ForeColor = Color.FromArgb(161, 161, 170),
                    AutoSize = true,
                    Location = new Point(22, 20)
                };
                TextBox txtCloudUrl = new TextBox
                {
                    Location = new Point(22, 44),
                    Size = new Size(496, 28),
                    BackColor = Color.FromArgb(17, 17, 21),
                    ForeColor = Color.White,
                    BorderStyle = BorderStyle.FixedSingle,
                    Font = monoFont,
                    Text = _server.CloudUrl
                };
                Button btnSync = CreateStyledButton(
                    "Sincronizar Online",
                    new Point(22, 86),
                    new Size(240, 38),
                    Color.FromArgb(24, 24, 28),
                    Color.FromArgb(244, 244, 245)
                );
                Button btnRecompile = CreateStyledButton(
                    "Recompilar Base Local",
                    new Point(278, 86),
                    new Size(240, 38),
                    Color.FromArgb(24, 24, 28),
                    Color.FromArgb(244, 244, 245)
                );
                Label lblDlgStatus = new Label
                {
                    Text = "Fonte ativa: " + Regex.Replace(_server.ActiveSource ?? "", @"\s*\([^)]*\)\s*$", ""),
                    Font = subFont,
                    ForeColor = Color.FromArgb(161, 161, 170),
                    AutoSize = false,
                    Size = new Size(496, 48),
                    Location = new Point(22, 138)
                };
                Button btnClose = CreateStyledButton(
                    "Fechar",
                    new Point(408, 202),
                    new Size(110, 34),
                    Color.FromArgb(28, 28, 34),
                    Color.White
                );
                btnClose.DialogResult = DialogResult.OK;

                btnSync.Click += (s, e) =>
                {
                    string url = txtCloudUrl.Text;
                    btnSync.Enabled = false;
                    btnRecompile.Enabled = false;
                    lblDlgStatus.ForeColor = Color.FromArgb(253, 226, 142);
                    lblDlgStatus.Text = "Sincronizando base online...";
                    ThreadPool.QueueUserWorkItem(_ =>
                    {
                        string msg;
                        bool ok = _server.SyncFromCloud(url, out msg);
                        if (owner.IsHandleCreated && !owner.IsDisposed)
                        {
                            try
                            {
                                owner.BeginInvoke((Action)(() =>
                                {
                                    if (owner.IsDisposed) return;
                                    owner.RefreshMetricsUi();
                                    if (owner._lblFeedback != null && !owner._lblFeedback.IsDisposed)
                                    {
                                        owner._lblFeedback.ForeColor = ok ? Color.FromArgb(52, 199, 135) : Color.FromArgb(226, 92, 104);
                                        owner._lblFeedback.Text = msg;
                                    }
                                    if (!dlg.IsDisposed)
                                    {
                                        btnSync.Enabled = true;
                                        btnRecompile.Enabled = true;
                                        lblDlgStatus.ForeColor = ok ? Color.FromArgb(52, 199, 135) : Color.FromArgb(226, 92, 104);
                                        lblDlgStatus.Text = msg;
                                    }
                                }));
                            }
                            catch { }
                        }
                    });
                };

                btnRecompile.Click += (s, e) =>
                {
                    btnSync.Enabled = false;
                    btnRecompile.Enabled = false;
                    lblDlgStatus.ForeColor = Color.FromArgb(253, 226, 142);
                    lblDlgStatus.Text = "Recompilando base local...";
                    ThreadPool.QueueUserWorkItem(_ =>
                    {
                        string msg;
                        bool ok = _server.RecompileLocalConde(out msg);
                        if (owner.IsHandleCreated && !owner.IsDisposed)
                        {
                            try
                            {
                                owner.BeginInvoke((Action)(() =>
                                {
                                    if (owner.IsDisposed) return;
                                    owner.RefreshMetricsUi();
                                    if (owner._lblFeedback != null && !owner._lblFeedback.IsDisposed)
                                    {
                                        owner._lblFeedback.ForeColor = ok ? Color.FromArgb(52, 199, 135) : Color.FromArgb(226, 92, 104);
                                        owner._lblFeedback.Text = msg;
                                    }
                                    if (!dlg.IsDisposed)
                                    {
                                        btnSync.Enabled = true;
                                        btnRecompile.Enabled = true;
                                        lblDlgStatus.ForeColor = ok ? Color.FromArgb(52, 199, 135) : Color.FromArgb(226, 92, 104);
                                        lblDlgStatus.Text = msg;
                                    }
                                }));
                            }
                            catch { }
                        }
                    });
                };

                dlg.AcceptButton = btnClose;
                dlg.CancelButton = btnClose;
                dlg.Shown += (s, e) =>
                {
                    txtCloudUrl.SelectionStart = 0;
                    txtCloudUrl.SelectionLength = 0;
                    btnClose.Focus();
                };
                dlg.Controls.Add(lblCloud);
                dlg.Controls.Add(txtCloudUrl);
                dlg.Controls.Add(btnSync);
                dlg.Controls.Add(btnRecompile);
                dlg.Controls.Add(lblDlgStatus);
                dlg.Controls.Add(btnClose);
                dlg.ShowDialog(this);
            }
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
                _lblFeedback.Text = "Interface de conversação por voz iniciada.";
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
            bool bindMulti = false;
            int requestedPort = 0;
            int maxConn = 0;

            if (args != null)
            {
                for (int i = 0; i < args.Length; i++)
                {
                    if (args[i] == "--test-headless") testHeadless = true;
                    else if (args[i] == "--serve-only") serveOnly = true;
                    else if (args[i] == "--bind-multi") bindMulti = true;
                    else if (args[i] == "--port" && i + 1 < args.Length)
                    {
                        int p;
                        if (int.TryParse(args[++i], out p) && p >= 0) requestedPort = p;
                    }
                    else if (args[i] == "--max-conn" && i + 1 < args.Length)
                    {
                        int mc;
                        if (int.TryParse(args[++i], out mc) && mc > 0) maxConn = mc;
                    }
                }
            }

            EmbeddedServer server = new EmbeddedServer();
            if (requestedPort > 0) server.PreferredPort = requestedPort;
            if (bindMulti) server.BindMultiLoopback = true;
            if (maxConn > 0) server.MaxConcurrentConnections = maxConn;
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
                        string svgText = wc.DownloadString(baseUrl + "/brasao_conde.svg");
                        string ipaJson = wc.DownloadString(baseUrl + "/api/ipa?q=vevar");
                        string apiTransJson = wc.DownloadString(baseUrl + "/api/traduzir?dir=pt-tr&q=" + Uri.EscapeDataString("pão"));
                        string apiSearchJson = wc.DownloadString(baseUrl + "/api/search?q=falde&limit=5");
                        bool apisOk = healthJson.Contains("\"ok\":true")
                                   && healthJson.Contains("\"version\":\"9.0.0\"")
                                   && svgText.Contains("<svg")
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
