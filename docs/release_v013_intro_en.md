# ComfyUI Spark-H3 v0.1.3

This release adds RTX 30-series support, compatibility with the KJNodes low-VRAM nodes, quick mode presets, and selectable attention backends for dense warmup steps. It also adds guidance for two-pass workflows.

## Highlights

### 1. SM86 support

This release adds a dedicated node and package for NVIDIA SM86 (RTX 30-series) GPUs. Both Linux and Windows have been validated on an RTX 3090.

The current release supports:

- SM86: RTX 30 series
- SM89: RTX 40 series
- SM120: RTX 50 series and RTX PRO Blackwell
- Linux x86_64 and Windows x86_64
- PyTorch CUDA 13.0

### 2. KJNodes low-VRAM compatibility

Spark Attention can now be combined with the following ComfyUI-KJNodes nodes:

- `MiniMax H3 Low VRAM Attention`
- `MiniMax H3 Chunk FeedForward`

The recommended MODEL connection order is:

```text
Model Loader → Low VRAM Attention → Chunk FeedForward → Spark Attention → Sampler
```

These nodes are provided by ComfyUI-KJNodes and must be installed separately. Smaller chunk sizes generally reduce VRAM usage, but may increase execution overhead.

### 3. Quick mode presets

The Spark node now provides the following quick mode presets:

- `fidelity`: the default mode; uses dense attention for the first 20% of denoising steps to balance fidelity and speed.
- `speed`: disables dense warmup and uses Spark sparse attention from the first model evaluation.
- `custom`: preserves manually configured warmup settings.
- `dense`: bypasses Spark completely, equivalent to leaving the Spark Attention node disconnected.

If the active warmup settings are edited so that they no longer match the `fidelity` or `speed` preset, the mode automatically changes to `custom`. Selecting `fidelity` or `speed` again reapplies the corresponding preset.

### 4. Selectable backend for dense warmup steps

The new `dense_backend` parameter controls the attention backend used during dense warmup steps:

- `inherit`: the default; inherits the model or current global ComfyUI attention setting.
- `kitchen`: uses comfy-kitchen INT8 attention and is the recommended option to try.
- `sage`: uses SageAttention and requires `sageattention` to be installed separately.
- `sdpa`: uses PyTorch SDPA.

Kitchen and Sage have not yet undergone complete end-to-end quality regression testing, so they are currently provided as experimental options.

### 5. In-node guidance

- The high-resolution second stage of a two-pass workflow should disable dense warmup; the prompt button can switch the node to `speed` in one click.
- When the default `inherit` backend is selected, the node indicates that the warmup stage can use Kitchen INT8 attention.

These prompt buttons are UI-only and are not serialized into workflows.

## Linux performance

The table below uses the LightX2V 768p 8-step LoRA workflow on **Linux with ComfyUI 0.38.2**, producing 1344×768 video with 345 frames at 24 FPS. The test configuration uses `topk_ratio=20%`, `warmup_steps=2`, and ComfyUI's default PyTorch SDPA for dense attention.

| GPU | Fidelity vs. Dense | Speed vs. Dense |
| --- | ---: | ---: |
| RTX 3090 (SM86) | **2.42×** | **4.62×** |
| RTX 4090 (SM89) | **2.37×** | **4.35×** |
| RTX PRO 6000 Blackwell (SM120) | **2.05×** | **3.15×** |

> **Version note:** Additional Linux tests on the RTX 3090 and RTX PRO 6000 Blackwell show a small improvement in speedup ratios with ComfyUI 0.39.2 compared with 0.38.2. We recommend using the newer **ComfyUI 0.39.2** release.

## W6A8 version note

Testing found that comfy-kitchen 0.2.36, bundled with ComfyUI 0.38.2, is not optimized for W6A8. The corresponding support is available in comfy-kitchen 0.2.37, bundled with ComfyUI 0.39.2. Users of W6A8 weights should upgrade to ComfyUI 0.39.2 for better inference performance.

## Compatibility

- ComfyUI 0.38.x and 0.39.x
- Linux and Windows x86_64
- SM86, SM89, and SM120 GPUs
- Workflows created with earlier releases load normally, with parameters migrated to equivalent settings.

## Download and installation

Choose the package matching both your operating system and GPU architecture:

| GPU architecture | Linux | Windows |
| --- | --- | --- |
| SM86 · RTX 30 series | `ComfyUI-Spark-H3-0.1.3-linux-x86_64-sm86-cu130.zip` | `ComfyUI-Spark-H3-0.1.3-windows-x86_64-sm86-cu130.zip` |
| SM89 · RTX 40 series | `ComfyUI-Spark-H3-0.1.3-linux-x86_64-sm89-cu130.zip` | `ComfyUI-Spark-H3-0.1.3-windows-x86_64-sm89-cu130.zip` |
| SM120 · RTX 50 series / RTX PRO Blackwell | `ComfyUI-Spark-H3-0.1.3-linux-x86_64-sm120-cu130.zip` | `ComfyUI-Spark-H3-0.1.3-windows-x86_64-sm120-cu130.zip` |

Installation steps:

1. Stop ComfyUI if it is running.
2. Download the ZIP matching your operating system and GPU architecture.
3. Extract it into `ComfyUI/custom_nodes/` and confirm that the node directory is `ComfyUI/custom_nodes/ComfyUI-Spark-H3/`.
4. Run `install.py` from the node directory using the **Python interpreter from the ComfyUI runtime environment**.
5. Restart ComfyUI after installation completes.

For example:

```bash
# Linux: run from the ComfyUI root directory
./.venv/bin/python custom_nodes/ComfyUI-Spark-H3/install.py

# Windows virtual environment: run from the ComfyUI root directory
.venv\Scripts\python.exe custom_nodes\ComfyUI-Spark-H3\install.py

# Windows Portable: run from the ComfyUI_windows_portable directory
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-Spark-H3\install.py
```

Do not use a system Python installation unrelated to the ComfyUI runtime environment, as dependencies may be installed into the wrong environment. The installer automatically selects the matching comfy-kitchen backend: version 0.2.36 for ComfyUI 0.38.x and version 0.2.37 for ComfyUI 0.39.x. See `README.md` in the package for detailed installation and troubleshooting instructions.
