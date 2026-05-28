from PIL import Image, ImageOps, ImageDraw
import numpy as np

IMAGE_IN = "input.JPG"
IMAGE_OUT = "hidden_fourier.png"

MESSAGE = "Flag{ihateyouizaak},Hint{Turing}"
MAGIC = b"FT"

# These must match decoder.py exactly.
Y_OFFSET = 80
X_START_OFFSET = 40
X_STEP = 3

# Higher contrast = more obvious Fourier corruption, easier decoding.
BLEND_ORIGINAL = 0.35
BLEND_PATTERN = 0.65


def bytes_to_bits(data: bytes) -> list[int]:
    bits = []
    for byte in data:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    return bits


def build_payload_bits(message: str) -> list[int]:
    msg = message.encode("utf-8")
    payload = MAGIC + len(msg).to_bytes(2, "big") + msg
    return bytes_to_bits(payload)


def make_fourier_pattern(height: int, width: int, bits: list[int]) -> np.ndarray:
    cy, cx = height // 2, width // 2
    first_x = cx + X_START_OFFSET
    last_x = first_x + (len(bits) - 1) * X_STEP

    if last_x >= width - 2:
        raise ValueError(
            f"Image too narrow. last_x={last_x}, width={width}. "
            "Use a wider image, reduce X_STEP, or shorten the message."
        )

    if cy - Y_OFFSET < 2 or cy + Y_OFFSET >= height - 2:
        raise ValueError(
            f"Image too short. Y_OFFSET={Y_OFFSET}, height={height}. "
            "Use a taller image or reduce Y_OFFSET."
        )

    F = np.zeros((height, width), dtype=np.complex128)

    for i, bit in enumerate(bits):
        x = first_x + i * X_STEP
        y_one = cy - Y_OFFSET
        y_zero = cy + Y_OFFSET

        selected_y = y_one if bit == 1 else y_zero
        mirror_y = (2 * cy - selected_y) % height
        mirror_x = (2 * cx - x) % width

        # Big clean spikes in an otherwise empty frequency canvas.
        F[selected_y, x] = 1.0
        F[mirror_y, mirror_x] = 1.0

    pattern = np.fft.ifft2(np.fft.ifftshift(F)).real
    pattern -= pattern.min()
    max_value = pattern.max()
    if max_value != 0:
        pattern /= max_value
    pattern *= 255.0
    return pattern.astype(np.float32)


def encode_image(img: Image.Image, bits: list[int]) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("L")
    original = np.array(img).astype(np.float32)
    h, w = original.shape

    pattern = make_fourier_pattern(h, w, bits)
    out = (BLEND_ORIGINAL * original) + (BLEND_PATTERN * pattern)
    out = np.clip(out, 0, 255).astype(np.uint8)

    result = Image.fromarray(out)
    draw = ImageDraw.Draw(result)
    draw.text((12, 12), "fourier", fill=255)
    return result


def main():
    bits = build_payload_bits(MESSAGE)
    img = Image.open(IMAGE_IN)
    out = encode_image(img, bits)
    out.save(IMAGE_OUT)

    print(f"Saved: {IMAGE_OUT}")
    print(f"Embedded message: {MESSAGE}")
    print(f"Embedded bits: {len(bits)}")
    print(f"Expected magic bits: {''.join(str(b) for b in bits[:16])}")
    print(f"Expected length bits: {''.join(str(b) for b in bits[16:32])}")
    print("Expected magic: FT")
    print(f"Expected decoded length: {len(MESSAGE.encode('utf-8'))}")


if __name__ == "__main__":
    main()
