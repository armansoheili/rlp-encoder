"""Minimal pure-Python implementation of Recursive Length Prefix (RLP) encoding,
the serialization format used by Ethereum.

Reference: https://ethereum.org/en/developers/docs/data-structures-and-encoding/rlp/
"""

__all__ = ["encode", "decode", "DecodingError"]


class DecodingError(ValueError):
    pass


def _encode_length(length: int, offset: int) -> bytes:
    if length <= 55:
        return bytes([offset + length])
    blen = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes([offset + 55 + len(blen)]) + blen


def encode(item) -> bytes:
    """Encode a bytes object or a (nested) list of bytes objects."""
    if isinstance(item, bytes):
        if len(item) == 1 and item[0] < 0x80:
            return item
        return _encode_length(len(item), 0x80) + item
    if isinstance(item, list):
        payload = b"".join(encode(x) for x in item)
        return _encode_length(len(payload), 0xC0) + payload
    raise TypeError(f"RLP can only encode bytes or lists, got {type(item).__name__}")


def _consume_length(data: bytes, pos: int):
    """Return (data_len, next_pos) parsed from the prefix at pos."""
    if pos >= len(data):
        raise DecodingError("unexpected end of input")
    first = data[pos]
    if first < 0x80:
        return 0, pos  # single byte, handled by caller
    if first <= 0xB7:
        return first - 0x80, pos + 1
    if first <= 0xBF:
        llen = first - 0xB7
        return int.from_bytes(data[pos + 1: pos + 1 + llen], "big"), pos + 1 + llen
    if first <= 0xF7:
        return first - 0xC0, pos + 1
    llen = first - 0xF7
    return int.from_bytes(data[pos + 1: pos + 1 + llen], "big"), pos + 1 + llen


def _decode_item(data: bytes, pos: int):
    first = data[pos]
    if first < 0x80:
        return bytes([first]), pos + 1
    if first < 0xC0:
        length, pos = _consume_length(data, pos)
        return data[pos: pos + length], pos + length
    length, pos = _consume_length(data, pos)
    end = pos + length
    items = []
    while pos < end:
        item, pos = _decode_item(data, pos)
        items.append(item)
    if pos != end:
        raise DecodingError("list length mismatch")
    return items, pos


def decode(data: bytes):
    """Decode RLP bytes into a bytes object or nested list. Trailing garbage rejected."""
    if not data:
        raise DecodingError("cannot decode empty input")
    item, pos = _decode_item(data, 0)
    if pos != len(data):
        raise DecodingError("trailing bytes after RLP item")
    return item
