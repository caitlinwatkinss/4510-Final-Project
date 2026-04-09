#!/usr/bin/env python3
"""Extracts hidden OCR text from PDF streams that use UTF-16BE hex TJ commands."""
import re
import zlib
from pathlib import Path
import sys


def extract_pdf_text(path: Path):
    data = path.read_bytes()
    for match in re.finditer(rb"(\d+)\s+(\d+)\s+obj(.*?)endobj", data, re.S):
        obj_no = int(match.group(1))
        body = match.group(3)
        if b"stream" not in body or b"/FlateDecode" not in body:
            continue
        stream = body.split(b"stream", 1)[1].split(b"endstream", 1)[0].lstrip(b"\r\n").rstrip(b"\r\n")
        try:
            decoded = zlib.decompress(stream)
        except Exception:
            continue
        if b"BT" not in decoded:
            continue

        bt_blocks = re.findall(rb"BT(.*?)ET", decoded, re.S)
        lines = []
        for block in bt_blocks:
            hex_strings = re.findall(rb"<([0-9A-Fa-f]+)>", block)
            parts = []
            for h in hex_strings:
                if len(h) % 4:
                    continue
                try:
                    text = bytes.fromhex(h.decode()).decode("utf-16-be")
                except Exception:
                    continue
                parts.append(text)
            line = "".join(parts).strip()
            if line:
                lines.append(line)

        if lines:
            yield obj_no, lines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: extract_ocr_text.py <pdf>")
        raise SystemExit(1)
    pdf = Path(sys.argv[1])
    for obj, lines in extract_pdf_text(pdf):
        print(f"\n=== Object {obj} ===")
        for i, line in enumerate(lines, start=1):
            print(f"{i:02d}: {line}")
