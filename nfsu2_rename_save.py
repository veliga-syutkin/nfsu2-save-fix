#!/usr/bin/env python3
"""Rename the profile inside an NFS Underground 2 PC save so nfsu2.xyz accepts it.

nfsu2.xyz refuses saves whose internal name is not 1-7 ASCII letters/digits:

    <name> cannot be restored: the name inside, "...", is not one the game makes
    (1 to 7 letters and digits).

This happens with saves made by third-party tools (e.g. underscores in the name)
and with saves from other-language releases (non-ASCII bytes in the name). The name is stored
inside the file and covered by checksums, so renaming the file is not enough.
This script rewrites the name and recomputes the checksums.

Usage:
  python3 nfsu2_rename_save.py check  SAVEFILE
  python3 nfsu2_rename_save.py rename SAVEFILE NEWNAME [-o OUTDIR]

`rename` never touches SAVEFILE: it writes OUTDIR/NEWNAME/NEWNAME (default OUTDIR
is the current directory). Import that folder/file on nfsu2.xyz.

Format (as read from the nfsu2.xyz client code): 54966 bytes, magic "20CM",
36-byte header, name at offset 53797 (32 bytes, NUL-terminated), three
little-endian CRC32/MPEG-2 values at offsets 16, 20 and 24. Python 3, stdlib only.
"""
import argparse
import os
import re
import struct
import sys

SIZE = 54966
MAGIC = b"20CM"
HDR = 36
NAME_OFF = HDR + 53761
NAME_LEN = 32
MAX_NAME = 7

TABLE = []
for _n in range(256):
    _e = (_n << 24) & 0xFFFFFFFF
    for _ in range(8):
        _e = ((_e << 1) & 0xFFFFFFFF) ^ 0x04C11DB7 if _e & 0x80000000 else (_e << 1) & 0xFFFFFFFF
    TABLE.append(_e)


def crc(b):
    if len(b) < 4:
        return 0
    e = ~(b[0] << 24 | b[1] << 16 | b[2] << 8 | b[3]) & 0xFFFFFFFF
    for t in range(4, len(b)):
        e = ((((e << 8) & 0xFFFFFFFF) | b[t]) ^ TABLE[e >> 24]) & 0xFFFFFFFF
    return ~e & 0xFFFFFFFF


def valid_name(name):
    return re.fullmatch(r"[A-Za-z0-9]{1,%d}" % MAX_NAME, name) is not None


def load(path):
    with open(path, "rb") as f:
        b = f.read()
    if len(b) != SIZE or b[:4] != MAGIC:
        sys.exit(f"{path}: not an NFSU2 PC profile (expected {SIZE} bytes starting with {MAGIC!r}, "
                 f"got {len(b)} bytes starting with {b[:4]!r})")
    return b


def raw_name(b):
    field = b[NAME_OFF:NAME_OFF + NAME_LEN]
    return field.split(b"\0", 1)[0]


def stored_and_computed(b):
    spans = {16: b[28:HDR], 20: b[HDR:], 24: b[0:24]}
    return {off: (struct.unpack_from("<I", b, off)[0], crc(bytes(data))) for off, data in spans.items()}


def cmd_check(args):
    b = load(args.save)
    name = raw_name(b)
    text = name.decode("ascii", "backslashreplace")  # stays printable on any console encoding
    print(f"name inside the file: {text!r} (bytes {name.hex()})")
    print("  accepted by nfsu2.xyz" if valid_name(text)
          else f"  REJECTED by nfsu2.xyz (needs 1-{MAX_NAME} ASCII letters/digits)")
    for off, (stored, calc) in stored_and_computed(b).items():
        print(f"  checksum @{off}: stored {stored:08x} / computed {calc:08x} -> "
              f"{'OK' if stored == calc else 'MISMATCH'}")


def cmd_rename(args):
    if not valid_name(args.newname):
        sys.exit(f"invalid name {args.newname!r}: use 1-{MAX_NAME} ASCII letters/digits")
    b = bytearray(load(args.save))
    b[NAME_OFF:NAME_OFF + NAME_LEN] = args.newname.encode("ascii").ljust(NAME_LEN, b"\0")
    struct.pack_into("<I", b, 16, crc(bytes(b[28:HDR])))
    struct.pack_into("<I", b, 20, crc(bytes(b[HDR:])))
    struct.pack_into("<I", b, 24, crc(bytes(b[0:24])))
    folder = os.path.join(args.outdir, args.newname)
    out = os.path.join(folder, args.newname)
    if os.path.exists(out):
        sys.exit(f"{out} already exists, not overwriting")
    os.makedirs(folder)
    with open(out, "wb") as f:
        f.write(b)
    print(f"written: {out}")
    print("import this on nfsu2.xyz (the original file was not modified)")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="show the name inside a save and verify its checksums")
    c.add_argument("save")
    c.set_defaults(fn=cmd_check)
    r = sub.add_parser("rename", help="write a copy of the save with a new internal name")
    r.add_argument("save")
    r.add_argument("newname", help=f"1-{MAX_NAME} ASCII letters/digits")
    r.add_argument("-o", "--outdir", default=".", help="where to create NEWNAME/NEWNAME (default: .)")
    r.set_defaults(fn=cmd_rename)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
