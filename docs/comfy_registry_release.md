# Comfy Registry release

Spark-H3 publishes one self-contained Registry archive under publisher
`zechengtang` and node ID `comfyui-spark-h3`. The archive contains the complete
Linux/Windows, SM86/SM89/SM120, comfy-kitchen 0.2.36/0.2.37 wheel matrix. Users
do not need GitHub access during installation.

## Build locally

Collect the twelve `comfy_kitchen` wheels from the six architecture-specific
GitHub release ZIPs into one directory, then run:

```bash
python tools/build_comfyui_package.py \
  --registry \
  --version 0.1.3 \
  --publisher-id zechengtang \
  --kernel-wheel-dir /path/to/registry-wheels \
  --output-dir dist/registry
```

The builder rejects incomplete, duplicate, unsupported-CUDA, or unsupported-
platform wheel matrices. The preview archive is
`dist/registry/ComfyUI-Spark-H3-0.1.3-registry.zip`.

## Publish

Create a Registry publishing API key for `@zechengtang`, then save it as the
GitHub repository secret `REGISTRY_ACCESS_TOKEN`. Run the **Publish Comfy
Registry package** workflow manually. It downloads the six already-published
v0.1.3 platform archives, verifies that exactly twelve wheels are present,
builds the Registry package, runs the package tests and `comfy node validate`,
and publishes version 0.1.3.

The workflow is intentionally manual because a Registry version must not be
published twice. For later releases, update the version and release tag in the
workflow only after the matching six platform archives are public.
