# ComfyUI Spark-H3 v0.1.3

本版本新增 RTX 30 系显卡支持、KJNodes 低显存节点适配、快速模式设置和 dense warmup steps 后端选择，并补充了双采工作流的使用提醒。

## 主要更新

### 1. 新增 SM86 支持

新增面向 NVIDIA SM86（RTX 30 系）的独立节点与安装包，并已在 RTX 3090 上完成 Linux 和 Windows 验证。

当前发布版支持：

- SM86：RTX 30 系
- SM89：RTX 40 系
- SM120：RTX 50 系与 RTX PRO Blackwell
- Linux x86_64 与 Windows x86_64
- PyTorch CUDA 13.0

### 2. 适配 KJNodes 低显存节点

Spark Attention 现在可以与以下 ComfyUI-KJNodes 节点组合使用：

- `MiniMax H3 Low VRAM Attention`
- `MiniMax H3 Chunk FeedForward`

推荐的 MODEL 连接顺序为：

```text
模型加载器 → Low VRAM Attention → Chunk FeedForward → Spark Attention → 采样器
```

这些节点由 ComfyUI-KJNodes 提供，需要单独安装。分块设置越小，通常越节省显存，但也可能增加执行开销。

### 3. 新增快速设置模式

Spark 节点新增以下快速设置模式：

- `fidelity`：默认模式，使用 20% dense warmup steps，以兼顾输出保真度与速度。
- `speed`：关闭 dense warmup，从第一次模型调用开始使用 Spark 稀疏注意力。
- `custom`：保留用户手动设置的 warmup 配置。
- `dense`：完全旁路 Spark，等价于不连接 Spark Attention 节点。

手动修改当前生效的 warmup 参数，使其不再符合 `fidelity` 或 `speed` 预设时，模式会自动切换为 `custom`。重新选择 `fidelity` 或 `speed` 会重新应用对应预设。

### 4. 新增 dense warmup steps 后端选择

新增 `dense_backend` 参数，用于控制 dense warmup steps 实际使用的注意力后端：

- `inherit`：默认值，继承模型或 ComfyUI 当前的全局注意力设置。
- `kitchen`：使用 comfy-kitchen INT8 attention，推荐尝试。
- `sage`：使用 SageAttention，需要单独安装 `sageattention`。
- `sdpa`：使用 PyTorch SDPA。

Kitchen 与 Sage 后端尚未完成端到端质量损失测试，因此目前作为实验功能提供。

### 5. 新增节点内提示

- 双采工作流的高分辨率二阶段应关闭 dense warmup，可通过提示按钮一键切换到 `speed`。
- 使用默认 `inherit` 后端时，节点会提示 warmup 阶段可切换到 Kitchen INT8 attention。

提示按钮仅用于交互，不参与工作流序列化。

## Linux 性能测试

下表统一采用 **Linux、ComfyUI 0.38.2** 下的 LightX2V 768p 8-step LoRA 工作流进行测试，输出规格为 1344×768、345 帧、24 FPS。测试参数为 `topk_ratio=20%`、`warmup_steps=2`，dense attention 使用 ComfyUI 默认的 PyTorch SDPA。

| GPU | Fidelity 相对 Dense | Speed 相对 Dense |
| --- | ---: | ---: |
| RTX 3090（SM86） | **2.42×** | **4.62×** |
| RTX 4090（SM89） | **2.37×** | **4.35×** |
| RTX PRO 6000 Blackwell（SM120） | **2.05×** | **3.15×** |

> **版本提醒：** RTX 3090 与 RTX PRO 6000 Blackwell 上的 Linux 补测结果均表明，ComfyUI 0.39.2 的加速比例相较 0.38.2 有小幅提升，建议使用更新的 **ComfyUI 0.39.2**。

## W6A8 版本说明

测试发现，ComfyUI 0.38.2 配套的 comfy-kitchen 0.2.36 尚未适配 W6A8；ComfyUI 0.39.2 配套的 comfy-kitchen 0.2.37 已完成相关适配。使用 W6A8 权重时，建议升级至 ComfyUI 0.39.2，以获得更好的推理性能。

## 兼容性

- 支持 ComfyUI 0.38.x 与 0.39.x。
- 支持 Linux 与 Windows x86_64。
- 支持 SM86、SM89 与 SM120 GPU。
- 旧版本工作流可以正常加载，参数会进行等价迁移。

## 下载与安装

请根据操作系统和 GPU 架构选择对应安装包：

| GPU 架构 | Linux | Windows |
| --- | --- | --- |
| SM86 · RTX 30 系 | `ComfyUI-Spark-H3-0.1.3-linux-x86_64-sm86-cu130.zip` | `ComfyUI-Spark-H3-0.1.3-windows-x86_64-sm86-cu130.zip` |
| SM89 · RTX 40 系 | `ComfyUI-Spark-H3-0.1.3-linux-x86_64-sm89-cu130.zip` | `ComfyUI-Spark-H3-0.1.3-windows-x86_64-sm89-cu130.zip` |
| SM120 · RTX 50 系／RTX PRO Blackwell | `ComfyUI-Spark-H3-0.1.3-linux-x86_64-sm120-cu130.zip` | `ComfyUI-Spark-H3-0.1.3-windows-x86_64-sm120-cu130.zip` |

安装步骤：

1. 关闭正在运行的 ComfyUI。
2. 根据操作系统和 GPU 架构下载对应的 ZIP。
3. 将 ZIP 解压至 `ComfyUI/custom_nodes/`，并确认节点目录为 `ComfyUI/custom_nodes/ComfyUI-Spark-H3/`。
4. 使用 **ComfyUI 运行环境中的 Python 解释器**执行节点目录内的 `install.py`。
5. 安装完成后重新启动 ComfyUI。

例如：

```bash
# Linux：在 ComfyUI 根目录中执行
./.venv/bin/python custom_nodes/ComfyUI-Spark-H3/install.py

# Windows 虚拟环境：在 ComfyUI 根目录中执行
.venv\Scripts\python.exe custom_nodes\ComfyUI-Spark-H3\install.py

# Windows Portable：在 ComfyUI_windows_portable 目录中执行
python_embeded\python.exe ComfyUI\custom_nodes\ComfyUI-Spark-H3\install.py
```

请勿使用与 ComfyUI 运行环境无关的系统 Python，否则依赖可能会被安装到错误的环境。安装器会根据 ComfyUI 版本自动选择匹配的 comfy-kitchen 后端：ComfyUI 0.38.x 对应 0.2.36，ComfyUI 0.39.x 对应 0.2.37。更详细的安装与故障排查说明请参阅安装包内的 `INSTALL.zh-CN.md`。
