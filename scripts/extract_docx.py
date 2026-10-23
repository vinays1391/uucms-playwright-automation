"""Extract DOCX body text into Markdown (stdlib only)."""
from __future__ import annotations

import argparse
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W_P = f"{{{W_NS}}}p"
W_T = f"{{{W_NS}}}t"


def _paragraph_lines(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    lines: list[str] = []
    for paragraph in root.iter(W_P):
        text = "".join(node.text or "" for node in paragraph.iter(W_T)).strip()
        if text:
            lines.append(text)
    return lines


def extract_paragraphs(docx_path: str | Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as archive:
        xml_bytes = archive.read("word/document.xml")
    return _paragraph_lines(xml_bytes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract DOCX body text to Markdown.")
    parser.add_argument("docx", help="Path to the .docx file")
    parser.add_argument("-o", "--output", help="Output .md path (default: stdout)")
    args = parser.parse_args()

    lines = extract_paragraphs(args.docx)
    markdown = "\n".join(f"- {line}" for line in lines) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {len(lines)} paragraphs to {output}")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
