# fourrier-stego

A small steganography challenge that hides a payload (utf8) in the frequency domain of an image. But for a CTF.

The encoder writes a Fourier-domain pattern into `hidden_fourier.png`. The decoder shows the intended recovery path: transform the image, compare paired frequency spikes, rebuild bytes, check the `FT` magic marker, read a 2-byte big-endian length, and decode the message.

## Files

- `main.py` builds the challenge image.
- `decoder.py` demonstrates the solve path.
- Image files are intentionally not committed.

Place your local source image at `input.JPG`, then run the generator to create `hidden_fourier.png`.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate

```sh
python main.py
```

## Decode

```sh
python decoder.py
```
