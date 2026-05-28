from PIL import Image, ImageOps
import numpy as np

IMAGE_IN = "hidden_fourier.png"

MAGIC = b"FT"
Y_OFFSET = 80
X_START_OFFSET = 40
X_STEP = 3
MAX_BITS = 4096


def bits_to_bytes(bits: list[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        if len(chunk) < 8:
            break

        byte = 0
        for bit in chunk:
            byte = (byte << 1) | bit
        out.append(byte)

    return bytes(out)


def bytes_to_bits(data: bytes) -> list[int]:
    bits = []
    for byte in data:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    return bits


def extract_bits(img, max_bits=MAX_BITS) -> list[int]:
    img = ImageOps.exif_transpose(img).convert("L")
    arr = np.array(img).astype(np.float32)

    h, w = arr.shape
    cy, cx = h // 2, w // 2

    F = np.fft.fftshift(np.fft.fft2(arr))
    mag = np.abs(F)

    first_x = cx + X_START_OFFSET
    bits = []

    for i in range(max_bits):
        x = first_x + i * X_STEP
        if x >= w - 2:
            break

        y_one = cy - Y_OFFSET
        y_zero = cy + Y_OFFSET

        one_strength = mag[y_one, x]
        zero_strength = mag[y_zero, x]

        bits.append(1 if one_strength > zero_strength else 0)

    return bits


def find_magic_offset(bits: list[int]) -> int:
    magic_bits = bytes_to_bits(MAGIC)
    limit = min(256, max(0, len(bits) - 32))

    for offset in range(limit):
        if bits[offset:offset + 16] == magic_bits:
            return offset

    return -1


def decode_message(bits: list[int]) -> str:
    offset = find_magic_offset(bits)
    if offset < 0:
        first_64 = ''.join(str(b) for b in bits[:64])
        raise ValueError(
            "Bad magic. Could not find b'FT' in the first 256 decoded bit positions. "
            f"First 64 bits were: {first_64}"
        )

    magic_bits = bits[offset:offset + 16]
    length_bits = bits[offset + 16:offset + 32]

    magic = bits_to_bytes(magic_bits)
    length = int.from_bytes(bits_to_bytes(length_bits), "big")

    print(f"Magic offset: {offset}")
    print(f"Magic bits: {''.join(str(b) for b in magic_bits)}")
    print(f"Magic bytes: {magic!r}")
    print(f"Length bits: {''.join(str(b) for b in length_bits)}")
    print(f"Decoded length: {length}")

    if magic != MAGIC:
        first_64 = ''.join(str(b) for b in bits[:64])
        raise ValueError(
            "Bad magic. Expected b'FT'. "
            f"First 64 decoded bits were: {first_64}"
        )

    if length <= 0 or length > 1000:
        raise ValueError(f"Bad decoded length: {length}.")

    start = offset + 32
    end = start + length * 8
    if len(bits) < end:
        raise ValueError(f"Not enough bits. Need {end}, extracted {len(bits)}.")

    message_bits = bits[start:end]
    return bits_to_bytes(message_bits).decode("utf-8", errors="replace")


def main():
    img = Image.open(IMAGE_IN)
    bits = extract_bits(img)
    message = decode_message(bits)
    print(message)


if __name__ == "__main__":
    main()