# rlp-encoder

A tiny, dependency-free implementation of **Recursive Length Prefix (RLP)**
encoding/decoding in pure Python — the serialization format Ethereum uses for
transactions, blocks, and state.

## Rules in a nutshell

RLP only knows two types: byte strings and (nested) lists.

| Input | Encoding |
|---|---|
| Single byte `< 0x80` | The byte itself |
| String of length 0–55 | `0x80 + len` followed by the string |
| String longer than 55 | `0xb7 + len(len)` + length + string |
| List with short payload | `0xc0 + len` followed by concatenated items |
| List with long payload | `0xf7 + len(len)` + length + items |

Integers are encoded big-endian with no leading zeros (`0` = empty string).

## Usage

```python
from rlp import encode, decode

encode(b"dog")                    # b'\x83dog'
encode([b"dog", b"god", b"cat"])  # b'\xcc\x83dog\x83god\x83cat'

decode(bytes.fromhex("c7c0c1c0c3c0c1c0"))  # [[], [[]], [[], [[]]]]
```

## Run the demo

```bash
python3 demo.py   # verifies the official Ethereum RLP test vectors
```

Zero dependencies, ~80 lines. Educational toy — not for production use.
