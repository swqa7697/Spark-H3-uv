# ComfyUI Spark 节点参数

节点名称：GeForce RTX 40 系使用 `MiniMax H3 Spark Attention (SM89)`；GeForce RTX 50 系及 RTX PRO 5000/6000 Blackwell 使用 `MiniMax H3 Spark Attention (SM120)`。把对应节点接在 MiniMax H3 模型加载节点与采样器之间。两个节点的参数接口相同，界面中的每个输入也有中文悬浮说明。

节点最前面的 `mode` 按 `fidelity`、`speed`、`custom`、`dense` 排列。它取代 `enabled`，但不会取代 `warmup_mode`、`warmup_ratio` 和 `warmup_steps`：选择 fidelity/speed 时自动填入推荐 warmup 值；手动修改当前生效的 warmup 参数使其不再符合预设时，mode 自动变为 custom。切换到 dense 只旁路 Spark，不会清空 warmup 配置。`topk_mode` 仍显示在 Top-K 参数上方，并只读取当前模式使用的 Top-K 数值框。

## 常用设置

默认使用 `mode=fidelity`、`warmup_mode=warmup_ratio`、`warmup_ratio=0.2`、`topk_mode=topk_ratio`、`topk_ratio=0.2`、`sparse_scope=target-video` 和 `producer_chunk=16384`；切换到固定块数模式时，`topk_blocks` 默认是 `228`。选择 `speed` 会把 warmup ratio 填成 0；`dense` 完全不安装 Spark 补丁并原样传出模型。`steps` 填实际采样调用次数。

`sparse_scope=target-video` 保留原有发布路径，只把目标视频放入稀疏域，并继续使用单连续区间 direct-output 优化。`joint-video` 用于 Ref2VA，把具有多个时间位置的参考视频视觉 token 与目标视频放入同一个稀疏域，统一执行 Reblock、Top-K 和 Reweight；静态参考图、文本、参考音频和目标音频仍保持 exact。没有参考视频视觉 token 时，`joint-video` 自动退化为完全相同的 target-video 路径。参考视频与目标分辨率不同时会使用 flat composite grid，并在 kernel 后恢复 ComfyUI 原始 packed 顺序。

当 `sparse_scope=target-video` 且该字段没有连接外部输入时，节点会显示不参与工作流序列化的提醒按钮：“带视频条件的 Ref2VA：建议使用 sparse_scope=joint-video → 一键切换”。点击后会切换到 `joint-video` 并隐藏提醒。

从其他 mode 切换到 `fidelity` 会重新写入未连接成外部输入的 `warmup_mode=warmup_ratio` 和 `warmup_ratio=0.2`，因此可以覆盖之前的手动 warmup 设置。手动改变当前生效的 warmup mode/数值后会立即进入 `custom`，再选择 fidelity 即可重新应用预设；修改当前未生效的 `warmup_steps` 不会误触发 custom。预设控制字段连接外部输入时也会进入 custom，因为实际运行值由上游决定。fidelity 下会出现不参与工作流序列化的提醒按钮：“双采高分辨率二阶段：建议使用 mode=speed → 一键切换”。点击即可应用 speed 预设。

在本地 10 秒 768p 样本中，视频有 72,576 个 token，按 64 token 一块分成 1,134 个候选视频块。因此 `topk_blocks=114/228/342` 分别约为 **10%/20%/30% 精确保留比例**。在这几个预算中，10% 更偏速度，30% 更偏保真度，建议从 20% 开始。这里的“10%”是精确选中的候选块比例，不是 10% 被跳过；未选中块仍可经过 Spark 的近似校正。改变时长、分辨率或视频 token 布局时，相同块数对应的百分比也会变化。

## 所有输入

| 参数 | 作用与建议 |
| --- | --- |
| `model` | 要打补丁的 ComfyUI 原生 MiniMax H3 `MODEL`。连接模型加载节点输出，Spark 节点输出再接采样器。 |
| `mode` | 按 `fidelity / speed / custom / dense` 排列。`fidelity`（默认）填入 `warmup_mode=warmup_ratio, warmup_ratio=0.2`；`speed` 填入相同 mode 和 ratio 0；`custom` 使用手动 warmup 配置；`dense` 等价于原来的 `enabled=false`，不安装 Spark 补丁并原样输出模型。dense 不清空 warmup 值。 |
| `steps` | 一次采样的模型调用次数，用于按步数计算预热。通常与采样器的 `steps` 相同；应按实际模型调用次数设置。 |
| `warmup_mode` | 选择用比例或固定调用次数表示 dense 预热长度。mode 预设会选择 `warmup_ratio`，但用户可以改回 `warmup_steps`。 |
| `warmup_ratio` | `warmup_mode=warmup_ratio` 时生效，范围 0–1。默认/fidelity 为 0.2，speed 填入 0。 |
| `warmup_steps` | `warmup_mode=warmup_steps` 时生效，直接指定 dense 模型调用次数；保留用于精确控制。 |
| `topk_ratio` | 精确计算的候选视频块比例：`0.1≈10%` 速度最快，`0.3≈30%` 保真度最好，建议 `0.15` 或 `0.2` 取得均衡。仅在 `topk_mode=topk_ratio` 时生效。 |
| `dense_layers` | 前多少个 Transformer 层始终使用 dense attention。默认 `0`，表示没有固定 dense 层。 |
| `min_tokens` | 序列 token 数低于此阈值时保持 dense。默认 `12288`，避免短序列走稀疏路径的固定开销；它不是 Top-K 的块数。 |
| `strict` | 开启时，遇到 Spark 不支持的输入直接报错；关闭时回退到原 attention 并在日志中记录原因。建议调试时开启，以免误把回退结果当作 Spark。 |
| `sparse_scope` | 稀疏视觉范围。`target-video`（默认）保持原有路径，只稀疏目标视频；`joint-video` 将 Ref2VA 的参考视频视觉 token 与目标视频放入同一个稀疏域，统一执行 Reblock、Top-K 和 Reweight。静态参考图、文本和音频在两种模式下都保持 exact。旧工作流中的 `target` 和 `ref+target` 会分别自动兼容为 `target-video` 和 `joint-video`。 |
| `producer_chunk` | Spark Q/K/V producer 每次处理的 token 数，默认 `16384`，必须是 64 的正整数倍；节点界面范围为 `64–262144`。减小该值可能降低 producer 阶段的临时显存，但会增加分块调用开销，实际速度和显存收益依硬件与工作流而异。环境变量 `H3_SPARK_PRODUCER_CHUNK` 仍可设置节点的启动默认值。此参数只属于 Spark 节点，Sol 兼容节点不显示。 |
| `topk_mode` | Top-K 预算方式：默认 `topk_ratio`，用随视频长度变化的比例；`topk_blocks` 用固定块数。 |
| `topk_blocks` | 每个 query 块精确计算的候选视频块数。仅在 `topk_mode=topk_blocks` 时生效；本地 10 秒 768p 样本可参考 `114≈10%`、`228≈20%`、`342≈30%`，建议先用 `228`。实际保留数会受候选块总数限制；额外的 dense sink 不计入这个预算。 |
| `dense_backend` | dense 预热、`dense_layers`、短序列和非严格模式回退使用的注意力后端。`inherit`（默认）不强制覆盖，沿用模型或 ComfyUI 当前设置，并不表示自动选择最快后端；`kitchen` 强制使用 comfy-kitchen INT8 attention；`sage` 强制使用单独安装的 SageAttention；`sdpa` 强制使用 PyTorch SDPA。选择不可用的强制后端会在安装节点补丁时明确报错，不会静默换成其他后端。此选项只改变 dense 调用，不改变 Spark 稀疏 kernel。 |
| `tail_granularity` | 近似分支的 Q 粒度。`query`（默认）对应 sol-engine 的 Sol 实现思路：只对 K/V 下采样，每条真实 Q 分别消费近似汇总。`block` 对应 ComfyUI 的 Sol 实现思路：Q 和 K/V 都按块下采样，同一 Q 块共享近似结果。Spark 的精确分支在两种模式下仍使用真实 Q；此参数不控制视频尾块的 dense 策略。 |
| `reblock_layout` | reblock 布局。默认 `q_reuse_k`（与 Python API 的 `q_from_k` 同义）只构造 K 侧布局并让 Q 共用同一 permutation，从而省去 Q 侧 M2、投影、树构建和重复索引存储。`independent` 分别构造 Q/K 布局，用于复现旧版行为。 |

`topk_ratio=0.2` 表示精确选择 20% 的候选块，`topk_blocks=228` 表示固定选择 228 个块。`mode` 提供 warmup 快捷填充、custom 状态或 dense 旁路；实际预热由显式 warmup 参数决定。`topk_mode` 决定 Top-K 的表示方式。

切换到 `joint-video` 会扩大候选视觉块集合。`topk_ratio` 会维持相同的候选保留比例；`topk_blocks` 保持绝对块数，因此对更大的候选集合会形成更低的实际比例。Ref2VA 建议优先使用 `topk_ratio`。

`dense_backend` 通过 ComfyUI 的 attention 注册表在 Python 层逐次覆盖，因此在对应依赖已经安装、后端已经包含于当前环境时，不需要重新编译 SM86、SM89 或 SM120 的 Spark comfy-kitchen wheel。`sage` 需要 ComfyUI 环境中安装 `sageattention`；`kitchen` 需要当前 comfy-kitchen build 报告 INT8 attention 可用。

`producer_chunk` 只改变 Python producer 的分块大小，不改变 comfy-kitchen 的二进制 ABI，因此调整它不需要重新编译 wheel。除非在特定显存压力下进行过实测，建议保留默认值 `16384`。

当 `dense_backend=inherit` 且该字段没有连接外部输入时，节点会显示不参与工作流序列化的按钮“Dense warmup 加速：可使用 dense_backend=kitchen → 一键切换”。点击后会将 dense backend 切换为 kitchen，按钮随即隐藏；默认值仍保持 inherit。

## 与 KJNodes 低显存节点组合

支持 `MiniMax H3 Low VRAM Attention` 和 `MiniMax H3 Chunk FeedForward`，推荐连接为：

```text
模型加载器 → Low VRAM Attention → Chunk FeedForward → Spark Attention → 采样器
```

Low VRAM Attention 必须位于 Spark 前面。Spark 在安装时检测其
`sol_take_forward` 标记；检测到后才选择专用 head-chunk 路径，否则继续安装原来的
Spark block patch。这样未使用低显存节点的工作流不会增加逐层判断。把 Low VRAM
Attention 放在 Spark 后面虽然通常不会报错，但 Spark 稀疏阶段不会获得完整的
head 分块和提前释放效果，因此不属于受支持顺序。Chunk FeedForward 修改的是 MLP，
可以与 Spark 并用。两者都不要求重新编译 Spark wheel。
