"""Demo + self-test: encodes/decodes Ethereum RLP test vectors."""

from rlp import encode, decode

VECTORS = [
    (b"", "80"),
    (b"\x00", "00"),
    (b"\x0f", "0f"),
    (bytes.fromhex("0400"), "820400"),
    (b"dog", "83646f67"),
    ([b"dog", b"god", b"cat"], "cc83646f6783676f6483636174"),
    ([[], [[]], [[], [[]]]], "c7c0c1c0c3c0c1c0"),
]

LONG = b"Lorem ipsum dolor sit amet, consectetur adipisicing elit"
assert len(LONG) == 56  # forces the long-string form (>55 bytes)

for item, expected_hex in VECTORS:
    enc = encode(item).hex()
    assert enc == expected_hex, (item, enc, expected_hex)
    assert decode(bytes.fromhex(enc)) == item
    print(f"ok  {enc}")

# long-string roundtrip
enc_long = encode(LONG)
assert enc_long[:2] == b"\xb8\x38"  # 0xb7+1, then length 56
assert decode(enc_long) == LONG
print(f"ok  long string ({len(LONG)} bytes) -> {enc_long[:8].hex()}...")

# integers the RLP way (big-endian, no leading zeros)
n = 1024
enc_int = encode(n.to_bytes((n.bit_length() + 7) // 8, "big"))
assert enc_int.hex() == "820400"
print("ok  integer 1024 -> 820400")

print("\nAll RLP vectors passed.")
