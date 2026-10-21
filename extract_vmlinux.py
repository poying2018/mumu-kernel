"""Extract the uncompressed vmlinux from a bzImage.

The payload of a bzImage is a compressed kernel. The kernel source ships
scripts/extract-vmlinux, which handles the layouts, but it needs the lz4
tool for the LZ4 payloads Android uses, so the extraction is done here with
the same fallback chain the kernel script uses.

Usage: extract_vmlinux.py <bzImage> <output>
"""
import gzip
import lzma
import struct
import subprocess
import sys

MAGICS = [
    (b"\x1f\x8b\x08", "gzip"),
    (b"\xfd7zXZ", "xz"),
    (b"\x28\xb5\x2f\xfd", "zstd"),
    (b"\x02!L\x18", "lz4-legacy"),
]


def main(img_path, out_path):
    data = open(img_path, "rb").read()

    # the payload starts after the setup code, at the offset the header gives
    setup_sects = data[0x1F1]
    setup_end = (setup_sects + 1) * 512
    payload_offset = struct.unpack_from("<I", data, 0x248)[0]
    candidates = [payload_offset, setup_end + payload_offset, setup_end]

    for base in candidates:
        if base >= len(data):
            continue
        for magic, kind in MAGICS:
            idx = data.find(magic, base, base + 0x100000)
            if idx < 0:
                continue
            blob = data[idx:]
            try:
                if kind == "gzip":
                    out = gzip.decompress(blob)
                elif kind == "xz":
                    out = lzma.decompress(blob)
                elif kind == "zstd":
                    p = subprocess.run(["zstd", "-d", "-c"], input=blob,
                                       capture_output=True)
                    out = p.stdout
                else:
                    # Linux LZ4 payloads are a legacy frame: the whole
                    # remainder is one compressed block.
                    p = subprocess.run(["lz4", "-d", "-c"], input=blob,
                                       capture_output=True)
                    out = p.stdout
            except Exception:
                continue
            if len(out) < 1024:
                continue
            open(out_path, "wb").write(out)
            print("extracted %s at 0x%x: %d bytes, ELF=%s"
                  % (kind, idx, len(out), out[:4] == b"\x7fELF"))
            return 0

    print("no supported compression found")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
