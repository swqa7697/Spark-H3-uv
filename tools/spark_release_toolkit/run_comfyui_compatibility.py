#!/usr/bin/env python3
"""Short same-shape ComfyUI compatibility check for Dense/Fidelity/Speed."""

from __future__ import annotations

import os
import time

import run_lightx2v_three_variants as bench


def main() -> None:
    bench.ROOT.mkdir(parents=True, exist_ok=True)
    for directory in (
        bench.COMFY_OUTPUT, bench.ROOT / "temp", bench.ROOT / "input", bench.ROOT / "user"
    ):
        directory.mkdir(parents=True, exist_ok=True)

    wheel_audit = bench.prepare_isolated_runtime()
    state = bench.backend_state()
    bench.validate_static(state)
    bench.write_json(bench.ROOT / "wheel_audit.json", wheel_audit)

    log_path = bench.ROOT / "comfyui.log"
    log_handle = log_path.open("w", encoding="utf-8")
    env = {
        **bench.runtime_environment(),
        "CUDA_VISIBLE_DEVICES": "0",
        "HF_HUB_OFFLINE": "1",
        "PYTHONUNBUFFERED": "1",
        "NO_PROXY": "127.0.0.1,localhost",
        "no_proxy": "127.0.0.1,localhost",
        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
    }
    server = bench.launch_server(env, log_handle)
    records = {}
    try:
        stats = bench.wait_server(server)
        bench.write_json(bench.ROOT / "environment.json", bench.environment(stats, state))
        token = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        for index, tier in enumerate(bench.TIERS):
            name = tier["name"]
            prompt = bench.warmup_prompt(bench.formal_prompt(tier, token), tier, token)
            result = bench.run_prompt(
                server, prompt, f"{name}_compatibility", log_path,
                interrupt_after_sampler=True,
            )
            summary = result["execution_summary"]
            calls = 0 if summary is None else int(summary["counts"].get("comfy_kitchen_calls", 0))
            expected = 0 if name == "dense" else 50
            if calls != expected:
                raise RuntimeError(f"{name}: native calls {calls}, expected {expected}")
            if name != "dense":
                if summary["unexpected_fallbacks"]:
                    raise RuntimeError(f"{name}: unexpected fallback {summary}")
                if bench.ACTIVATION not in result["log_segment"]:
                    raise RuntimeError(f"{name}: missing {bench.ARCH} activation")
            records[name] = {
                "valid": True,
                "evaluations": tier["warmup_evaluations"],
                "sampler_seconds": result["sampler_seconds"],
                "peak_cuda_memory_mib": result["peak_cuda_memory_mib"],
                "kernel_calls": calls,
                "execution_summary": summary,
            }
            bench.write_json(bench.ROOT / f"{name}.json", records[name])
            if index + 1 < len(bench.TIERS):
                bench.stop_server(server)
                server = bench.launch_server(env, log_handle)
                bench.wait_server(server)

        full_log = log_path.read_text(encoding="utf-8", errors="replace")
        forbidden = [
            marker for marker in ("dense after Spark failure", "[Spark-H3] dense fallback:")
            if marker in full_log
        ]
        report = {
            "valid": not forbidden,
            "mode": "short_same_shape_compatibility",
            "comfyui_version": (bench.COMFY / "comfyui_version.py").read_text(encoding="utf-8").split('"')[1],
            "architecture": bench.ARCH,
            "backend_version": bench.EXPECTED_BACKEND,
            "formal_steps": bench.STEPS,
            "lora": bench.LORA_NAME,
            "wheel_audit": wheel_audit,
            "variants": records,
            "unexpected_fallbacks": forbidden,
        }
        bench.write_json(bench.ROOT / "compatibility-summary.json", report)
        if not report["valid"]:
            raise RuntimeError(f"compatibility validation failed: {report}")
        print(f"PASS {bench.ROOT / 'compatibility-summary.json'}")
    finally:
        bench.stop_server(server)
        log_handle.close()


if __name__ == "__main__":
    main()
