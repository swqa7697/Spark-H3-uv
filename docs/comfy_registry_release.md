# Comfy Registry release

Spark-H3 publishes one self-contained Registry archive under publisher
`zechengtang` and node ID `comfyui-spark-h3`. The archive contains the complete
Linux/Windows, SM86/SM89/SM120, comfy-kitchen 0.2.36/0.2.37 wheel matrix. Users
do not need GitHub access during installation.

Registry version `0.1.5` packages the runtime and backend wheels from GitHub
Release `comfyui-v0.1.3`. Versions `0.1.3` and `0.1.4` were withdrawn while the
Registry metadata and package introduction were being corrected. Registry
version numbers cannot be reused after withdrawal. The next release will use
`0.2.0` in both GitHub Releases and Comfy Registry so the two version lines are
aligned again.

The Registry node description is:

> Spark-H3 accelerates ComfyUI's native MiniMax-H3 video generation with
> adaptive block-sparse attention by grouping similar tokens and correcting
> tail tokens through reweighting. v0.1.3 Linux benchmarks (LightX2V 768p
> 8-step, 1344x768, 345 frames, 24 FPS; topk_ratio 20%, warmup_steps 2, dense
> SDPA): RTX 3090 - Fidelity 2.42x / Speed 4.62x; RTX 4090 - 2.37x / 4.35x;
> RTX PRO 6000 Blackwell - 2.05x / 3.15x.

## Build locally

Collect the twelve `comfy_kitchen` wheels from the six architecture-specific
GitHub release ZIPs into one directory, then run:

```bash
python tools/build_comfyui_package.py \
  --registry \
  --version 0.1.5 \
  --publisher-id zechengtang \
  --kernel-wheel-dir /path/to/registry-wheels \
  --output-dir dist/registry
```

The builder rejects incomplete, duplicate, unsupported-CUDA, or unsupported-
platform wheel matrices. The preview archive is
`dist/registry/ComfyUI-Spark-H3-0.1.5-registry.zip`.

## Publish

Create a Registry publishing API key for `@zechengtang`, then save it as the
GitHub repository secret `REGISTRY_ACCESS_TOKEN`. Run the **Publish Comfy
Registry package** workflow manually. It downloads the six already-published
v0.1.3 platform archives, verifies that exactly twelve wheels are present,
builds the Registry package, runs the package tests and `comfy node validate`,
and publishes Registry version 0.1.5.

The workflow is intentionally manual because a Registry version must not be
published twice. For later releases, update the version and release tag in the
workflow only after the matching six platform archives are public.
