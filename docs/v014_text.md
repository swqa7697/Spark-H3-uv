# ComfyUI Spark-H3 v0.1.4

## 中文

本版本新增 ComfyUI 0.40.x 兼容支持，并为 Spark Attention 节点加入可选的 `sparse_scope` 与 `producer_chunk`。Ref2VA 用户可以将参考视频与目标视频放入同一个 Spark 稀疏域，也可以按工作流显存与性能需求调整 Q/K/V producer 的分块大小。默认行为保持不变。

## 主要更新

### 1. 支持 ComfyUI 0.40.x

### 2. 新增 Spark `sparse_scope`

Spark Attention 节点新增以下稀疏范围：

- `target-video`：默认值，只将目标视频 token 放入 Spark 稀疏域。文本、参考图、参考视频和音频保持 dense/exact，与 v0.1.3 的行为一致。
- `joint-video`：将具有多个时间位置的参考视频视觉 token 与目标视频 token 放入同一个 Spark 稀疏域，统一执行 Reblock、Top-K 和 Reweight。静态参考图、文本、参考音频和目标音频仍保持 exact。

对于带视频条件的 Ref2VA，建议使用：

```text
sparse_scope=joint-video
```

### 3. 新增 Ref2VA 节点内提示

### 4. 新增可选 `producer_chunk`

Spark Attention 节点新增可选参数 `producer_chunk`，默认值为 `16384`。适当调低该参数可以降低显存占用，但设置过低可能影响速度。

### 5. 已知问题

我们观察到，`mode=fidelity` 从 dense warmup steps 切换到 sparse steps 时，可能出现不合理的高显存占用，目前尚未找到原因。可以通过调低 `producer_chunk` 来降低显存占用，或改用 `mode=speed` 跳过 dense warmup 来规避。

## 兼容性

- ComfyUI 0.38.x、0.39.x 与 0.40.x
- Linux x86_64 与 Windows x86_64
- NVIDIA SM86、SM89 与 SM120 GPU
- PyTorch CUDA 13.0
- 每个 ZIP 同时内置适用于 ComfyUI 0.38.x 的 comfy-kitchen 0.2.36 wheel，以及适用于 ComfyUI 0.39.x/0.40.x 的 0.2.37 wheel
- 旧版工作流可继续加载；未显式保存时使用 `sparse_scope=target-video` 和 `producer_chunk=16384`

## 下载

请根据操作系统和 GPU 架构选择对应安装包：

| GPU 架构 | Linux | Windows |
| --- | --- | --- |
| SM86 · RTX 30 系 | `ComfyUI-Spark-H3-0.1.4-linux-x86_64-sm86-cu130.zip` | `ComfyUI-Spark-H3-0.1.4-windows-x86_64-sm86-cu130.zip` |
| SM89 · RTX 40 系 | `ComfyUI-Spark-H3-0.1.4-linux-x86_64-sm89-cu130.zip` | `ComfyUI-Spark-H3-0.1.4-windows-x86_64-sm89-cu130.zip` |
| SM120 · RTX 50 系／RTX PRO Blackwell | `ComfyUI-Spark-H3-0.1.4-linux-x86_64-sm120-cu130.zip` | `ComfyUI-Spark-H3-0.1.4-windows-x86_64-sm120-cu130.zip` |

请同时下载 `SHA256SUMS.txt` 并在安装前校验 ZIP。

## 安装

1. 关闭正在运行的 ComfyUI。
2. 下载与操作系统和 GPU 架构匹配的 ZIP。
3. 将 ZIP 解压到 `ComfyUI/custom_nodes/`，确认节点目录为 `ComfyUI/custom_nodes/ComfyUI-Spark-H3/`。
4. 使用 **ComfyUI 自己的 Python 解释器**运行节点目录内的 `install.py`。
5. 安装完成后重新启动 ComfyUI。

```bash
# Linux：在 ComfyUI 根目录中执行
./.venv/bin/python custom_nodes/ComfyUI-Spark-H3/install.py

# Windows 虚拟环境：在 ComfyUI 根目录中执行
.venv\Scripts\python.exe custom_nodes\ComfyUI-Spark-H3\install.py

# Windows Portable：在 ComfyUI_windows_portable 目录中执行
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-Spark-H3\install.py
```

请勿使用与 ComfyUI 运行环境无关的系统 Python。本版本未推送到 Comfy Registry，请使用上述 ZIP 手动安装。

---

## English

This release adds compatibility with ComfyUI 0.40.x and introduces optional `sparse_scope` and `producer_chunk` controls for Spark Attention. Ref2VA users can place reference-video and target-video tokens in one shared Spark sparse domain and adjust the Q/K/V producer chunk size to balance VRAM usage and performance for their workflows. Default behavior remains unchanged.

## Highlights

### 1. ComfyUI 0.40.x support

### 2. New Spark `sparse_scope`

Spark Attention now provides two sparse scopes:

- `target-video`: the default. Only target-video tokens enter the Spark sparse domain. Text, reference images, reference video, and audio remain dense/exact, preserving the v0.1.3 behavior.
- `joint-video`: multi-timestep reference-video visual tokens and target-video tokens enter one shared Spark sparse domain and jointly use Reblock, Top-K, and Reweight. Static reference images, text, reference audio, and target audio remain exact.

For video-conditioned Ref2VA, we recommend:

```text
sparse_scope=joint-video
```

### 3. New in-node Ref2VA guidance

### 4. New optional `producer_chunk`

Spark Attention now provides an optional `producer_chunk` parameter with a default value of `16384`. Lowering it can reduce VRAM usage, but setting it too low may reduce performance.

### 5. Known issue

We have observed that `mode=fidelity` may use unexpectedly high VRAM when it transitions from dense warmup steps to sparse steps. The cause is currently unknown. Lowering `producer_chunk` can reduce VRAM usage, or `mode=speed` can be used to skip dense warmup and avoid the issue.

## Compatibility

- ComfyUI 0.38.x, 0.39.x, and 0.40.x
- Linux x86_64 and Windows x86_64
- NVIDIA SM86, SM89, and SM120 GPUs
- PyTorch CUDA 13.0
- Each ZIP bundles both a comfy-kitchen 0.2.36 wheel for ComfyUI 0.38.x and a 0.2.37 wheel for ComfyUI 0.39.x/0.40.x
- Existing workflows continue to load; omitted values default to `sparse_scope=target-video` and `producer_chunk=16384`

## Downloads

Choose the package matching both your operating system and GPU architecture:

| GPU architecture | Linux | Windows |
| --- | --- | --- |
| SM86 · RTX 30 series | `ComfyUI-Spark-H3-0.1.4-linux-x86_64-sm86-cu130.zip` | `ComfyUI-Spark-H3-0.1.4-windows-x86_64-sm86-cu130.zip` |
| SM89 · RTX 40 series | `ComfyUI-Spark-H3-0.1.4-linux-x86_64-sm89-cu130.zip` | `ComfyUI-Spark-H3-0.1.4-windows-x86_64-sm89-cu130.zip` |
| SM120 · RTX 50 series / RTX PRO Blackwell | `ComfyUI-Spark-H3-0.1.4-linux-x86_64-sm120-cu130.zip` | `ComfyUI-Spark-H3-0.1.4-windows-x86_64-sm120-cu130.zip` |

Download `SHA256SUMS.txt` as well and verify the selected ZIP before installation.

## Installation

1. Stop ComfyUI if it is running.
2. Download the ZIP matching your operating system and GPU architecture.
3. Extract it into `ComfyUI/custom_nodes/` and confirm that the node directory is `ComfyUI/custom_nodes/ComfyUI-Spark-H3/`.
4. Run `install.py` from the node directory using the **Python interpreter from the ComfyUI runtime environment**.
5. Restart ComfyUI after installation completes.

```bash
# Linux: run from the ComfyUI root directory
./.venv/bin/python custom_nodes/ComfyUI-Spark-H3/install.py

# Windows virtual environment: run from the ComfyUI root directory
.venv\Scripts\python.exe custom_nodes\ComfyUI-Spark-H3\install.py

# Windows Portable: run from the ComfyUI_windows_portable directory
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-Spark-H3\install.py
```

Do not use a system Python installation unrelated to the ComfyUI runtime. This release has not been published to the Comfy Registry; install it manually from one of the ZIP archives above.
