"""Assemble the independent Spark-VPack ComfyUI package."""
from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "Spark-VPack"
DEFAULT_VERSION = "0.1.0"
SOURCE_ROOT = REPOSITORY_ROOT / "comfyui" / "compact_ref2va"

PACKAGE_FILES = {
    SOURCE_ROOT / "__init__.py": "__init__.py",
    REPOSITORY_ROOT / "comfyui_ref2va.py": "comfyui_ref2va.py",
    REPOSITORY_ROOT / "comfyui_ref2va_compat.py": "comfyui_ref2va_compat.py",
    SOURCE_ROOT / "README.md": "README.md",
    SOURCE_ROOT / "README.zh-CN.md": "README.zh-CN.md",
    REPOSITORY_ROOT / "LICENSE": "LICENSE",
}


def assemble(output_dir: Path, *, version: str, publisher_id: str) -> Path:
    """Create and return an unpacked, registry-compatible custom-node tree."""
    target = output_dir / PACKAGE_NAME
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for source, relative in PACKAGE_FILES.items():
        shutil.copy2(source, target / relative)

    template = (SOURCE_ROOT / "pyproject.toml.in").read_text(encoding="utf-8")
    (target / "pyproject.toml").write_text(
        template.replace("@VERSION@", version).replace(
            "@PUBLISHER_ID@", publisher_id
        ),
        encoding="utf-8",
    )
    return target


def make_zip(package_dir: Path, output_dir: Path, *, version: str) -> Path:
    """Create a deterministic archive with one installable root directory."""
    archive = output_dir / f"{PACKAGE_NAME}-{version}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(
        archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for path in sorted(package_dir.rglob("*")):
            if not path.is_file():
                continue
            relative = Path(PACKAGE_NAME) / path.relative_to(package_dir)
            info = zipfile.ZipInfo(
                relative.as_posix(), date_time=(2026, 1, 1, 0, 0, 0)
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, path.read_bytes())
    return archive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument(
        "--publisher-id",
        required=True,
        help="existing Comfy Registry publisher id",
    )
    parser.add_argument("--no-zip", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    package = assemble(
        args.output_dir, version=args.version, publisher_id=args.publisher_id
    )
    print(package)
    if not args.no_zip:
        print(make_zip(package, args.output_dir, version=args.version))


if __name__ == "__main__":
    main()
