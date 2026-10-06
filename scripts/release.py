"""Build self-contained student and instructor course editions with manifests.

Run after notebooks.py execute. Only explicitly selected files are distributed.
This does not install dependencies or publish either edition externally.
"""

import argparse
from copy import deepcopy
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import shutil
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

from bs4 import BeautifulSoup
import jupytext
import nbformat
from nbconvert import HTMLExporter

from scripts import check_links, notebooks


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0-rc1"
PUBLIC_FOLDERS = ("notebooks", "labs", "projects", "assignments", "templates")
PUBLIC_NOTES = ("tucker_chapter1_examples.md", "patriot_failure_reference.md",
                "siam_challenge_examples.md", "existing_course_review.md")
PUBLIC_TESTS = ("test_arithmetic_environment.py", "test_notebook_workflow.py")
COMMON_FILES = ("pyproject.toml", "requirements-lock.txt", "jupytext.toml", "syllabus.md", "COLAB.md", "vc_runtime.zip")
STARTER_FOLDERS = ("labs", "projects")
FORBIDDEN_PARTS = {".venv", ".git", ".cache", "__pycache__", ".ipynb_checkpoints"}


def selected_files(root, audience):
    paths = [root / name for name in COMMON_FILES]
    paths.extend((root / "PDF_Lectures").glob("lecture*.pdf"))
    for folder in PUBLIC_FOLDERS:
        for extension in ("*.py", "*.ipynb", "*.md"):
            paths.extend((root / folder).glob(extension))
    paths.extend((root / "vc").glob("*.py"))
    paths.extend(root / "scripts" / name for name in ("notebooks.py", "check_links.py"))
    if audience == "student":
        paths.extend(root / "Doc" / name for name in PUBLIC_NOTES)
        paths.extend(root / "tests" / name for name in PUBLIC_TESTS)
    else:
        paths.extend(root.glob("*.md"))
        paths.extend((root / "Doc").glob("*.md"))
        paths.extend((root / "tests").glob("*.py"))
        paths.extend((root / "solutions").glob("*.py"))
        paths.extend((root / "solutions").glob("*.ipynb"))
        paths.extend((root / "solutions").glob("*.md"))
        paths.append(root / "scripts" / "release.py")
        paths.append(root / "scripts" / "colab.py")
        paths.extend((root / "release").glob("*.md"))
        certificate = root / "build" / "certificates" / "mirror_t3.json"
        if certificate.exists():
            paths.append(certificate)
    return sorted(set(paths))


def scrub_text(value, root):
    """Remove author-machine paths from exported outputs, not mathematical data."""
    return value.replace(str(root), "<course>")


def scrub_output(value, root):
    if isinstance(value, str):
        return scrub_text(value, root)
    if isinstance(value, list):
        return [scrub_output(item, root) for item in value]
    if isinstance(value, dict):
        return {key: scrub_output(item, root) for key, item in value.items()}
    return value


def prepare_notebook(source, folder, root):
    notebook = deepcopy(source)
    notebooks.configure(notebook, folder)
    for cell in notebook.cells:
        # Only teaching tags belong in released cell metadata.
        tags = list(cell.metadata.get("tags", []))
        cell.metadata = {"tags": tags} if tags else {}
        if cell.cell_type != "code":
            continue
        if any(output.get("output_type") == "error" for output in cell.get("outputs", [])):
            raise ValueError("Notebook contains a saved execution error")
        if folder in STARTER_FOLDERS:
            # Strip every output, including accidentally saved student answers.
            cell.outputs = []
            cell.execution_count = None
        else:
            if folder in ("notebooks", "solutions") and cell.source.strip():
                if cell.execution_count is None:
                    raise ValueError("Completed notebook has unexecuted code; execute before release")
            cell.outputs = [nbformat.from_dict(output) for output in scrub_output(cell.outputs, root)]
    notebook.metadata = {key: notebook.metadata[key] for key in ("kernelspec", "course", "jupytext")}
    return notebook


def copy_materials(root, destination, audience):
    for source in selected_files(root, audience):
        relative = source.relative_to(root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == ".ipynb":
            notebook = prepare_notebook(nbformat.read(source, as_version=4), source.parent.name, root)
            nbformat.write(notebook, target)
            # Rewrite the paired source too, so metadata/signatures agree.
            jupytext.write(notebook, target.with_suffix(".py"), fmt="py:percent")
        elif source.suffix == ".py" and source.with_suffix(".ipynb").exists():
            continue  # Written with its notebook above.
        elif source.suffix in (".md", ".json"):
            target.write_text(scrub_text(source.read_text(), root))
        else:
            shutil.copy2(source, target)
    if audience == "student":
        readme = (root / "release" / "student_README.md").read_text()
        source_readme = (root / "README.md").read_text()
        table = source_readme.split("| Material |", 1)[1].split("\n\n", 1)[0]
        readme = readme.replace("{{COURSE_TABLE}}", "| Material |" + table)
        (destination / "README.md").write_text(readme)
        (destination / "references.md").write_text((root / "release" / "student_references.md").read_text())
        (destination / "Doc" / "mirror_trajectory_project.md").write_text(
            (root / "release" / "student_mirror_note.md").read_text())
        (destination / "Doc" / "existing_course_review.md").write_text(
            (root / "release" / "student_advanced_note.md").read_text())
        syllabus = destination / "syllabus.md"
        syllabus.write_text(syllabus.read_text().replace(
            " and the [detailed plan](COURSE_PLAN.md)", ""))
    else:
        readme = destination / "README.md"
        readme.write_text(readme.read_text() + "\n## Instructor edition\n\n"
                          "This archive includes solutions and full regression tests. Distribute the "
                          "separate student archive to students. [Reading copies](reading/index.html) "
                          "include both public notebooks and instructor material. HTML mathematical "
                          "typesetting uses the public MathJax CDN; Jupyter is the primary format.\n")

    # Release notes must not claim that optional local PDFs accompany the archive.
    for path in (destination / "Doc").glob("*.md"):
        text = path.read_text().replace("The PDF is available in this directory.",
                                      "The source book is an optional reading and is not included.")
        if path.name == "existing_course_review.md" and audience == "instructor":
            text = text.replace("Local source directory: `/home/beni/Courses/ValidatedNumerics`.",
                                "A locally held advanced-course snapshot was reviewed; its files are not distributed.")
            lines = text.splitlines()
            text = "\n".join("- Finite-dimensional Pluto notebook source (local snapshot, not included)."
                             if "](/home/beni/Courses/ValidatedNumerics/" in line else line
                             for line in lines) + "\n"
        path.write_text(text)
    references = destination / "references.md"
    references.write_text(references.read_text().replace("The locally supplied PDF is in `Doc/`.",
        "The book is optional further reading; no PDF is included in this release."))


def rewrite_links(html, source, output, mapping, root):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(href=True) + soup.find_all(src=True):
        attribute = "href" if tag.has_attr("href") else "src"
        url = urlsplit(tag[attribute])
        if url.scheme or url.netloc or not url.path:
            continue
        original = (source.parent / unquote(url.path)).resolve()
        target = mapping.get(original, original)
        if original.is_dir() and (original / "index.html").resolve() in mapping:
            target = mapping[(original / "index.html").resolve()]
        relative = Path(os.path.relpath(target, output.parent)).as_posix()
        if url.fragment:
            relative += "#" + url.fragment
        tag[attribute] = relative
    return str(soup)


def page(title, body):
    return ("<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{escape(title)}</title><style>body{{max-width:980px;margin:3rem auto;"
            "padding:0 1rem;font:17px/1.6 system-ui,sans-serif;color:#20252b}}"
            "table{border-collapse:collapse}th,td{padding:.4rem .7rem;border:1px solid #ccc}"
            "code,pre{font-family:monospace}pre{overflow:auto;background:#f5f5f5;padding:1rem}"
            "a{color:#125aa0}</style><body>" + body + "</body></html>")


def reading_copies(root, audience):
    sources = [path for path in check_links.course_documents(root) if path.suffix in (".md", ".ipynb")]
    mapping = {source.resolve(): (root / "reading" / source.relative_to(root)).with_suffix(".html")
               for source in sources}
    exporter = HTMLExporter()
    notebook_entries = []
    for source in sources:
        target = mapping[source.resolve()]
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix == ".ipynb":
            notebook = nbformat.read(source, as_version=4)
            title = notebook.cells[0].source.splitlines()[0].lstrip("# ") if notebook.cells else source.stem
            html, _ = exporter.from_notebook_node(notebook, resources={"metadata": {"name": title}})
            notebook_entries.append((source.parent.name, title, target))
        else:
            # The same renderer handles LaTeX in reference notes and lectures.
            document = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(source.read_text())])
            html, _ = exporter.from_notebook_node(document, resources={"metadata": {"name": source.stem}})
        target.write_text(rewrite_links(html, source, target, mapping, root))
    index = root / "reading" / "index.html"
    body = f"<h1>Validated Computing — {audience} reading copies</h1>"
    body += "<p><a href='README.html'>Course guide and installation</a>. "
    body += "Use Jupyter for interactive work. HTML math uses the public MathJax CDN.</p>"
    for folder in notebooks.FOLDERS:
        entries = [entry for entry in notebook_entries if entry[0] == folder]
        if not entries:
            continue
        body += f"<h2>{escape(folder.title())}</h2><ul>"
        for _, title, path in entries:
            href = path.relative_to(index.parent).as_posix()
            body += f"<li><a href='{escape(href)}'>{escape(title)}</a></li>"
        body += "</ul>"
    index.write_text(page("Validated Computing reading index", body))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_manifest(root, audience):
    paths = sorted(path for path in root.rglob("*") if path.is_file())
    files = {path.relative_to(root).as_posix(): {"sha256": digest(path), "bytes": path.stat().st_size}
             for path in paths if path.name != "RELEASE_MANIFEST.json"}
    manifest = {"release": VERSION, "audience": audience, "files": files,
                "notebooks": sum(name.endswith(".ipynb") for name in files),
                "tested_target": "CPython 3.12, Linux x86_64",
                "reference_code": "vc is public teaching infrastructure; worked solutions are instructor-only"}
    (root / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def audit(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "RELEASE_MANIFEST.json").read_text())
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    expected = set(manifest["files"]) | {"RELEASE_MANIFEST.json"}
    if actual != expected:
        raise ValueError("Release file set differs from its manifest")
    for name, info in manifest["files"].items():
        path = root / name
        if digest(path) != info["sha256"]:
            raise ValueError(f"Release hash mismatch: {name}")
        if any(part in FORBIDDEN_PARTS for part in path.relative_to(root).parts):
            raise ValueError(f"Private/runtime directory in release: {name}")
        lecture_pdf = (path.parent == root / "PDF_Lectures"
                       and path.match("lecture*.pdf"))
        if path.suffix == ".pyc" or (path.suffix == ".pdf" and not lecture_pdf):
            raise ValueError(f"Excluded file type: {name}")
        if manifest["audience"] == "student" and ("solutions" in path.relative_to(root).parts or "_solution" in path.name):
            raise ValueError(f"Instructor material in student release: {name}")
        if path.suffix == ".ipynb":
            notebook = nbformat.read(path, as_version=4)
            paired = jupytext.read(path.with_suffix(".py"))
            if notebooks.signature(notebook) != notebooks.signature(paired):
                raise ValueError(f"Mismatched released notebook pair: {name}")
            if path.parent.name in STARTER_FOLDERS:
                for cell in notebook.cells:
                    if cell.cell_type == "code" and (cell.outputs or cell.execution_count is not None):
                        raise ValueError(f"Starter output in release: {name}")
    check_links.check(root)
    print(f"Audited {manifest['audience']} release: {len(expected)} files, {manifest['notebooks']} notebooks")
    return manifest


def build(audience, output):
    notebooks.check()  # Refuse stale pairs instead of silently selecting one source.
    output.mkdir(parents=True, exist_ok=True)
    name = f"validated-computing-{VERSION}-{audience}"
    with tempfile.TemporaryDirectory(prefix="course-release-", dir=output) as temporary:
        stage = Path(temporary) / name
        stage.mkdir()
        copy_materials(ROOT, stage, audience)
        reading_copies(stage, audience)
        write_manifest(stage, audience)
        audit(stage)
        archive = output / (name + ".zip")
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    bundle.write(path, path.relative_to(stage.parent))
        print(f"Built {archive}")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "audit"))
    parser.add_argument("--audience", choices=("student", "instructor", "both"), default="both")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--root", type=Path)
    arguments = parser.parse_args()
    if arguments.command == "audit":
        if arguments.root is None:
            parser.error("audit requires --root")
        audit(arguments.root)
    else:
        audiences = ("student", "instructor") if arguments.audience == "both" else (arguments.audience,)
        for audience in audiences:
            build(audience, arguments.output.resolve())
