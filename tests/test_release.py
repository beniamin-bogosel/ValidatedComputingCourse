"""Release regressions: avoid answer leakage and broken/corrupted distributions."""

import json
from pathlib import Path

import nbformat
import pytest

from scripts import check_links, release


def sample_notebook():
    cell = nbformat.v4.new_code_cell('print("student answer")')
    cell.execution_count = 1
    cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text="PRIVATE WORKED ANSWER")]
    cell.metadata = {"tags": ["exercise"], "private_note": "answer key"}
    notebook = nbformat.v4.new_notebook(cells=[cell])
    notebook.metadata["private_note"] = "answer key"
    return notebook


def test_starter_release_strips_all_outputs_and_private_metadata(tmp_path):
    notebook = release.prepare_notebook(sample_notebook(), "projects", tmp_path)
    assert notebook.cells[0].outputs == []
    assert notebook.cells[0].execution_count is None
    assert notebook.cells[0].metadata == {"tags": ["exercise"]}
    assert "private_note" not in notebook.metadata
    assert "PRIVATE WORKED ANSWER" not in nbformat.writes(notebook)


def test_unexecuted_lecture_cannot_be_published_as_checked(tmp_path):
    notebook = sample_notebook()
    notebook.cells[0].execution_count = None
    with pytest.raises(ValueError, match="unexecuted"):
        release.prepare_notebook(notebook, "notebooks", tmp_path)


def test_student_file_selection_excludes_solutions_pdfs_and_algorithm_keys(tmp_path):
    (tmp_path / "solutions").mkdir()
    (tmp_path / "solutions" / "answer.py").write_text("secret")
    (tmp_path / "Doc").mkdir()
    (tmp_path / "Doc" / "book.pdf").write_bytes(b"secret")
    selected = release.selected_files(tmp_path, "student")
    names = {path.relative_to(tmp_path).as_posix() for path in selected}
    assert not any("solutions" in name or name.endswith(".pdf") for name in names)
    assert "tests/test_geometry_and_mirrors.py" not in names


def test_manifest_detects_tampering_and_extra_files(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Course\n")
    release.write_manifest(tmp_path, "student")
    release.audit(tmp_path)
    readme.write_text("changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        release.audit(tmp_path)
    readme.write_text("# Course\n")
    (tmp_path / "answer.py").write_text("secret")
    with pytest.raises(ValueError, match="file set"):
        release.audit(tmp_path)


def test_link_checker_rejects_broken_or_external_local_paths(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("[Broken](missing.ipynb)")
    with pytest.raises(ValueError, match="missing"):
        check_links.check(tmp_path)
    readme.write_text("[Outside](../private.md)")
    with pytest.raises(ValueError, match="escapes"):
        check_links.check(tmp_path)


def test_html_links_point_to_reading_pages_and_original_code(tmp_path):
    source = tmp_path / "notebooks" / "lesson.ipynb"
    target = tmp_path / "reading" / "notebooks" / "lesson.html"
    readme = tmp_path / "README.md"
    readme_html = tmp_path / "reading" / "README.html"
    html = '<a href="../README.md">Guide</a><a href="../vc/intervals.py">Code</a>'
    converted = release.rewrite_links(html, source, target, {readme: readme_html}, tmp_path)
    assert 'href="../README.html"' in converted
    assert 'href="../../vc/intervals.py"' in converted


def test_saved_errors_are_not_released_as_completed(tmp_path):
    notebook = sample_notebook()
    notebook.cells[0].outputs = [nbformat.v4.new_output(
        "error", ename="AssertionError", evalue="bad bound", traceback=[])]
    with pytest.raises(ValueError, match="saved execution error"):
        release.prepare_notebook(notebook, "notebooks", tmp_path)


def test_build_rejects_unsynchronized_notebook_sources(tmp_path, monkeypatch):
    import jupytext
    root = tmp_path / "course"
    folder = root / "notebooks"
    folder.mkdir(parents=True)
    notebook = sample_notebook()
    nbformat.write(notebook, folder / "example.ipynb")
    notebook.cells[0].source = 'print("Changed mathematical assumption")'
    jupytext.write(notebook, folder / "example.py", fmt="py:percent")
    monkeypatch.setattr(release, "ROOT", root)
    monkeypatch.setattr(release.notebooks, "ROOT", root)
    monkeypatch.setattr(release.notebooks, "FOLDERS", ("notebooks",))
    output = tmp_path / "dist"
    with pytest.raises(ValueError, match="Pair differs"):
        release.build("student", output)
    assert not output.exists()


def test_sanitized_lecture_outputs_remain_valid_notebook_objects(tmp_path):
    notebook = sample_notebook()
    notebook.cells[0].outputs[0].text = f"Interpreter: {tmp_path}/.venv/bin/python"
    prepared = release.prepare_notebook(notebook, "notebooks", tmp_path)
    serialized = nbformat.writes(prepared)
    assert str(tmp_path) not in serialized
    assert "<course>" in serialized
    assert "Interpreter" in serialized


def test_student_audit_ignores_names_of_parent_directories(tmp_path):
    root = tmp_path / "solutions" / "student-course"
    root.mkdir(parents=True)
    (root / "README.md").write_text("# Student course\n")
    release.write_manifest(root, "student")
    assert release.audit(root)["audience"] == "student"
