# ComfyUI Spark-H3 v0.1.5

## 中文

v0.1.5 新增对 ComfyUI 0.42.x（comfy-kitchen 0.2.39）的支持。本次提供 Linux SM120、Windows SM89 和 Windows SM120 安装包。每份 ZIP 都内置对应平台及 GPU 架构的三个 wheel：0.2.36 用于 ComfyUI 0.38.x，0.2.37 用于 0.39.x/0.40.x，0.2.39 用于 0.42.x。

安装器要求 Python 3.12+、PyTorch 2.12+ 和 PyTorch CUDA 13.0+。wheel 以 CUDA 13.0 构建；更新的 PyTorch/CUDA 运行时可以直接尝试安装，并接受原生入口检查，但仍需在目标环境中验证完整工作流与性能。

如果相同工作流中只有 `fidelity` 模式出现 OOM，而 `dense` 与 `speed` 均可运行，可尝试在启动 ComfyUI 时加入 `--disable-cuda-malloc`，作为临时规避办法。它是 ComfyUI 启动参数，不是节点参数。

| 平台 | GPU 架构 | 安装包 |
| --- | --- | --- |
| Linux x86_64 | SM120 · RTX 50 系 | `ComfyUI-Spark-H3-0.1.5-linux-x86_64-sm120-cu130.zip` |
| Windows x86_64 | SM89 · RTX 40 系 | `ComfyUI-Spark-H3-0.1.5-windows-x86_64-sm89-cu130.zip` |
| Windows x86_64 | SM120 · RTX 50 系 | `ComfyUI-Spark-H3-0.1.5-windows-x86_64-sm120-cu130.zip` |

请下载对应 ZIP 和 `SHA256SUMS.txt`，将 ZIP 解压到 `ComfyUI/custom_nodes/`，再用启动该 ComfyUI 的 Python 执行 `ComfyUI-Spark-H3/install.py`，最后重启 ComfyUI。模型权重与 LoRA 不包含在安装包中。

## English

v0.1.5 adds ComfyUI 0.42.x support through comfy-kitchen 0.2.39. The available packages target Linux SM120, Windows SM89, and Windows SM120. Each ZIP also bundles the matching comfy-kitchen 0.2.36 wheel for ComfyUI 0.38.x and 0.2.37 wheel for 0.39.x/0.40.x.

The installer requires Python 3.12+, PyTorch 2.12+, and PyTorch CUDA 13.0+. The wheels were built with CUDA 13.0. Newer PyTorch/CUDA runtimes may try the bundled wheel without an opt-in flag; installation checks the native entry point, while full workflow and performance compatibility require testing on the target runtime.

If only `fidelity` runs out of GPU memory while the same workflow succeeds in `dense` and `speed`, try `--disable-cuda-malloc` when launching ComfyUI as a temporary workaround. This is a ComfyUI startup flag, not a node setting.

Download the ZIP matching your operating system and GPU architecture, verify it with `SHA256SUMS.txt`, extract it into `ComfyUI/custom_nodes/`, and run `ComfyUI-Spark-H3/install.py` with the Python interpreter used by that ComfyUI installation. Restart ComfyUI afterward. Model weights and LoRAs are not included.
