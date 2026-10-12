"""Narrow, stateless text format for the existing customer registration flow."""

TEMPLATE = "Masukkan data pelanggan:\n\nNama:\nAlamat:\nKota:\nNo. Telp:\nKet:"
LABELS = {"nama": "name", "alamat": "address", "kota": "city", "no. telp": "phone", "ket": "notes"}

def input_kind(text):
    if type(text) is not str:
        return None
    command = text.strip().casefold()
    if command == "catat pelanggan":
        return "start"
    if command == "batal pelanggan":
        return "cancel"
    if text.partition(" ")[0] in ("catat_pelanggan", "konfirmasi_pelanggan"):
        return "legacy"
    # A known field anywhere also catches malformed replacement forms: they
    # must cancel a pending draft instead of entering generic ingestion.
    if any(line.partition(":")[0].strip().casefold() in LABELS for line in text.splitlines()):
        return "form"
    return None

def parse_form(text):
    if len(text) > 3500:
        raise ValueError("form too large")
    result = {}
    lines = [line for line in text.splitlines() if line.strip()]
    if lines and lines[0].strip().casefold() == "masukkan data pelanggan:":
        lines.pop(0)
    for line in lines:
        label, separator, value = line.partition(":")
        key = LABELS.get(label.strip().casefold())
        if not separator or key is None or key in result:
            raise ValueError("unknown, duplicate or malformed field")
        value = value.strip()
        result[key] = value or None
    if not {"name", "address", "city"} <= result.keys():
        raise ValueError("required form fields missing")
    result.setdefault("notes", None)
    result.setdefault("phone", None)
    return result
