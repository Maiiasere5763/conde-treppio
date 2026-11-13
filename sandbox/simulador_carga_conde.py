#!/usr/bin/env python3
"""Simulador de Carga Concorrente (100 e 1.000 usuarios simultaneos) para o Codice Treppio."""

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from collections import Counter

import aiohttp


def percentile(sorted_vals, pct):
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * pct / 100.0
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


async def fetch_stream(session, url, headers=None):
    t0 = time.perf_counter()
    total_bytes = 0
    try:
        async with session.get(url, headers=headers) as resp:
            status = resp.status
            async for chunk in resp.content.iter_chunked(65536):
                total_bytes += len(chunk)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return status, total_bytes, elapsed_ms, None
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return 0, total_bytes, elapsed_ms, f"{type(exc).__name__}: {exc}"


async def user_journey(
    user_id,
    base_url,
    connector_factory_session,
    include_heavy,
    test_dynamic_api,
    results,
):
    queries_pt = ["pao", "agua", "fogo", "estrela", "coracao", "casa", "espada"]
    queries_tr = ["Haly'itror", "giza", "esur", "ve'ar", "Faldem et Véom pasum"]
    q_pt = queries_pt[user_id % len(queries_pt)]
    q_tr = queries_tr[user_id % len(queries_tr)]

    endpoints = [
        (f"{base_url}/icon-512.png", {"Accept-Encoding": "gzip"}),
        (f"{base_url}/manifest.json", {"Accept-Encoding": "gzip"}),
    ]
    if include_heavy and user_id % 10 == 0:
        endpoints.append((f"{base_url}/", {"Accept-Encoding": "gzip"}))
        endpoints.append((f"{base_url}/dados_dicionario_conde.js", {"Accept-Encoding": "gzip"}))
    elif user_id % 4 == 0:
        endpoints.append((f"{base_url}/", {"Accept-Encoding": "gzip"}))

    if test_dynamic_api:
        endpoints.append((f"{base_url}/api/health", {"Accept-Encoding": "gzip"}))
        endpoints.append((f"{base_url}/api/traduzir?dir=pt-tr&q={q_pt}", {"Accept-Encoding": "gzip"}))
        endpoints.append((f"{base_url}/api/ipa?q={q_tr}", {"Accept-Encoding": "gzip"}))
        endpoints.append((f"{base_url}/api/search?q={q_pt}", {"Accept-Encoding": "gzip"}))

    for url, hdrs in endpoints:
        status, nbytes, ms, err = await fetch_stream(connector_factory_session, url, hdrs)
        results.append((status, nbytes, ms, err))


async def run_wave(base_url, users, force_close, include_heavy, test_dynamic_api, timeout_s):
    if sys.platform.startswith("win"):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            pass

    connector = aiohttp.TCPConnector(
        limit=0,
        limit_per_host=0,
        force_close=force_close,
        enable_cleanup_closed=True,
    )
    timeout = aiohttp.ClientTimeout(total=timeout_s, connect=min(15.0, timeout_s))
    results = []

    t_start = time.perf_counter()
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, auto_decompress=False) as session:
        tasks = [
            asyncio.create_task(
                user_journey(uid, base_url, session, include_heavy, test_dynamic_api, results)
            )
            for uid in range(users)
        ]
        await asyncio.gather(*tasks)
    wall_s = time.perf_counter() - t_start

    latencies = sorted(r[2] for r in results)
    statuses = Counter(r[0] for r in results)
    errors = Counter(r[3] for r in results if r[3])
    total_bytes = sum(r[1] for r in results)
    ok_count = sum(cnt for code, cnt in statuses.items() if code in (200, 304))
    fail_count = len(results) - ok_count

    return {
        "mode": "burst_close" if force_close else "keep_alive",
        "users": users,
        "requests": len(results),
        "wall_seconds": round(wall_s, 3),
        "rps": round(len(results) / wall_s, 1) if wall_s > 0 else 0.0,
        "wire_mb": round(total_bytes / (1024 * 1024), 2),
        "wire_mb_per_s": round((total_bytes / (1024 * 1024)) / wall_s, 2) if wall_s > 0 else 0.0,
        "ok": ok_count,
        "fail": fail_count,
        "error_rate_pct": round((fail_count * 100.0) / max(1, len(results)), 2),
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "p99_ms": round(percentile(latencies, 99), 2),
        "max_ms": round(latencies[-1], 2) if latencies else 0.0,
        "statuses": dict(statuses),
        "top_errors": errors.most_common(5),
    }


async def main_async(args):
    modes = [False, True] if args.mode == "both" else ([False] if args.mode == "keepalive" else [True])
    report = {
        "base_url": args.url,
        "users": args.users,
        "waves": [],
    }
    for force_close in modes:
        res = await run_wave(
            base_url=args.url.rstrip("/"),
            users=args.users,
            force_close=force_close,
            include_heavy=not args.light_only,
            test_dynamic_api=not args.static_only,
            timeout_s=args.timeout,
        )
        report["waves"].append(res)
        await asyncio.sleep(0.5)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    total_fails = sum(w["fail"] for w in report["waves"])
    if args.strict and total_fails > 0:
        sys.exit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark de carga 100/1000 usuarios - Codice Treppio")
    parser.add_argument("--url", default="http://127.0.0.1:8766")
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--mode", choices=["keepalive", "burst", "both"], default="both")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--light-only", action="store_true")
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--strict", action="store_true")
    cli_args = parser.parse_args()
    asyncio.run(main_async(cli_args))

