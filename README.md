# fourrier-stego

A small steganography challenge that hides a payload (utf8) in the frequency domain of an image. Built for a CTF.

The encoder (main.py) writes a Fourier-domain pattern into `hidden_fourier.png`. The decoder (decode.py) validates the stego and shows the intended recovery path.

## Quick Run

Place your local source image at `input.JPG`, then run the generator to create `hidden_fourier.png`.
