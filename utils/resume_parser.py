from __future__ import annotations

from io import BytesIO
import base64
import re
import zlib


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from an uploaded PDF with optional libraries and a stdlib fallback."""
    raw = uploaded_file.getvalue()
    text_chunks: list[str] = []

    try:
        import pdfplumber

        with pdfplumber.open(BytesIO(raw)) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
    except Exception:
        text_chunks = []

    text = "\n".join(chunk for chunk in text_chunks if chunk.strip())
    if text.strip():
        return text

    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text
    except Exception:
        pass

    text = _extract_text_without_pdf_library(raw)
    if text.strip():
        return text

    raise ValueError("Could not extract readable text from this PDF.")


def _extract_text_without_pdf_library(raw: bytes) -> str:
    """Best-effort PDF text extraction for environments without PDF packages."""
    candidates: list[str] = []
    decoded_payloads: list[bytes] = []

    for stream in re.findall(rb"stream\r?\n(.*?)\r?\n?endstream", raw, flags=re.S):
        decoded_streams = [_try_decompress(stream), _try_ascii85_then_decompress(stream)]
        if not any(decoded_streams):
            decoded_streams.append(stream)
        for payload in decoded_streams:
            if not payload:
                continue
            decoded_payloads.append(payload)

    cmap = _build_unicode_cmap(decoded_payloads)
    for payload in decoded_payloads:
        candidates.extend(_extract_pdf_text_tokens(payload, cmap))

    if not candidates:
        candidates.extend(_extract_pdf_text_tokens(raw, cmap))

    cleaned = " ".join(candidates)
    cleaned = re.sub(r"\\[nrtbf()]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _try_decompress(data: bytes) -> bytes:
    try:
        return zlib.decompress(data.strip())
    except Exception:
        return b""


def _try_ascii85_then_decompress(data: bytes) -> bytes:
    cleaned = data.strip()
    if cleaned.endswith(b"~>") and not cleaned.startswith(b"<~"):
        cleaned_for_plain_decode = cleaned[:-2]
    else:
        cleaned_for_plain_decode = cleaned
    try:
        decoded = base64.a85decode(cleaned_for_plain_decode, adobe=cleaned.startswith(b"<~"))
    except Exception:
        try:
            wrapped = cleaned if cleaned.startswith(b"<~") else b"<~" + cleaned
            decoded = base64.a85decode(wrapped if wrapped.endswith(b"~>") else wrapped + b"~>", adobe=True)
        except Exception:
            return b""
    return _try_decompress(decoded) or decoded


def _extract_pdf_text_tokens(data: bytes, cmap: dict[str, str] | None = None) -> list[str]:
    decoded = data.decode("latin-1", errors="ignore")
    tokens: list[str] = []

    tokens.extend(re.findall(r"\(([^()]{2,220})\)", decoded))

    for match in re.findall(r"<([0-9A-Fa-f]{4,})>", decoded):
        try:
            text = _decode_hex_text(match, cmap or {})
            if text.strip():
                tokens.append(text)
        except Exception:
            continue

    readable = re.findall(r"[A-Za-z][A-Za-z0-9+#./&@ -]{2,}", decoded)
    tokens.extend(item for item in readable if not item.startswith(("obj", "endobj", "xref")))
    return tokens


def _build_unicode_cmap(payloads: list[bytes]) -> dict[str, str]:
    cmap: dict[str, str] = {}
    for payload in payloads:
        text = payload.decode("latin-1", errors="ignore")
        for block in re.findall(r"beginbfchar(.*?)endbfchar", text, flags=re.S):
            for source, target in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
                decoded = _decode_unicode_hex(target)
                if decoded:
                    cmap[source.upper()] = decoded

        for block in re.findall(r"beginbfrange(.*?)endbfrange", text, flags=re.S):
            for start, end, target in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
                start_int = int(start, 16)
                end_int = int(end, 16)
                target_int = int(target, 16)
                width = len(start)
                for code in range(start_int, min(end_int, start_int + 300) + 1):
                    unicode_hex = f"{target_int + (code - start_int):04X}"
                    decoded = _decode_unicode_hex(unicode_hex)
                    if decoded:
                        cmap[f"{code:0{width}X}"] = decoded

            for start, end, array_values in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*?)\]", block, flags=re.S):
                start_int = int(start, 16)
                width = len(start)
                values = re.findall(r"<([0-9A-Fa-f]+)>", array_values)
                for offset, value in enumerate(values):
                    decoded = _decode_unicode_hex(value)
                    if decoded:
                        cmap[f"{start_int + offset:0{width}X}"] = decoded
    return cmap


def _decode_hex_text(hex_value: str, cmap: dict[str, str]) -> str:
    hex_value = re.sub(r"[^0-9A-Fa-f]", "", hex_value).upper()
    if not hex_value:
        return ""
    if cmap:
        sizes = sorted({len(key) for key in cmap}, reverse=True)
        output: list[str] = []
        index = 0
        while index < len(hex_value):
            matched = False
            for size in sizes:
                piece = hex_value[index : index + size]
                if piece in cmap:
                    output.append(cmap[piece])
                    index += size
                    matched = True
                    break
            if not matched:
                index += 2
        mapped = "".join(output).strip()
        if mapped:
            return mapped

    raw = bytes.fromhex(hex_value)
    for encoding in ("utf-16-be", "latin-1"):
        text = raw.decode(encoding, errors="ignore").strip()
        if text and _looks_like_resume_text(text):
            return text
    return raw.decode("latin-1", errors="ignore")


def _decode_unicode_hex(value: str) -> str:
    try:
        raw = bytes.fromhex(value)
    except ValueError:
        return ""
    if len(raw) >= 2:
        text = raw.decode("utf-16-be", errors="ignore").strip("\x00")
        if text:
            return text
    return raw.decode("latin-1", errors="ignore").strip()


def _looks_like_resume_text(text: str) -> bool:
    letters = sum(character.isalpha() for character in text)
    return letters >= max(2, len(text) * 0.35)
