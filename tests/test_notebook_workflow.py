"""Protect paired sources and prevent stale or incomplete outputs passing review."""

import jupytext
import nbformat
import pytest

from scripts import notebooks


@pytest.fixture
def pair(tmp_path, monkeypatch):
    monkeypatch.setattr(notebooks, "ROOT", tmp_path)
    monkeypatch.setattr(notebooks, "FOLDERS", ("notebooks",))
    folder = tmp_path / "notebooks"
    folder.mkdir()
    path = folder / "example.py"
    nb = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_markdown_cell("An exact computation"),
        nbformat.v4.new_code_cell("print(1 + 1)"),
    ])
    jupytext.write(nb, path, fmt="py:percent")
    notebooks.sync("py")
    ipynb = path.with_suffix(".ipynb")
    executed = nbformat.read(ipynb, as_version=4)
    executed.cells[1].outputs = [nbformat.v4.new_output("stream", name="stdout", text="2\n")]
    executed.cells[1].execution_count = 1
    nbformat.write(executed, ipynb)
    return path, ipynb


def test_unchanged_pair_keeps_outputs(pair):
    _, ipynb = pair
    notebooks.sync("py")
    assert nbformat.read(ipynb, as_version=4).cells[1].outputs[0].text == "2\n"
    notebooks.check()


def test_changed_source_clears_all_outputs(pair):
    py, ipynb = pair
    nb = jupytext.read(py)
    nb.cells[0].source = "Changed assumptions"
    jupytext.write(nb, py, fmt="py:percent")
    notebooks.sync("py")
    cell = nbformat.read(ipynb, as_version=4).cells[1]
    assert cell.outputs == []
    assert cell.execution_count is None


def test_diverged_pair_is_rejected(pair):
    py, _ = pair
    nb = jupytext.read(py)
    nb.cells[1].source = "print(3)"
    jupytext.write(nb, py, fmt="py:percent")
    with pytest.raises(ValueError, match="Pair differs"):
        notebooks.check()


def test_notebook_edit_can_be_explicit_source(pair):
    py, ipynb = pair
    nb = nbformat.read(ipynb, as_version=4)
    nb.cells[0].source = "Edited in Jupyter"
    nbformat.write(nb, ipynb)
    notebooks.sync("ipynb")
    assert jupytext.read(py).cells[0].source == "Edited in Jupyter"
    notebooks.check()


def test_error_outputs_are_rejected(pair):
    _, ipynb = pair
    nb = nbformat.read(ipynb, as_version=4)
    nb.cells[1].outputs = [nbformat.v4.new_output(
        "error", ename="ArithmeticError", evalue="bad", traceback=[])]
    nbformat.write(nb, ipynb)
    with pytest.raises(ValueError, match="Saved error output"):
        notebooks.check()



def test_project_exercises_need_tags(tmp_path, monkeypatch):
    monkeypatch.setattr(notebooks, "ROOT", tmp_path)
    monkeypatch.setattr(notebooks, "FOLDERS", ("projects",))
    folder = tmp_path / "projects"
    folder.mkdir()
    path = folder / "example.py"
    notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(
        'raise NotImplementedError("Student task")')])
    jupytext.write(notebook, path, fmt="py:percent")
    notebooks.sync("py")
    with pytest.raises(ValueError, match="Untagged exercise"):
        notebooks.check()
    notebook.cells[0].metadata["tags"] = ["exercise"]
    jupytext.write(notebook, path, fmt="py:percent")
    notebooks.sync("py")
    notebooks.check()
    saved = nbformat.read(path.with_suffix(".ipynb"), as_version=4)
    assert saved.metadata.course.kind == "student_project"
