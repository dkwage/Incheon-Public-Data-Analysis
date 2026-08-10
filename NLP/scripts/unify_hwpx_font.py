#!/usr/bin/env python3
"""Preserve an HWPX body exactly while making every registered font Malgun Gothic."""
from pathlib import Path
import re
import sys
import zipfile

if len(sys.argv) != 3:
    raise SystemExit('usage: unify_hwpx_font.py INPUT.hwpX OUTPUT.hwpx')

source, output = map(Path, sys.argv[1:])
with zipfile.ZipFile(source, 'r') as src, zipfile.ZipFile(output, 'w') as dst:
    for info in src.infolist():
        data = src.read(info.filename)
        if info.filename == 'Contents/header.xml':
            data = re.sub(rb'(<hh:font\b[^>]*\bface=")[^"]*(")', lambda m: m.group(1) + '맑은 고딕'.encode() + m.group(2), data)
        # Keep the HWPX-required mimetype entry uncompressed; retain all other entry settings.
        clone = zipfile.ZipInfo(info.filename, info.date_time)
        clone.compress_type = zipfile.ZIP_STORED if info.filename == 'mimetype' else info.compress_type
        clone.external_attr = info.external_attr
        clone.comment = info.comment
        dst.writestr(clone, data)
