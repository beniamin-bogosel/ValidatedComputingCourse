"""Explicit notebook pairing, structural checks, and fresh-kernel execution.

Run from the project environment: python scripts/notebooks.py sync|check|execute.
"""

import argparse
import ast
from copy import deepcopy
from pathlib import Path
import os
import socket
import sys

import jupytext
import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ("notebooks", "labs", "solutions", "templates", "assignments", "projects")
KERNEL = {"display_name": "Python (Validated Computing)", "language": "python",
          "name": "validated-computing"}


def signature(nb):
    return [(c.cell_type, c.source, list(c.metadata.get("tags", []))) for c in nb.cells]


def sources():
    return sorted(p for folder in FOLDERS for p in (ROOT / folder).glob("*.py"))


def configure(nb, folder):
    nb.metadata["kernelspec"] = KERNEL
    nb.metadata["course"] = {"kind": {"notebooks": "lecture", "labs": "student_lab",
                                      "solutions": "instructor_solution",
                                      "templates": "template", "assignments": "assessment",
                                      "projects": "student_project"}[folder]}
    nb.metadata["jupytext"] = {
        "formats": "ipynb,py:percent",
        "notebook_metadata_filter": "kernelspec,jupytext,course",
        "cell_metadata_filter": "tags",
    }


def sync(direction):
    paths = sources() if direction == "py" else sorted(
        p for folder in FOLDERS for p in (ROOT / folder).glob("*.ipynb"))
    for path in paths:
        py, ipynb = path.with_suffix(".py"), path.with_suffix(".ipynb")
        nb = jupytext.read(path)
        configure(nb, path.parent.name)
        if direction == "py" and ipynb.exists():
            old = nbformat.read(ipynb, as_version=4)
            if signature(old) == signature(nb):
                nb = old  # retain executed outputs only if ALL cells are unchanged
                configure(nb, path.parent.name)
        jupytext.write(nb, py, fmt="py:percent")
        nbformat.write(nb, ipynb)
        print(f"paired {py.relative_to(ROOT)}", flush=True)


def check():
    count = 0
    for folder in FOLDERS:
        for ipynb in (ROOT / folder).glob("*.ipynb"):
            if not ipynb.with_suffix(".py").exists():
                raise ValueError(f"Missing text pair: {ipynb}")
    for py in sources():
        ipynb = py.with_suffix(".ipynb")
        nb = nbformat.read(ipynb, as_version=4)
        nbformat.validate(nb)
        if signature(nb) != signature(jupytext.read(py)):
            raise ValueError(f"Pair differs: {py}; sync from the intended source")
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == "code":
                ast.parse(cell.source, filename=f"{py}:cell{i}")
                if py.parent.name == "solutions" and "NotImplementedError" in cell.source:
                    raise ValueError(f"Incomplete solution in {py}:cell{i}")
                if py.parent.name in ("labs", "projects"):
                    if "NotImplementedError" in cell.source and "exercise" not in cell.metadata.get("tags", []):
                        raise ValueError(f"Untagged exercise in {py}:cell{i}")
                if any(o.output_type == "error" for o in cell.get("outputs", [])):
                    raise ValueError(f"Saved error output in {py}:cell{i}")
        count += 1
    print(f"Checked {count} notebook pairs, code syntax, exercise tags, and saved outputs.")


def execute():
    check()
    # Fail promptly if a restricted environment cannot start local Jupyter sockets.
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
    # Keep caches and Jupyter runtime files within the project.
    for name, subdir in {"MPLCONFIGDIR": "matplotlib", "IPYTHONDIR": "ipython",
                         "JUPYTER_RUNTIME_DIR": "jupyter"}.items():
        path = ROOT / ".cache" / subdir
        path.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(path)
    os.environ["MPLBACKEND"] = "module://matplotlib_inline.backend_inline"
    for py in sources():
        if py.parent.name == "templates":
            continue
        path = py.with_suffix(".ipynb")
        nb = nbformat.read(path, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        # The current interpreter is authoritative, not a globally installed kernel.
        km = KernelManager(kernel_name="python3")
        km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
        is_lab = py.parent.name in ("labs", "projects")
        client = NotebookClient(deepcopy(nb), km=km, timeout=120, startup_timeout=30,
                                resources={"metadata": {"path": str(path.parent)}},
                                skip_cells_with_tag="exercise" if is_lab else "never-skip")
        mode = "setup and demonstrations" if is_lab else "all cells"
        print(f"Executing {path.relative_to(ROOT)} ({mode})", flush=True)
        result = client.execute(cleanup_kc=True)
        for cell in result.cells:
            if cell.cell_type != "code" or "display(fig)" not in cell.source:
                continue
            if is_lab and "exercise" in cell.metadata.get("tags", []):
                continue
            if not any("image/png" in output.get("data", {}) for output in cell.outputs):
                raise RuntimeError(f"Expected an embedded plot in {path}")
        nbformat.write(result, path)
        print("  passed", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["sync", "check", "execute"])
    parser.add_argument("--from", dest="direction", choices=["py", "ipynb"], default="py")
    args = parser.parse_args()
    if args.command == "sync":
        sync(args.direction)
    elif args.command == "check":
        check()
    else:
        execute()
