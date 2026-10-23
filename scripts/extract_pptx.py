"""Extract slide text from a PPTX deck into Markdown (stdlib only)."""
from __future__ import annotations

import argparse
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
A_P = f"{{{A_NS}}}p"
A_T = f"{{{A_NS}}}t"


def _slide_number(name: str) -> int:
    return int(re.search(r"(\d+)\.xml$", name).group(1))


def _slide_lines(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    lines: list[str] = []
    for paragraph in root.iter(A_P):
        text = "".join(node.text or "" for node in paragraph.iter(A_T)).strip()
        if text:
            lines.append(text)
    return lines


def extract_slides(pptx_path: str | Path) -> list[tuple[int, list[str]]]:
    slides: list[tuple[int, list[str]]] = []
    with zipfile.ZipFile(pptx_path) as archive:
        names = [
            name
            for name in archive.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        ]
        for name in sorted(names, key=_slide_number):
            slides.append((_slide_number(name), _slide_lines(archive.read(name))))
    return slides


def to_markdown(slides: list[tuple[int, list[str]]]) -> str:
    chunks: list[str] = []
    for number, lines in slides:
        body = "\n".join(f"- {line}" for line in lines) or "- (no text on slide)"
        chunks.append(f"## Slide {number}\n\n{body}")
    return "\n\n".join(chunks) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PPTX slide text to Markdown.")
    parser.add_argument("pptx", help="Path to the .pptx file")
    parser.add_argument("-o", "--output", help="Output .md path (default: stdout)")
    args = parser.parse_args()

    slides = extract_slides(args.pptx)
    markdown = to_markdown(slides)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {len(slides)} slides to {output}")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
