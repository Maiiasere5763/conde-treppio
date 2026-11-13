import asyncio
import ctypes
import json
import math
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ENDPOINTS = [
    b"GET /api/health HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: keep-alive\r\n\r\n",
    b"GET /brasao_conde.svg HTTP/1.1\r\nHost: 127.0.0.1\r\nAccept-Encoding: gzip\r\nConnection: keep-alive\r\n\r\n",
    b"GET /api/ipa?q=vevar HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: keep-alive\r\n\r\n",
    b"GET /api/traduzir?dir=pt-tr&q=p%C3%A3o HTTP/1.1\r\nHost: 127.0.0.1\r\nAccept-Encoding: gzip\r\nConnection: keep-alive\r\n\r\n",
    b"GET /api/search?q=falde&limit=8 HTTP/1.1\r\nHost: 127.0.0.1\r\nAccept-Encoding: gzip\r\nConnection: keep-alive\r\n\r\n",
    b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\nAccept-Encoding: gzip\r\nConnection: keep-alive\r\n\r\n",
]

DADOS_REQ = b"GET /dados_dicionario_conde.js HTTP/1.1\r\nHost: 127.0.0.1\r\nAccept-Encoding: gzip\r\nConnection: keep-alive\r\n\r\n"


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def get_avail_phys_mb():
    st = MEMORYSTATUSEX()
    st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
        return st.ullAvailPhys / (1024.0 * 1024.0)
    return 4096.0


def parse_http_response(buf):
    hdr_end = buf.find(b"\r\n\r\n")
    if hdr_end < 0:
        return None
    hdr = buf[:hdr_end]
    first_nl = hdr.find(b"\r\n")
    status_line = hdr[:first_nl] if first_nl >= 0 else hdr
    parts = status_line.split(b" ", 2)
    status = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
    cl = 0
    for line in hdr.split(b"\r\n")[1:]:
        if line.lower().startswith(b"content-length:"):
            try:
                cl = int(line.split(b":", 1)[1].strip())
            except Exception:
                cl = 0
            break
    total_need = hdr_end + 4 + cl
    if len(buf) < total_need:
        return None
    return status, total_need


async def open_and_hold_worker(worker_id, port, count, hold_sec, rounds, req_timeout, hold_mode, bind_ips, port_base, out_file):
    loop = asyncio.get_running_loop()
    sockets = []
    latencies_ms = []
    errors = 0
    connect_errors = 0
    http_ok = 0
    http_other = 0

    sem = asyncio.Semaphore(180)

    async def connect_one(idx):
        nonlocal connect_errors
        g_idx = worker_id * count + idx
        ip = bind_ips[g_idx % len(bind_ips)]
        slot = g_idx // len(bind_ips)
        async with sem:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setblocking(False)
            try:
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                if port_base > 0:
                    bound = False
                    for attempt in range(4):
                        try:
                            s.bind((ip, port_base + slot + attempt * 2500))
                            bound = True
                            break
                        except OSError:
                            continue
                    if not bound:
                        s.bind((ip, 0))
                else:
                    s.bind((ip, 0))
                await asyncio.wait_for(loop.sock_connect(s, (ip, port)), timeout=req_timeout)
                sockets.append(s)
            except Exception:
                connect_errors += 1
                try:
                    s.close()
                except Exception:
                    pass

    async def do_one_req(s, req_bytes):
        nonlocal errors, http_ok, http_other
        t0 = time.perf_counter()
        try:
            await asyncio.wait_for(loop.sock_sendall(s, req_bytes), timeout=req_timeout)
            buf = bytearray()
            while True:
                chunk = await asyncio.wait_for(loop.sock_recv(s, 8192), timeout=req_timeout)
                if not chunk:
                    errors += 1
                    return False
                buf.extend(chunk)
                parsed = parse_http_response(buf)
                if parsed is not None:
                    status, _ = parsed
                    dt = (time.perf_counter() - t0) * 1000.0
                    latencies_ms.append(dt)
                    if 200 <= status < 400:
                        http_ok += 1
                    else:
                        http_other += 1
                    return True
        except Exception:
            errors += 1
            return False

    # Stagger connect in waves to avoid Windows SYN queue spikes
    batch_sz = 400
    for start in range(0, count, batch_sz):
        batch = [connect_one(i) for i in range(start, min(count, start + batch_sz))]
        await asyncio.gather(*batch)

    connected = len(sockets)

    if hold_mode == "hold_and_query":
        for r in range(rounds):
            tasks = []
            for idx, s in enumerate(sockets):
                if r == 0 and (idx % 200 == 0):
                    req = DADOS_REQ
                else:
                    req = ENDPOINTS[(idx + r) % len(ENDPOINTS)]
                tasks.append(do_one_req(s, req))
            # Throttle gather batches lightly so Proactor doesn't stall
            for start in range(0, len(tasks), 500):
                await asyncio.gather(*tasks[start : start + 500])
        if hold_sec > 0:
            await asyncio.sleep(hold_sec)
    elif hold_mode == "keepalive_wave":
        # Each open socket executes `rounds` consecutive keep-alive requests simulating multiple wave users
        req_sem = asyncio.Semaphore(min(250, max(32, connected)))

        async def run_socket_wave(s, idx):
            async with req_sem:
                for r in range(rounds):
                    req = ENDPOINTS[(idx + r) % len(ENDPOINTS)]
                    ok = await do_one_req(s, req)
                    if not ok:
                        break

        wave_tasks = [run_socket_wave(s, i) for i, s in enumerate(sockets)]
        await asyncio.gather(*wave_tasks)

    for s in sockets:
        try:
            s.close()
        except Exception:
            pass

    latencies_ms.sort()
    summary = {
        "worker": worker_id,
        "target": count,
        "connected": connected,
        "connect_errors": connect_errors,
        "http_ok": http_ok,
        "http_other": http_other,
        "errors": errors,
        "latencies_sample": latencies_ms[:: max(1, len(latencies_ms) // 1000)] if latencies_ms else [],
        "max_lat": latencies_ms[-1] if latencies_ms else 0.0,
        "count_lat": len(latencies_ms),
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f)


def get_server_metrics(pid, port):
    mem_ws = 0.0
    mem_priv = 0.0
    handles = 0
    health = {}
    try:
        ps_cmd = (
            f"$p = Get-Process -Id {pid} -ErrorAction SilentlyContinue; "
            f"if ($p) {{ \"$($p.WorkingSet64),$($p.PrivateMemorySize64),$($p.HandleCount)\" }}"
        )
        out = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_cmd], text=True, timeout=3).strip()
        if out:
            a, b, c = out.split(",")
            mem_ws = round(int(a) / (1024 * 1024), 2)
            mem_priv = round(int(b) / (1024 * 1024), 2)
            handles = int(c)
    except Exception:
        pass
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=2) as resp:
            health = json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass
    return {"ws_mb": mem_ws, "priv_mb": mem_priv, "handles": handles, "health": health}


def run_distributed_phase(label, server_pid, port, num_workers, per_worker, hold_sec, rounds, req_timeout, hold_mode, port_base=0):
    print(f"\n=== {label} ===")
    print(f"Workers={num_workers}, Sockets/Worker={per_worker} (Total Simultaneous Sockets={num_workers*per_worker}), Mode={hold_mode}, Rounds={rounds}")
    avail_before = round(get_avail_phys_mb(), 1)
    if avail_before < 900:
        print(f"ABORT SAFETY: Avail RAM too low ({avail_before} MB)")
        return None

    tmpdir = tempfile.mkdtemp(prefix="conde_c100k_")
    t_start = time.perf_counter()
    procs = []
    out_files = []
    for w in range(num_workers):
        out_f = os.path.join(tmpdir, f"w_{w}.json")
        out_files.append(out_f)
        cmd = [
            sys.executable,
            __file__,
            "--worker",
            str(w),
            str(port),
            str(per_worker),
            str(hold_sec),
            str(rounds),
            str(req_timeout),
            hold_mode,
            str(port_base),
            out_f,
        ]
        procs.append(subprocess.Popen(cmd))

    peak_ws = 0.0
    peak_priv = 0.0
    peak_conns = 0
    peak_handles = 0
    while any(p.poll() is None for p in procs):
        m = get_server_metrics(server_pid, port)
        peak_ws = max(peak_ws, m["ws_mb"])
        peak_priv = max(peak_priv, m["priv_mb"])
        peak_handles = max(peak_handles, m["handles"])
        ac = m["health"].get("activeConnections", 0)
        peak_conns = max(peak_conns, ac)
        if get_avail_phys_mb() < 750:
            print("WARNING: System free RAM below 750 MB; terminating load workers early for host safety!")
            for p in procs:
                p.terminate()
            break
        time.sleep(0.5)

    for p in procs:
        p.wait()
    elapsed = time.perf_counter() - t_start

    total_connected = 0
    total_conn_err = 0
    total_ok = 0
    total_other = 0
    total_err = 0
    all_lats = []
    max_lat = 0.0
    for fpath in out_files:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            total_connected += d["connected"]
            total_conn_err += d["connect_errors"]
            total_ok += d["http_ok"]
            total_other += d["http_other"]
            total_err += d["errors"]
            all_lats.extend(d["latencies_sample"])
            max_lat = max(max_lat, d["max_lat"])
    all_lats.sort()

    def pct(p):
        if not all_lats:
            return 0.0
        idx = min(len(all_lats) - 1, max(0, int(math.ceil(p * len(all_lats))) - 1))
        return round(all_lats[idx], 2)

    time.sleep(3.5)
    post = get_server_metrics(server_pid, port)
    res = {
        "label": label,
        "target_sockets": num_workers * per_worker,
        "connected_sockets": total_connected,
        "connect_errors": total_conn_err,
        "virtual_users_or_reqs": total_ok + total_other + total_err,
        "http_ok": total_ok,
        "http_other": total_other,
        "errors": total_err,
        "elapsed_sec": round(elapsed, 2),
        "rps": round(total_ok / max(0.01, elapsed), 1),
        "p50_ms": pct(0.50),
        "p95_ms": pct(0.95),
        "p99_ms": pct(0.99),
        "max_ms": round(max_lat, 2),
        "peak_server_active_conns": peak_conns,
        "peak_server_ws_mb": peak_ws,
        "peak_server_priv_mb": peak_priv,
        "peak_server_handles": peak_handles,
        "post_server_ws_mb": post["ws_mb"],
        "post_server_active_conns": post["health"].get("activeConnections", -1),
        "avail_ram_before_mb": avail_before,
        "avail_ram_after_mb": round(get_avail_phys_mb(), 1),
    }
    print(json.dumps(res, indent=2))
    try:
        for fpath in out_files:
            if os.path.exists(fpath):
                os.remove(fpath)
        os.rmdir(tmpdir)
    except Exception:
        pass
    return res


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--worker":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        wid = int(sys.argv[2])
        port = int(sys.argv[3])
        count = int(sys.argv[4])
        hold_sec = float(sys.argv[5])
        rounds = int(sys.argv[6])
        req_timeout = float(sys.argv[7])
        hold_mode = sys.argv[8]
        port_base = int(sys.argv[9])
        out_file = sys.argv[10]
        bind_ips = [f"127.0.0.{i}" for i in range(1, 33)]
        asyncio.run(open_and_hold_worker(wid, port, count, hold_sec, rounds, req_timeout, hold_mode, bind_ips, port_base, out_file))
        return

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8779
    pid = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    if pid == 0:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", "(Get-Process Codice_Treppio_Conde | Select-Object -First 1).Id"],
            text=True,
        ).strip()
        pid = int(out)

    print(f"Target PID={pid}, Port={port}, AvailPhysRAM={round(get_avail_phys_mb(), 1)} MB")
    baseline = get_server_metrics(pid, port)
    print("Baseline server:", json.dumps(baseline))

    # Test 1: 10,000 TRUE simultaneous live keep-alive TCP connections across 127.0.0.1..127.0.0.32
    r1 = run_distributed_phase(
        "PHASE 1: C10K TRUE SIMULTANEOUS (10,000 live TCP keep-alive sockets)",
        pid, port, num_workers=10, per_worker=1000, hold_sec=2.0, rounds=2, req_timeout=15.0, hold_mode="hold_and_query", port_base=10000
    )

    # Test 2: Push simultaneous open connections higher (25,000 live TCP sockets) to measure IOCP/Slab scaling
    r2 = run_distributed_phase(
        "PHASE 2: C25K SIMULTANEOUS SCALING PROBE (25,000 live TCP keep-alive sockets)",
        pid, port, num_workers=10, per_worker=2500, hold_sec=1.5, rounds=1, req_timeout=20.0, hold_mode="hold_and_query", port_base=15000
    )

    # Test 3: 100,000 Simultaneous Virtual Users Wave (20 workers x 1,000 live sockets = 20,000 simultaneous sockets x 5 rapid requests = 100,000 concurrent user workflows)
    r3 = run_distributed_phase(
        "PHASE 3: 100,000 VIRTUAL USERS WAVE (20,000 concurrent sockets x 5 reqs = 100,000 user actions)",
        pid, port, num_workers=20, per_worker=1000, hold_sec=0.0, rounds=5, req_timeout=20.0, hold_mode="keepalive_wave", port_base=20000
    )

    results = {"baseline": baseline, "c10k": r1, "c25k": r2, "c100k_wave": r3}
    print("\n=== ALL BENCHMARKS COMPLETE ===")


if __name__ == "__main__":
    main()

