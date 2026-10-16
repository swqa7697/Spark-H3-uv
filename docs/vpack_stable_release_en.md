# Spark-VPack 0.1.0 Release Notes

Spark-VPack compresses the reference videos used by ComfyUI's native MiniMax H3 Ref2VA task, shortening the sequence processed by the DiT. It supports ComfyUI 0.38.0 and newer.

| Compression ratio | Description |
| --- | --- |
| `0/5` | No compression |
| `1/5` | Light compression |
| `2/5` | **Recommended default** |
| `3/5` | Stronger compression |

We recommend `2/5`. In a single 4-step, 768p ikun test on an SM120 GPU, the character and scene remained broadly consistent while DiT sampling time fell by about 24% compared with `0/5`. We have not yet run the same quality and timing comparison for `1/5` or `3/5`.

## Usage

Place the `Spark-VPack` folder in `ComfyUI/custom_nodes/` and restart ComfyUI. Connect the native Ref2VA node's `positive` output and the model's `MODEL` output to Spark-VPack, then connect its outputs back into the sampling workflow. Keep the generation latent connected directly to the sampler.
