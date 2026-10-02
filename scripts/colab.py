"""Maintain shared Colab setup cells and export notebook editions.

Usage: python -m scripts.colab
The companion ZIP contains only the pure-Python vc package, not solutions.
"""

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
from textwrap import indent
import zipfile

import nbformat
import jupytext

from scripts import notebooks, release

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = ["numpy>=1.26", "matplotlib>=3.8", "gmpy2==2.3.1",
                "python-flint==0.9.0", "jupytext>=1.16"]


def runtime_archive(root):
    """Make a reproducible ZIP importable by Python, with no native libraries."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sorted((root / "vc").glob("*.py")):
            entry = zipfile.ZipInfo("vc/" + source.name)
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, source.read_bytes())
    return buffer.getvalue()


def setup_code(runtime_hash, folder):
    # Keep this cell explicit: it is visible to students in every exported notebook.
    return f'''import hashlib
from pathlib import Path
import subprocess
import sys
from google.colab import files

if sys.version_info < (3, 12):
    raise RuntimeError("This course needs a Python 3.12 or newer Colab runtime.")

# Upload the small companion file supplied with the Colab course edition.
expected_hash = {runtime_hash!r}
runtime_zip = Path("/content") / ("vc-course-" + expected_hash + ".zip")
if not runtime_zip.exists():
    print("Select vc_runtime.zip from the extracted Colab course folder.")
    uploaded = files.upload()
    if len(uploaded) != 1:
        raise ValueError("Upload only vc_runtime.zip, then run this cell again.")
    archive_bytes = next(iter(uploaded.values()))
    if hashlib.sha256(archive_bytes).hexdigest() != expected_hash:
        raise ValueError("Wrong vc_runtime.zip: use the one supplied with this notebook.")
    runtime_zip.write_bytes(archive_bytes)

if hashlib.sha256(runtime_zip.read_bytes()).hexdigest() != expected_hash:
    raise ValueError("The cached vc archive has changed; start a fresh runtime.")

# Keep Colab's existing NumPy and plotting stack when they satisfy these bounds.
# Install MPFR/Arb bindings, not the full local Jupyter environment.
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "--quiet",
    {', '.join(repr(package) for package in DEPENDENCIES)}
])
import gmpy2
import flint
if gmpy2.version() != "2.3.1" or flint.__version__ != "0.9.0":
    raise RuntimeError("Old arithmetic libraries are still loaded. Restart the session and run setup first.")

if str(runtime_zip) not in sys.path:
    sys.path.insert(0, str(runtime_zip))

import vc
if not vc.__file__.startswith(str(runtime_zip) + "/"):
    raise RuntimeError("Another vc copy is already loaded. Start a fresh runtime.")

# Preserve the relative output paths used by the project notebooks.
import os
working_folder = Path("/content/validated-course") / {folder!r}
working_folder.mkdir(parents=True, exist_ok=True)
os.chdir(working_folder)
print("Course helpers ready:", vc.__version__)
'''


SETUP_TEXT = """## Google Colab setup — run this cell first

**Local Jupyter:** this cell skips Colab setup; use your installed course environment.

Use a **CPU Python runtime** (Python 3.12 or newer). Run the next cell and select
**vc_runtime.zip** from this edition when prompted. It loads the course helpers
and installs the arithmetic libraries. Repeat setup whenever you get a new runtime.
No Drive mounting or local Python installation is required.
Use this setup instead of the local installation and kernel-selection instructions
in the original course text.

Save a copy of this notebook in Drive, or download it after editing. Files created
by the project are under `/content/validated-course/build/certificates/`; download
those separately from Colab's Files panel. Runtime files are temporary.

Open other course notebooks using **File → Upload notebook**, choosing them from
the extracted course folder. Relative course links are intended for local Jupyter
and do not open sibling notebooks automatically in Colab. In labs, complete exercise
cells before running their diagnostics: `NotImplementedError` marks an unfinished task.
"""


def portable_setup_code(runtime_hash, folder):
    return (
        "try:\n"
        "    import google.colab\n"
        "except ImportError:\n"
        "    print(\"Local Jupyter: using the installed course environment.\")\n"
        "else:\n"
        + indent(setup_code(runtime_hash, folder), "    ")
    ).rstrip()


def prepare_sources():
    """Put setup before imports in the actual paired notebooks, not only exports."""
    notebooks.check()
    runtime_bytes = runtime_archive(ROOT)
    (ROOT / "vc_runtime.zip").write_bytes(runtime_bytes)
    runtime_hash = sha256(runtime_bytes).hexdigest()
    for py in notebooks.sources():
        path = py.with_suffix(".ipynb")
        notebook = nbformat.read(path, as_version=4)
        before = notebooks.signature(notebook)
        notebook.cells = [cell for cell in notebook.cells
                          if "colab-setup" not in cell.metadata.get("tags", [])]
        notebook.cells[1:1] = [
            nbformat.v4.new_markdown_cell(SETUP_TEXT, metadata={"tags": ["colab-setup"]}),
            nbformat.v4.new_code_cell(portable_setup_code(runtime_hash, py.parent.name),
                                     metadata={"tags": ["colab-setup"]}),
        ]
        if notebooks.signature(notebook) == before:
            continue
        for cell in notebook.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        notebooks.configure(notebook, py.parent.name)
        nbformat.write(notebook, path)
        jupytext.write(notebook, py, fmt="py:percent")
    notebooks.check()
    print("Prepared original notebook pairs and vc_runtime.zip; execute before exporting.")


def convert(source, runtime_hash):
    notebook = release.prepare_notebook(
        nbformat.read(source, as_version=4), source.parent.name, ROOT)
    # Colab copies are edited as notebooks; they are not additional Jupytext pairs.
    notebook.metadata.pop("jupytext", None)
    notebook.metadata["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3"}
    expected = portable_setup_code(runtime_hash, source.parent.name)
    first_code = next((cell for cell in notebook.cells if cell.cell_type == "code"), None)
    if first_code is None or first_code.source != expected:
        raise ValueError("Missing or outdated Colab setup; run --prepare-sources, then execute notebooks.")
    # Old local outputs would otherwise misleadingly describe a Colab execution.
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    return notebook


def build(audience, output):
    notebooks.check()
    runtime_bytes = runtime_archive(ROOT)
    runtime_hash = sha256(runtime_bytes).hexdigest()
    name = f"validated-computing-{release.VERSION}-colab-{audience}"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="colab-build-", dir=output) as temporary:
        destination = Path(temporary) / name
        destination.mkdir()
        (destination / "vc_runtime.zip").write_bytes(runtime_bytes)
        guide = (ROOT / "COLAB.md").read_text()
        (destination / "README.md").write_text(guide)
        folders = list(release.PUBLIC_FOLDERS)
        if audience == "instructor":
            folders.append("solutions")
        count = 0
        for folder in folders:
            for source in sorted((ROOT / folder).glob("*.ipynb")):
                target = destination / folder / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                nbformat.write(convert(source, runtime_hash), target)
                count += 1
        # Include public helper source for reading, as in the local course edition.
        for source in sorted((ROOT / "vc").glob("*.py")):
            target = destination / "vc" / source.name
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(source.read_bytes())
        manifest = release.write_manifest(destination, audience)
        manifest["format"] = "Colab notebooks without Jupytext pairs"
        manifest["runtime_sha256"] = runtime_hash
        manifest["setup_dependencies"] = DEPENDENCIES
        manifest["hosted_colab_tested"] = False
        (destination / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
        archive_path = output / (name + ".zip")
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(destination.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(destination.parent))
    print(f"Built {archive_path} ({count} Colab notebooks)")
    return archive_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-sources", action="store_true",
                        help="Update setup in original notebook pairs and write vc_runtime.zip")
    parser.add_argument("--audience", choices=("student", "instructor", "both"), default="both")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    arguments = parser.parse_args()
    if arguments.prepare_sources:
        prepare_sources()
    else:
        audiences = ("student", "instructor") if arguments.audience == "both" else (arguments.audience,)
        for audience in audiences:
            build(audience, arguments.output)
