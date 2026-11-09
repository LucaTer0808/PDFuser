import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

PDF_SIGNATURE = b"%PDF-"


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
    parser.add_argument("--input1", required=True, type=Path, help="Erste PDF-Datei")
    parser.add_argument("--input2", required=True, type=Path, help="Zweite PDF-Datei (wird hinten angefügt)")
    parser.add_argument(
        "--source",
        "--output",
        dest="source",
        type=Path,
        default=Path("merged.pdf"),
        help="Zielpfad inkl. Dateiname (Standard: merged.pdf im aktuellen Verzeichnis)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
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
