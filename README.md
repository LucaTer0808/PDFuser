# PDFuser

`pdfuse` hängt zwei PDF-Dateien aneinander: `--input2` wird hinten an `--input1` angefügt, das Ergebnis landet unter `--source` (Alias `--output`).

### Installation

```
./install.sh
```

Voraussetzung ist [uv](https://docs.astral.sh/uv/). Das Skript legt eine isolierte Python-Umgebung unter `~/.local/share/pdfuse/venv` an, die exakt die Versionen aus `uv.lock` installiert (`uv sync --frozen`, Hashes werden geprüft). Anschließend verlinkt es `pdfuse` unter `~/.local/share/pdfuse/bin` und trägt diesen Ordner per Eintrag in `~/.bashrc` (bzw. `~/.zshrc`) in den `PATH` ein. Danach ein neues Terminal öffnen.

### Nutzung

```
pdfuse --input1 a.pdf --input2 b.pdf --output /pfad/ergebnis.pdf
```

Ohne `--output` wird `merged.pdf` im aktuellen Verzeichnis erzeugt.

### Deinstallation

```
pdfuse --uninstall
```

Entfernt das Installationsverzeichnis und den Eintrag in der Shell-Konfiguration.
