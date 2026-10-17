"""Cross-architecture identity and planner-source safeguards for release kits."""

from __future__ import annotations

import json
import ast
import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools" / "build_spark_release_toolkit.py"


def test_generated_windows_kits_select_their_own_architecture(tmp_path):
    for arch, capability in (("sm86", [8, 6]), ("sm89", [8, 9]), ("sm120", [12, 0])):
        kit = tmp_path / f"kit-{arch}"
        subprocess.run(
            [sys.executable, str(GENERATOR), "--architecture", arch, "--platform", "windows",
             "--publisher-id", "test-publisher", "--output", str(kit)],
            check=True, capture_output=True, text=True,
        )
        identity = json.loads((kit / "release.json").read_text(encoding="utf-8"))
        assert identity["capability"] == capability
        assert identity["architecture"] == arch
        validate_source = (kit / "validate.ps1").read_text(encoding="utf-8")
        assert "'0.40' = '0.2.37'" in validate_source
        assert "0.38.x/0.39.x/0.40.x" in validate_source
        check = subprocess.run(
            [sys.executable, "-c", "from preflight import verify_packaged_source, require_direct_triton_imports; "
             "verify_packaged_source(); require_direct_triton_imports(__import__('pathlib').Path('ComfyUI-Spark-H3'))"],
            cwd=kit, capture_output=True, text=True,
        )
        assert check.returncode == 0, check.stderr
        with zipfile.ZipFile(kit.with_suffix(".zip")) as archive:
            assert archive.testzip() is None
        node_source = (kit / "ComfyUI-Spark-H3" / "comfyui_nodes.py").read_text(encoding="utf-8")
        node_tree = ast.parse(node_source)
        spark_class = next(
            node for node in node_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "MiniMaxH3SparkAttentionSM120"
        )
        patch = next(
            node for node in spark_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "patch"
        )
        accepted_inputs = {argument.arg for argument in patch.args.args} - {"self"}
        env = {**os.environ, "COMFYUI_ROOT": str(kit), "SPARK_WHEEL": str(
            kit / "wheelhouse" /
            f"comfy_kitchen-0.2.37+spark.h3.{arch}.cu130.1-cp312-abi3-win_amd64.whl"
        )}
        prompts = subprocess.run(
            [sys.executable, "-c",
             "import json,run_lightx2v_three_variants as b; "
             "print(json.dumps({t['name']:b.formal_prompt(t,'test')['141']['inputs'] for t in b.TIERS}))"],
            cwd=kit, env=env, capture_output=True, text=True,
        )
        assert prompts.returncode == 0, prompts.stderr
        mode_inputs = json.loads(prompts.stdout)
        for tier in ("dense", "fidelity", "speed"):
            assert mode_inputs[tier]["mode"] == tier
            assert "enabled" not in mode_inputs[tier]
            assert set(mode_inputs[tier]) <= accepted_inputs
        configured = subprocess.run(
            [sys.executable, "-c",
             "import json,run_lightx2v_three_variants as b; "
             "p={t['name']:b.formal_prompt(t,'test') for t in b.TIERS}; "
             "print(json.dumps({'steps':[(x['124']['inputs']['steps'],x['141']['inputs']['steps']) for x in p.values()],"
             "'loras':[x['142']['inputs']['lora_name'] for x in p.values()],"
             "'protocol':b.protocol('test')['fixed']}))"],
            cwd=kit,
            env={**env, "SPARK_STEPS": "4", "SPARK_LORA_NAME": "four_step.safetensors"},
            capture_output=True, text=True,
        )
        assert configured.returncode == 0, configured.stderr
        settings = json.loads(configured.stdout)
        assert settings["steps"] == [[4, 4]] * 3
        assert settings["loras"] == ["four_step.safetensors"] * 3
        assert settings["protocol"]["steps"] == 4
        assert settings["protocol"]["lora"] == "four_step.safetensors"
        planner = kit / "ComfyUI-Spark-H3" / "h3_sparse_attention" / "landmark_v2_fused_node.py"
        planner.write_text(planner.read_text(encoding="utf-8") + "\n# local patch\n", encoding="utf-8")
        check = subprocess.run(
            [sys.executable, "-c", "from preflight import verify_packaged_source; verify_packaged_source()"],
            cwd=kit, capture_output=True, text=True,
        )
        assert check.returncode != 0
        assert "planner source changed" in check.stderr


def test_generated_linux_kit_uses_linux_wheels_and_entrypoints(tmp_path):
    kit = tmp_path / "linux-kit"
    subprocess.run(
        [sys.executable, str(GENERATOR), "--architecture", "sm120",
         "--platform", "linux", "--publisher-id", "test-publisher",
         "--output", str(kit)],
        check=True, capture_output=True, text=True,
    )
    identity = json.loads((kit / "release.json").read_text(encoding="utf-8"))
    assert identity["platform"] == "linux-x86_64"
    assert (kit / "build.sh").is_file()
    assert (kit / "validate.sh").is_file()
    assert not (kit / "build.ps1").exists()
    for script in (("build.sh", "validate.sh") if sys.platform.startswith("linux")
                   else ("build.py", "validate.py")):
        command = [str(kit / script), "--help"] if script.endswith(".sh") else [sys.executable, str(kit / script), "--help"]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr

    source = "from config import wheel_base, EXTENSION_SUFFIX; " \
             "print(wheel_base('comfy_kitchen-0.2.37+spark.h3.sm120.cu130.1-cp312-abi3-manylinux_2_17_x86_64.whl')); " \
             "print(wheel_base('comfy_kitchen-0.2.37+spark.h3.sm120.cu130.1-cp312-abi3-win_amd64.whl')); " \
             "print(EXTENSION_SUFFIX)"
    check = subprocess.run([sys.executable, "-c", source], cwd=kit,
                           capture_output=True, text=True)
    assert check.returncode == 0, check.stderr
    assert check.stdout.splitlines() == ["0.2.37", "None", ".so"]
    extension_wheel = kit / "wheelhouse" / "synthetic.whl"
    with zipfile.ZipFile(extension_wheel, "w") as archive:
        archive.writestr("comfy_kitchen/backends/cuda/_C.abi3.so", b"linux")
        archive.writestr("comfy_kitchen/backends/cuda/_C.abi3.pyd", b"windows")
    extraction = subprocess.run(
        [sys.executable, "-c",
         "from pathlib import Path; import tempfile; from validate_wheels import extract_extension; "
         "print(extract_extension(Path('wheelhouse/synthetic.whl'), Path(tempfile.mkdtemp())).name)"],
        cwd=kit, capture_output=True, text=True,
    )
    assert extraction.returncode == 0, extraction.stderr
    assert extraction.stdout.strip() == "_C.abi3.so"
    release_wheel = kit / "wheelhouse" / (
        "comfy_kitchen-0.2.37+spark.h3.sm120.cu130.1-cp312-abi3-linux_x86_64.whl"
    )
    extension_wheel.rename(release_wheel)
    audit = kit / "results-audit" / "wheel-validation.json"
    audit.parent.mkdir()
    audit.write_text(json.dumps({
        "valid": True, "architecture": "sm120", "platform": "linux-x86_64",
        "wheels": [{"wheel": str(release_wheel),
                    "sha256": hashlib.sha256(release_wheel.read_bytes()).hexdigest()}],
    }), encoding="utf-8")
    package = subprocess.run([sys.executable, "bundle.py"], cwd=kit,
                             capture_output=True, text=True)
    assert package.returncode == 0, package.stderr
    release = kit / "release" / "ComfyUI-Spark-H3-linux-sm120-cu130.zip"
    with zipfile.ZipFile(release) as archive:
        assert archive.testzip() is None
        assert f"ComfyUI-Spark-H3/wheelhouse/{release_wheel.name}" in archive.namelist()
        packaged_identity = json.loads(archive.read("ComfyUI-Spark-H3/spark_h3_build.json"))
        assert packaged_identity["platform"] == "linux-x86_64"
    with zipfile.ZipFile(kit.with_suffix(".zip")) as archive:
        assert archive.testzip() is None
