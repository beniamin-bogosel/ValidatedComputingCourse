"""Build the application notebooks and the applications PDF.

Run from the course root with the course environment:

    .venv/bin/python applications/build.py            # sync, execute, figures, PDF
    .venv/bin/python applications/build.py sync       # .py -> .ipynb only
    .venv/bin/python applications/build.py execute [app09 ...]
    .venv/bin/python applications/build.py pdf        # figures from executed notebooks + LaTeX

The .py files (Jupytext percent format) are the editable sources. Figures used by
the LaTeX document come from notebook cells tagged ``tex-figure-<name>``.
"""

import base64
import os
import shutil
import subprocess
import sys
from pathlib import Path

import jupytext
import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parent
TEX = FOLDER / "tex"
BUILD = ROOT / "build" / "applications"
KERNEL = {"display_name": "Python (Validated Computing)", "language": "python",
          "name": "validated-computing"}


def sources(names=()):
    paths = sorted(FOLDER.glob("app*.py"))
    if names:
        paths = [p for p in paths if any(p.stem.startswith(n) for n in names)]
    return paths


def sync(names=()):
    for py in sources(names):
        nb = jupytext.read(py)
        nb.metadata["kernelspec"] = KERNEL
        nb.metadata["course"] = {"kind": "application"}
        nb.metadata["jupytext"] = {"formats": "ipynb,py:percent",
                                   "notebook_metadata_filter": "kernelspec,jupytext,course",
                                   "cell_metadata_filter": "tags"}
        jupytext.write(nb, py, fmt="py:percent")
        nbformat.write(nb, py.with_suffix(".ipynb"))
        print("paired", py.relative_to(ROOT), flush=True)


def execute(names=()):
    # The repository root goes on the path so `import vc` works without an install.
    os.environ["PYTHONPATH"] = str(ROOT) + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["MPLBACKEND"] = "module://matplotlib_inline.backend_inline"
    for py in sources(names):
        path = py.with_suffix(".ipynb")
        nb = nbformat.read(path, as_version=4)
        km = KernelManager(kernel_name="python3")
        km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
        client = NotebookClient(nb, km=km, timeout=600, startup_timeout=60,
                                resources={"metadata": {"path": str(FOLDER)}})
        print("executing", path.relative_to(ROOT), flush=True)
        client.execute(cleanup_kc=True)
        nbformat.write(nb, path)


def extract_figures():
    figures = TEX / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    for path in sorted(FOLDER.glob("app*.ipynb")):
        nb = nbformat.read(path, as_version=4)
        for cell in nb.cells:
            for tag in cell.metadata.get("tags", []):
                if not tag.startswith("tex-figure-"):
                    continue
                images = [o["data"]["image/png"] for o in cell.get("outputs", [])
                          if "image/png" in o.get("data", {})]
                if not images:
                    raise RuntimeError(f"{path.name}: cell tagged {tag} has no image; execute first")
                target = figures / (tag.removeprefix("tex-figure-") + ".png")
                target.write_bytes(base64.b64decode(images[-1]))
                print("figure", target.relative_to(ROOT))


def pdf():
    extract_figures()
    BUILD.mkdir(parents=True, exist_ok=True)
    command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
               "-output-directory=" + str(BUILD), "applications.tex"]
    log = BUILD / "applications-build.txt"
    with log.open("w") as output:
        for _ in range(3):           # third pass settles the table of contents
            if subprocess.run(command, cwd=TEX, stdout=output, stderr=subprocess.STDOUT).returncode:
                raise RuntimeError(f"PDF compilation failed; see {log}")
    shutil.copy2(BUILD / "applications.pdf", FOLDER / "applications.pdf")
    print("wrote", (FOLDER / "applications.pdf").relative_to(ROOT))


if __name__ == "__main__":
    command, names = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("all", [])
    if command in ("sync", "all"):
        sync(names)
    if command in ("execute", "all"):
        execute(names)
    if command in ("pdf", "all"):
        pdf()
