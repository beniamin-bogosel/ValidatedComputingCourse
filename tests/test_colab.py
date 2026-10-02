"""Check exported material and the upload/bootstrap path without a Colab account."""

from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import sys
import shutil
import zipfile

import nbformat
import pytest

from scripts import colab, notebooks


def test_original_notebooks_start_with_current_colab_setup():
    runtime = colab.runtime_archive(colab.ROOT)
    assert (colab.ROOT / "vc_runtime.zip").read_bytes() == runtime
    runtime_hash = sha256(runtime).hexdigest()
    for py in notebooks.sources():
        notebook = nbformat.read(py.with_suffix(".ipynb"), as_version=4)
        first_code = next(cell for cell in notebook.cells if cell.cell_type == "code")
        assert first_code.metadata.get("tags") == ["colab-setup"], py
        assert first_code.source == colab.portable_setup_code(runtime_hash, py.parent.name), py


def test_preparing_sources_is_idempotent_and_keeps_pairs(tmp_path, monkeypatch):
    folder = tmp_path / "notebooks"
    folder.mkdir()
    for suffix in (".py", ".ipynb"):
        shutil.copy2(colab.ROOT / "notebooks" / ("00_setup" + suffix), folder)
    (tmp_path / "vc").mkdir()
    (tmp_path / "vc" / "__init__.py").write_text('__version__ = "test"\n')
    monkeypatch.setattr(colab, "ROOT", tmp_path)
    monkeypatch.setattr(notebooks, "ROOT", tmp_path)
    colab.prepare_sources()
    before = {path.name: path.read_bytes() for path in folder.iterdir()}
    colab.prepare_sources()
    assert before == {path.name: path.read_bytes() for path in folder.iterdir()}
    notebooks.check()


def bootstrap_process(tmp_path, uploaded_bytes, runtime_bytes, extra_code=""):
    """Run the actual setup cell with only upload and pip replaced by local doubles."""
    runtime_hash = sha256(runtime_bytes).hexdigest()
    code = colab.portable_setup_code(runtime_hash, "notebooks")
    code = code.replace('Path("/content")', f"Path({str(tmp_path)!r})")
    code = code.replace('Path("/content/validated-course")',
                        f"Path({str(tmp_path / 'course')!r})")
    harness = f'''
import sys, types, subprocess
from pathlib import Path
uploads = []
installs = []
def upload():
    uploads.append(True)
    return {{"vc_runtime.zip": {uploaded_bytes!r}}}
google = types.ModuleType("google")
colab_module = types.ModuleType("google.colab")
colab_module.files = types.SimpleNamespace(upload=upload)
sys.modules["google"] = google
sys.modules["google.colab"] = colab_module
subprocess.check_call = lambda command: installs.append(command)
setup = {code!r}
exec(setup)
{extra_code}
'''
    return subprocess.run([sys.executable, "-I", "-c", harness],
                          text=True, capture_output=True)


def test_zip_import_and_repeated_setup_use_course_helpers(tmp_path):
    runtime = colab.runtime_archive(colab.ROOT)
    result = bootstrap_process(tmp_path, runtime, runtime, '''
exec(setup)
assert len(uploads) == 1
assert len(installs) == 2
from fractions import Fraction
from vc.intervals import RationalInterval
assert RationalInterval(Fraction(1, 3)).contains(Fraction(1, 3))
assert str(Path(vc.__file__)).startswith(str(runtime_zip))
assert Path.cwd() == working_folder
''')
    assert result.returncode == 0, result.stderr


def test_wrong_uploaded_archive_fails_before_install(tmp_path):
    runtime = colab.runtime_archive(colab.ROOT)
    result = bootstrap_process(tmp_path, b"wrong edition", runtime)
    assert result.returncode != 0
    assert "Wrong vc_runtime.zip" in result.stderr
    assert not list(tmp_path.glob("vc-course-*.zip"))


def test_changed_cached_archive_is_rejected(tmp_path):
    runtime = colab.runtime_archive(colab.ROOT)
    result = bootstrap_process(tmp_path, runtime, runtime, '''
runtime_zip.write_bytes(b"corrupted")
exec(setup)
''')
    assert result.returncode != 0
    assert "cached vc archive has changed" in result.stderr


def test_runtime_archive_is_reproducible_and_contains_only_helper_source():
    runtime = colab.runtime_archive(colab.ROOT)
    assert runtime == colab.runtime_archive(colab.ROOT)
    with zipfile.ZipFile(io.BytesIO(runtime)) as archive:
        expected = {"vc/" + path.name for path in (colab.ROOT / "vc").glob("*.py")}
        assert set(archive.namelist()) == expected
        assert "vc/__init__.py" in expected


@pytest.mark.parametrize("replacement, message", [
    ('sys.modules["gmpy2"] = types.SimpleNamespace(version=lambda: "old")',
     "Old arithmetic libraries are still loaded"),
    ('sys.modules["vc"] = types.SimpleNamespace(__file__="/other/vc/__init__.py")',
     "Another vc copy is already loaded"),
])
def test_conflicting_loaded_modules_require_restart(tmp_path, replacement, message):
    runtime = colab.runtime_archive(colab.ROOT)
    result = bootstrap_process(tmp_path, runtime, runtime, replacement + "\nexec(setup)")
    assert result.returncode != 0
    assert message in result.stderr


@pytest.mark.parametrize("audience, expected_count", [("student", 36), ("instructor", 53)])
def test_export_preserves_material_and_excludes_private_student_content(tmp_path, audience, expected_count):
    path = colab.build(audience, tmp_path)
    with zipfile.ZipFile(path) as archive:
        prefix = path.stem + "/"
        names = archive.namelist()
        assert len(names) == len(set(names))
        if audience == "student":
            assert not any("/solutions/" in name or name.endswith(".pdf") for name in names)
        manifest = json.loads(archive.read(prefix + "RELEASE_MANIFEST.json"))
        for relative, info in manifest["files"].items():
            assert sha256(archive.read(prefix + relative)).hexdigest() == info["sha256"]
        notebook_names = [name for name in names if name.endswith(".ipynb")]
        assert len(notebook_names) == expected_count
        for name in notebook_names:
            exported = nbformat.reads(archive.read(name).decode(), as_version=4)
            nbformat.validate(exported)
            source = nbformat.read(colab.ROOT / name[len(prefix):], as_version=4)
            assert exported.cells[2].metadata.tags == ["colab-setup"]
            assert notebooks.signature(exported) == notebooks.signature(source)
            for cell in exported.cells:
                if cell.cell_type == "code":
                    assert cell.outputs == []
                    assert cell.execution_count is None
