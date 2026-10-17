# Spark-H3 Linux and Windows release kit

The generator creates one kit for one GPU architecture (`sm86`, `sm89`, or
`sm120`) and one target platform (`linux` or `windows`). Check
`release.json` before building. Native CUDA wheels must be built and validated
on the target operating system with the same Python used by ComfyUI.

## Generate a kit

From the Spark-H3 repository root:

```bash
python tools/build_spark_release_toolkit.py --architecture sm120 --platform linux --publisher-id YOUR_ID
```

For Windows, use `--platform windows`. The generator can run on either
host, but building and executing a kit requires its target platform. Each kit
contains the custom node source, workflow, build tools, validators, and a
`wheelhouse/` for architecture-matched comfy-kitchen wheels.

## Linux

Use a ComfyUI Python with CUDA 13.0, torch 2.12.x and compatible Triton 3.7.x.
Install CUDA Toolkit, `git`, `g++`, `cuobjdump`, and `ffprobe` (for full video
validation). Then, from the generated kit:

```bash
./build.sh --python /path/to/comfyui/bin/python
./validate.sh --python /path/to/comfyui/bin/python --mode audit
./validate.sh --python /path/to/comfyui/bin/python --comfyui-root /path/to/ComfyUI --mode full
/path/to/comfyui/bin/python ./bundle.py
```

`--mode compatibility` runs the shorter same-shape check. Use `--kitchen-base
0.2.37` on `build.sh` if only that ComfyUI backend is needed. You may instead
place a correctly tagged wheel in `wheelhouse/` and skip the build step.

## Windows

Use the same Python for every step. It requires CUDA 13.0, torch 2.12.x and
compatible `triton-windows` 3.7.x. In a VS 2022 x64 developer PowerShell with
CUDA Toolkit and Git:

```powershell
./build.ps1 -Python C:\path\to\python.exe
./validate.ps1 -ComfyUIRoot C:\path\to\ComfyUI -Python C:\path\to\python.exe -Mode audit
./validate.ps1 -ComfyUIRoot C:\path\to\ComfyUI -Python C:\path\to\python.exe -Mode full
& C:\path\to\python.exe ./bundle.py
```

`-Mode compatibility` runs the shorter check. Both platforms accept a 4-step
LoRA: Linux `--steps 4 --lora-name NAME.safetensors`, Windows `-Steps 4
-LoraName NAME.safetensors`. Put it under ComfyUI `models/loras/` first.

The full workflow expects these model files under ComfyUI `models/`:
`diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors`,
`loras/minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`,
`text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`,
`vae/minimax_h3_video_vae_fp16.safetensors`, and
`vae/minimax_h3_audio_vae_fp32.safetensors`.

Validation checks wheel identity, embedded GPU architecture, native
`spark_attn` behavior, ComfyUI compatibility, Dense/Fidelity/Speed output, and
unexpected dense fallback. It supports ComfyUI 0.38.x (comfy-kitchen 0.2.36)
and 0.39.x/0.40.x (comfy-kitchen 0.2.37). `bundle.py` requires a passing wheel
audit and writes a platform-specific release archive with SHA-256 metadata.
