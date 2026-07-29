#!/usr/bin/env python3
"""Validate the Claude marketplace and build deterministic distribution ZIPs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "advocacia-brasil"
MARKETPLACE_FILE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_DIR = ROOT / "plugins" / PLUGIN_NAME
PLUGIN_MANIFEST = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
SKILLS_DIR = PLUGIN_DIR / "skills"
DIST_DIR = ROOT / "dist"
TEST_CASES = ROOT / "tests" / "trigger-cases.json"
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE_PATTERN = re.compile(r"(?:`|\()((?:references|assets|scripts)/[^`)]+)(?:`|\))")


class ValidationError(Exception):
    pass


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationError(f"{path}: frontmatter YAML ausente")

    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValidationError(f"{path}: frontmatter YAML não foi fechado")

    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValidationError(f"{path}: linha inválida no frontmatter: {line}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    return metadata, parts[2]


def validate_skill(skill_dir: Path) -> str:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise ValidationError(f"{skill_dir}: SKILL.md ausente")

    metadata, body = parse_frontmatter(skill_file)
    name = metadata.get("name", "")
    description = metadata.get("description", "")

    if name != skill_dir.name:
        raise ValidationError(
            f"{skill_file}: name '{name}' não corresponde à pasta '{skill_dir.name}'"
        )
    if not NAME_PATTERN.fullmatch(name):
        raise ValidationError(f"{skill_file}: name deve usar kebab-case")
    if len(name) > 64:
        raise ValidationError(f"{skill_file}: name excede 64 caracteres")
    if not description:
        raise ValidationError(f"{skill_file}: description ausente")
    if len(description) > 200:
        raise ValidationError(
            f"{skill_file}: description possui {len(description)} caracteres; máximo 200"
        )
    if "TODO" in body or "FIXME" in body:
        raise ValidationError(f"{skill_file}: marcador inacabado encontrado")

    for relative in REFERENCE_PATTERN.findall(body):
        target = skill_dir / relative
        if not target.exists():
            raise ValidationError(f"{skill_file}: referência inexistente: {relative}")

    return name


def validate_trigger_cases(skill_names: set[str]) -> None:
    if not TEST_CASES.is_file():
        raise ValidationError(f"{TEST_CASES}: arquivo de testes ausente")

    data = json.loads(TEST_CASES.read_text(encoding="utf-8"))
    cases = data.get("skills", {})

    missing = skill_names - set(cases)
    extra = set(cases) - skill_names
    if missing or extra:
        raise ValidationError(
            f"Casos de gatilho divergentes. Faltando={sorted(missing)} Extras={sorted(extra)}"
        )

    for name, examples in cases.items():
        if not examples.get("positive") or not examples.get("negative"):
            raise ValidationError(
                f"{name}: incluir ao menos um caso positivo e um negativo"
            )


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise ValidationError(f"{path}: arquivo ausente")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: objeto JSON esperado")
    return data


def validate_marketplace() -> None:
    marketplace = load_json(MARKETPLACE_FILE)
    manifest = load_json(PLUGIN_MANIFEST)
    plugins = marketplace.get("plugins")

    if marketplace.get("name") != "advocacia-brasil-marketplace":
        raise ValidationError(f"{MARKETPLACE_FILE}: nome inesperado")
    if not isinstance(plugins, list) or len(plugins) != 1:
        raise ValidationError(f"{MARKETPLACE_FILE}: deve conter exatamente um plugin")

    entry = plugins[0]
    if entry.get("name") != PLUGIN_NAME:
        raise ValidationError(f"{MARKETPLACE_FILE}: plugin inesperado")
    if entry.get("source") != f"./plugins/{PLUGIN_NAME}":
        raise ValidationError(f"{MARKETPLACE_FILE}: source relativo inválido")
    if manifest.get("name") != PLUGIN_NAME:
        raise ValidationError(f"{PLUGIN_MANIFEST}: name inválido")
    if entry.get("version") != manifest.get("version"):
        raise ValidationError("Versões do marketplace e do plugin são divergentes")


def iter_skill_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            yield path


def build_zip(skill_dir: Path) -> Path:
    output = DIST_DIR / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in iter_skill_files(skill_dir):
            relative = path.relative_to(skill_dir.parent)
            info = zipfile.ZipInfo.from_file(path, arcname=relative.as_posix())
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())

    with zipfile.ZipFile(output) as archive:
        names = archive.namelist()
        expected = f"{skill_dir.name}/SKILL.md"
        if expected not in names:
            raise ValidationError(f"{output}: pacote não contém {expected}")
        if any(not name.startswith(f"{skill_dir.name}/") for name in names):
            raise ValidationError(f"{output}: arquivo fora da pasta raiz da skill")

    return output


def build_plugin_zip() -> Path:
    output = DIST_DIR / f"{PLUGIN_NAME}.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in iter_skill_files(PLUGIN_DIR):
            relative = path.relative_to(PLUGIN_DIR)
            info = zipfile.ZipInfo.from_file(path, arcname=relative.as_posix())
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())

    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        if ".claude-plugin/plugin.json" not in names:
            raise ValidationError(f"{output}: plugin.json ausente na raiz do pacote")
        for skill_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
            expected = f"skills/{skill_dir.name}/SKILL.md"
            if expected not in names:
                raise ValidationError(f"{output}: pacote não contém {expected}")
    return output


def write_checksums(packages: list[Path]) -> None:
    lines = []
    for package in packages:
        digest = hashlib.sha256(package.read_bytes()).hexdigest()
        lines.append(f"{digest}  {package.name}")
    (DIST_DIR / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validar sem gerar os arquivos ZIP.",
    )
    args = parser.parse_args()

    try:
        validate_marketplace()
        skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
        if len(skill_dirs) != 10:
            raise ValidationError(
                f"Esperadas 10 skills; encontradas {len(skill_dirs)}"
            )

        names = {validate_skill(skill_dir) for skill_dir in skill_dirs}
        validate_trigger_cases(names)

        if args.check:
            print(f"OK: marketplace, plugin e {len(names)} skills validados")
            return 0

        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        DIST_DIR.mkdir()

        packages = [build_plugin_zip()]
        packages.extend(build_zip(skill_dir) for skill_dir in skill_dirs)
        write_checksums(packages)
        print(
            f"OK: marketplace e {len(names)} skills validados; "
            f"{len(packages)} pacotes gerados em {DIST_DIR}"
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError, ValidationError) as error:
        print(f"ERRO: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
