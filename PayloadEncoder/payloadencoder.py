import argparse
import base64
import sys

def xor(buf, key):
	buf2 = b''

	for x in range(len(buf)):
		buf2 += (buf[x] ^ key[x % len(key)]).to_bytes(1, 'big')
	return buf2


def tobase64(buf):
	return base64.b64encode(buf).decode()


def tohex(buf):
	s = ""
	for x in buf:
		s += "\\x" + int_to_bytes(x).hex()
	return s

def toraw(buf):
	b = b""
	for x in out_buf:
		b += x.to_bytes(1, 'big')

	return b

def int_to_bytes(x):
	return x.to_bytes(1, 'big')


parser = argparse.ArgumentParser(description='Payload encoder')
parser.add_argument('-i', '--input', required=True, help='')
parser.add_argument('-o', '--output', help='')
parser.add_argument('-f', '--format', help='b64, hex, raw')
parser.add_argument('-e', '--encrypt', help='xor')
parser.add_argument('-p', '--password', help='')
args = parser.parse_args()


with open(args.input, 'rb') as f:
	in_buf = f.read()

out_buf = in_buf

if args.encrypt and args.password:

	if args.encrypt == 'xor':
		out_buf = xor(in_buf, args.password.encode())

if args.format == 'b64':
	out_buf = tobase64(out_buf)
elif args.format == 'hex':
	out_buf = tohex(out_buf)
else:
	out_buf = toraw(out_buf)

if args.output:
	with open(args.output, 'wb') as f:
		f.write(out_buf)
else:
	print(out_buf)

