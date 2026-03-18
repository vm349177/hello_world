import argparse
import sys
from pathlib import Path


REQUIRED_SECTIONS = {"goal", "requirements", "testing"}


def normalize(text: str) -> str:
    return text.strip().lower()


def validate_sections(markdown: str) -> list[str]:
    lines = [line.strip().lower() for line in markdown.splitlines() if line.strip()]
    found = {line.lstrip("# ") for line in lines if line.startswith("#") or line.startswith("##")}
    missing = [section for section in REQUIRED_SECTIONS if section not in found]
    return missing


def ensure_has_content(markdown: str) -> None:
    if len(markdown.strip()) < 50:
        raise ValueError("Spec content too short; provide more detail.")


def validate_spec_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Spec file not found: {path}")
    content = path.read_text(encoding="utf-8")
    ensure_has_content(content)
    missing_sections = validate_sections(content)
    if missing_sections:
        raise ValueError(
            "Missing required sections: " + ", ".join(sorted(missing_sections))
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate spec markdown structure")
    parser.add_argument("spec_path", type=Path, help="Path to spec markdown file")
    args = parser.parse_args()
    try:
        validate_spec_file(args.spec_path)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Spec validation failed: {exc}", file=sys.stderr)
        return 1
    print("Spec validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
