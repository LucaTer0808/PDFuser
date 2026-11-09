import argparse
import os
import shutil
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

PDF_SIGNATURE = b"%PDF-"
APP_NAME = "pdfuse"
SHELL_RC_FILES = (".bashrc", ".zshrc", ".profile")
SHELL_BLOCK_START = "# >>> pdfuse >>>"
SHELL_BLOCK_END = "# <<< pdfuse <<<"


def validate_pdf(path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"Datei nicht gefunden: {path}")
    with path.open("rb") as file:
        header = file.read(1024)
        if PDF_SIGNATURE not in header:
            raise ValueError(f"Keine PDF-Datei (fehlende PDF-Signatur): {path}")
        try:
            reader = PdfReader(file)
            _ = len(reader.pages)
        except Exception as error:
            raise ValueError(f"PDF-Datei nicht lesbar: {path} ({error})") from error


def merge_pdfs(input1: Path, input2: Path, source: Path) -> int:
    writer = PdfWriter()
    writer.append(input1)
    writer.append(input2)
    source.parent.mkdir(parents=True, exist_ok=True)
    with source.open("wb") as file:
        writer.write(file)
    return len(writer.pages)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hängt --input2 hinten an --input1 an und speichert das Ergebnis unter --source."
    )
    parser.add_argument("--input1", type=Path, help="Erste PDF-Datei")
    parser.add_argument("--input2", type=Path, help="Zweite PDF-Datei (wird hinten angefügt)")
    parser.add_argument(
        "--source",
        "--output",
        dest="source",
        type=Path,
        default=Path("merged.pdf"),
        help="Zielpfad inkl. Dateiname (Standard: merged.pdf im aktuellen Verzeichnis)",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="pdfuse samt Installationsverzeichnis und Shell-Eintrag entfernen",
    )
    args = parser.parse_args(argv)
    if not args.uninstall and (args.input1 is None or args.input2 is None):
        parser.error("--input1 und --input2 sind erforderlich.")
    return args


def install_dir() -> Path:
    data_home = os.environ.get("XDG_DATA_HOME")
    base = Path(data_home) if data_home else Path.home() / ".local" / "share"
    return base / APP_NAME


def remove_shell_block(rc_file: Path) -> bool:
    if not rc_file.is_file():
        return False
    lines = rc_file.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = []
    inside_block = False
    found = False
    for line in lines:
        stripped = line.strip()
        if not inside_block and stripped == SHELL_BLOCK_START:
            inside_block = True
            found = True
            if kept and not kept[-1].strip():
                kept.pop()
        elif inside_block:
            if stripped == SHELL_BLOCK_END:
                inside_block = False
        else:
            kept.append(line)
    if found:
        rc_file.write_text("".join(kept), encoding="utf-8")
    return found


def uninstall() -> int:
    removed_any = False
    for name in SHELL_RC_FILES:
        if remove_shell_block(Path.home() / name):
            print(f"Shell-Eintrag entfernt aus: ~/{name}")
            removed_any = True
    target = install_dir()
    if target.exists():
        shutil.rmtree(target)
        print(f"Installationsverzeichnis entfernt: {target}")
        removed_any = True
    if not removed_any:
        print("pdfuse ist nicht installiert, nichts zu entfernen.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.uninstall:
        return uninstall()
    try:
        validate_pdf(args.input1)
        validate_pdf(args.input2)
        if args.source.resolve() in (args.input1.resolve(), args.input2.resolve()):
            raise ValueError("--source darf nicht auf eine Eingabedatei zeigen.")
        pages = merge_pdfs(args.input1, args.input2, args.source)
    except ValueError as error:
        print(f"Fehler: {error}", file=sys.stderr)
        return 1
    print(f"{pages} Seiten gespeichert unter: {args.source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
