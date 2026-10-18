"""Crop a PNG with nothing but the standard library.

Design review needs a true 390px-wide mobile capture, and this machine has no
image library installed. Rather than add a dependency for a review-time task,
this decodes the PNG by hand, keeps the columns we want, and writes it back.

    python tools/crop_png.py in.png out.png --width 390
    python tools/crop_png.py in.png out.png --width 390 --height 2400
"""

from __future__ import annotations

import argparse
import struct
import zlib


def _chunks(data: bytes):
    position = 8  # skip the signature
    while position < len(data):
        (length,) = struct.unpack(">I", data[position : position + 4])
        kind = data[position + 4 : position + 8]
        body = data[position + 8 : position + 8 + length]
        yield kind, body
        position += 12 + length


def read_png(path: str) -> tuple[int, int, int, int, bytes]:
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")

    width = height = depth = colour = 0
    compressed = b""
    for kind, body in _chunks(data):
        if kind == b"IHDR":
            width, height, depth, colour, _comp, _filter, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or colour not in (2, 6) or interlace:
                raise ValueError("only 8-bit RGB/RGBA non-interlaced PNGs are handled here")
        elif kind == b"IDAT":
            compressed += body
        elif kind == b"IEND":
            break
    return width, height, depth, colour, zlib.decompress(compressed)


def unfilter(raw: bytes, width: int, height: int, bpp: int) -> list[bytearray]:
    stride = width * bpp
    rows: list[bytearray] = []
    previous = bytearray(stride)
    position = 0
    for _ in range(height):
        filter_type = raw[position]
        position += 1
        line = bytearray(raw[position : position + stride])
        position += stride
        if filter_type == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif filter_type == 2:
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 0xFF
        elif filter_type == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif filter_type == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = previous[i]
                c = previous[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                predictor = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + predictor) & 0xFF
        elif filter_type != 0:
            raise ValueError(f"unknown filter type {filter_type}")
        rows.append(line)
        previous = line
    return rows


def write_png(path: str, rows: list[bytearray], colour: int) -> None:
    height = len(rows)
    width = len(rows[0]) // (3 if colour == 2 else 4)
    body = b"".join(b"\x00" + bytes(row) for row in rows)  # filter 0 per row
    header = struct.pack(">IIBBBBB", width, height, 8, colour, 0, 0, 0)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(chunk(b"IHDR", header))
        handle.write(chunk(b"IDAT", zlib.compress(body, 9)))
        handle.write(chunk(b"IEND", b""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Crop a PNG using only the standard library.")
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("--width", type=int, required=True, help="columns to keep, from the left")
    parser.add_argument("--height", type=int, default=0, help="rows to keep, from the top (0 = all)")
    args = parser.parse_args()

    width, height, _depth, colour, raw = read_png(args.source)
    bpp = 3 if colour == 2 else 4
    rows = unfilter(raw, width, height, bpp)

    keep_w = min(args.width, width)
    keep_h = min(args.height, height) if args.height else height
    cropped = [bytearray(row[: keep_w * bpp]) for row in rows[:keep_h]]
    write_png(args.target, cropped, colour)
    print(f"{args.source} {width}x{height} -> {args.target} {keep_w}x{keep_h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
