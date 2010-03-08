from PIL import Image
import sys

import rs

def encode(input, output_filename):
    """Encodes the input data with reed-solomon error correction in 223 byte
    blocks, and outputs each block along with 32 parity bytes to a new file by
    the given filename.

    input is a file-like object

    The outputted image will be in png format, and will be 255 by 255 pixels
    with one color channel. Each block of data will be one row, therefore, the
    data can be recovered if no more than 16 pixels per row are altered.
    """

    output = []

    while True:
        block = input.read(223)
        if not block: break
        code = rs.encode(block).rjust(255,"\0")
        output.append(code)
        sys.stderr.write(".")
        if len(output) == 255: break

    sys.stderr.write("\n")

    out = Image.new("L", (255,255))
    out.putdata("".join(output))
    out.save(output_filename)

def decode(input_filename):
    input = Image.open(input_filename)
    data = bytearray(input.getdata())
    del input

    for row in xrange(255):
        rowdata = data[row*255:(row+1)*255]

        decoded = rs.decode(rowdata)
        if not decoded:
            break
        sys.stdout.write(str(decoded))
        sys.stderr.write(".")
    sys.stderr.write("\n")

if __name__ == "__main__":
    if "-d" == sys.argv[1]:
        # decode
        decode(sys.argv[2])

    else:
        # encode
        encode(sys.stdin,sys.argv[1])
