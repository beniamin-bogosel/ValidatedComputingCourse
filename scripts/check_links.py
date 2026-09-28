"""Check local links in course Markdown, notebooks, and generated reading copies."""

import argparse
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt
import nbformat


ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ("notebooks", "labs", "projects", "assignments", "solutions", "templates", "Doc")


def markdown_links(source):
    parser = MarkdownIt()
    for block in parser.parse(source):
        for token in block.children or []:
            if token.type == "link_open":
                yield token.attrGet("href")
            elif token.type == "image":
                yield token.attrGet("src")


def links_in(path):
    if path.suffix == ".ipynb":
        notebook = nbformat.read(path, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                yield from markdown_links(cell.source)
    elif path.suffix == ".md":
        yield from markdown_links(path.read_text())
    elif path.suffix == ".html":
        soup = BeautifulSoup(path.read_text(), "html.parser")
        for tag in soup.find_all(href=True):
            yield tag["href"]
        for tag in soup.find_all(src=True):
            yield tag["src"]


def course_documents(root):
    paths = list(root.glob("*.md"))
    for folder in FOLDERS:
        paths.extend((root / folder).glob("*.md"))
        paths.extend((root / folder).glob("*.ipynb"))
    paths.extend((root / "reading").rglob("*.html"))
    return sorted(paths)


def check(root=ROOT):
    root = Path(root).resolve()
    count = 0
    errors = []
    for path in course_documents(root):
        for link in links_in(path):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            count += 1
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(root):
                errors.append(f"{path.relative_to(root)}: link escapes the course: {link}")
            elif not target.exists():
                errors.append(f"{path.relative_to(root)}: missing {link}")
    if errors:
        raise ValueError("\n".join(errors))
    print(f"Checked {count} local links in {root}")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    check(parser.parse_args().root)
