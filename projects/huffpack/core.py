"""Format HFP1 : magic, tailles, SHA-256, longueurs de codes, flux de bits."""

from collections import Counter
import hashlib
import heapq
import itertools
import struct

HEADER = struct.Struct(">4sQQ32sH")


def lengths(data):
    counter = itertools.count()
    heap = []
    for byte, frequency in sorted(Counter(data).items()):
        heapq.heappush(heap, (frequency, next(counter), byte))
    if not heap:
        return {}
    while len(heap) > 1:
        a, _, left = heapq.heappop(heap)
        b, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (a + b, next(counter), (left, right)))
    result = {}

    def visit(node, depth):
        if isinstance(node, int):
            result[node] = max(1, depth)
        else:
            visit(node[0], depth + 1)
            visit(node[1], depth + 1)

    visit(heap[0][2], 0)
    return result


def canonical(sizes):
    code = 0
    previous = 0
    result = {}
    for symbol, size in sorted(sizes.items(), key=lambda x: (x[1], x[0])):
        if not 1 <= size <= 255:
            raise ValueError("Longueur invalide")
        code <<= size - previous
        if code >= 1 << size:
            raise ValueError("Code sursouscrit")
        result[symbol] = (code, size)
        code += 1
        previous = size
    return result


def compress(data):
    sizes = lengths(data)
    codes = canonical(sizes)
    output = bytearray()
    bits = 0
    width = 0
    bit_count = 0
    for byte in data:
        code, size = codes[byte]
        bits = (bits << size) | code
        width += size
        bit_count += size
        while width >= 8:
            width -= 8
            output.append((bits >> width) & 255)
            bits &= (1 << width) - 1
    if width:
        output.append(bits << (8 - width))
    table = b"".join(bytes((symbol, size)) for symbol, size in sorted(sizes.items()))
    return (
        HEADER.pack(b"HFP1", len(data), bit_count, hashlib.sha256(data).digest(), len(sizes))
        + table
        + output
    )


def decompress(blob, max_output=10_000_000):
    if len(blob) < HEADER.size:
        raise ValueError("En-tête tronqué")
    magic, expected, count, digest, total = HEADER.unpack_from(blob)
    if magic != b"HFP1" or total > 256 or expected > max_output:
        raise ValueError("Format ou taille interdits")
    offset = HEADER.size + total * 2
    if len(blob) != offset + (count + 7) // 8:
        raise ValueError("Taille du flux incohérente")
    sizes = {}
    for i in range(HEADER.size, offset, 2):
        symbol, size = blob[i : i + 2]
        if symbol in sizes:
            raise ValueError("Symbole dupliqué")
        sizes[symbol] = size
    codes = canonical(sizes)
    inverse = {(code, width): symbol for symbol, (code, width) in codes.items()}
    if (expected == 0) != (total == 0) or (expected > 0 and not count):
        raise ValueError("Table incohérente")
    payload = blob[offset:]
    if count % 8 and payload[-1] & ((1 << (8 - count % 8)) - 1):
        raise ValueError("Padding non nul")
    output = bytearray()
    code = 0
    width = 0
    max_width = max(sizes.values(), default=0)
    for i in range(count):
        code = (code << 1) | ((payload[i // 8] >> (7 - i % 8)) & 1)
        width += 1
        if (code, width) in inverse:
            output.append(inverse[(code, width)])
            code = 0
            width = 0
            if len(output) > expected:
                raise ValueError("Décompression trop longue")
        elif width >= max_width:
            raise ValueError("Code inconnu")
    if width or len(output) != expected or hashlib.sha256(output).digest() != digest:
        raise ValueError("Flux altéré ou incomplet")
    return bytes(output)


def run(request, db=":memory:"):
    data = request["text"].encode("utf-8")
    packed = compress(data)
    unpacked = decompress(packed)
    return {
        "original_bytes": len(data),
        "compressed_bytes": len(packed),
        "round_trip": unpacked == data,
        "sha256": hashlib.sha256(unpacked).hexdigest(),
        "payload_hex": packed.hex(),
        "ratio": round(len(packed) / len(data), 4) if data else None,
    }
