"""Pure projection of one text value into semantic data."""

MAX_SEMANTIC_TEXT_CHARACTERS = 4_096
MAX_SEMANTIC_TEXT_UTF8_BYTES = 16_384


def project_text_semantics(text: str) -> dict[str, object]:
    """Return the exact bounded v1 semantic mapping for one text value."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized_text:
        raise ValueError("text must not be empty after normalization")
    if len(normalized_text) > MAX_SEMANTIC_TEXT_CHARACTERS:
        raise ValueError(
            f"text exceeds {MAX_SEMANTIC_TEXT_CHARACTERS} Unicode code points"
        )
    if len(normalized_text.encode("utf-8")) > MAX_SEMANTIC_TEXT_UTF8_BYTES:
        raise ValueError(
            f"text exceeds {MAX_SEMANTIC_TEXT_UTF8_BYTES} UTF-8 bytes"
        )
    if any(
        (ord(character) < 32 and character not in ("\t", "\n"))
        or ord(character) == 127
        for character in normalized_text
    ):
        raise ValueError("text contains a forbidden ASCII control character")

    return {"text": normalized_text}
