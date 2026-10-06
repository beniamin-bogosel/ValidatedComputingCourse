"""Build the six-page lecture PDFs with pdfLaTeX.

Run from the course root: .venv/bin/python PDF_Lectures/build.py
Requires TeX Live (pdflatex), Poppler (pdfinfo), matplotlib, and numpy.
"""
from pathlib import Path
import shutil
import subprocess
import sys

folder = Path(__file__).resolve().parent
source = folder / "source"
build = folder.parent / "build" / "pdf_lectures"
build.mkdir(parents=True, exist_ok=True)
subprocess.run([sys.executable, str(source / "make_figures.py")], check=True)
for tex in sorted(source.glob("lecture*.tex")):
    command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
               "-output-directory=" + str(build), tex.name]
    log = build / (tex.stem + "-build.txt")
    with log.open("w") as output:
        for _ in range(2):
            result = subprocess.run(command, cwd=source, stdout=output, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError(f"PDF compilation failed; see {log}")
    compiled = build / (tex.stem + ".pdf")
    info = subprocess.check_output(["pdfinfo", str(compiled)], text=True)
    page_line = next(line for line in info.splitlines() if line.startswith("Pages:"))
    if int(page_line.split()[1]) != 6:
        raise RuntimeError(f"Expected six pages: {compiled}")
    tex_log = (build / (tex.stem + ".log")).read_text()
    if "Overfull \\hbox" in tex_log or "Overfull \\vbox" in tex_log:
        raise RuntimeError(f"Layout overflow; inspect {tex.stem}.log in {build}")
    target = folder / compiled.name
    shutil.copy2(compiled, target)
    print(target)
