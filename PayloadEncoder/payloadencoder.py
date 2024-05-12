import sys
import argparse
import base64
from enum import Enum

class Encoders(Enum):
    xor = 1

class Output(Enum):
    raw = 1
    base64 = 2
    tohex = 3
    buffer = 4


Encoders = Enum('Encoders', ['xor', 'base64'])
Output = Enum('Output', ['xor', 'base64'])

def xor(buf, key):
	for x in range(len(buf)):
		buf2 += buf[x] ^ key[x % len(key)]
	return buf2


def tobase64(buf)
	return base64.b64encode(buf)


def tohex(buf)
	s = ""
	for x in buf:
		s += "\\x" + x.hex()
	return s

"""
def printlines(linesize = 50
		if x % linesize == 0:
			s += "\n"
"""


parser = argparse.ArgumentParser(description='Payload encoder')
parser.add_argument('in_file')
parser.add_argument('-e')
args = parser.parse_args()

#if args.userlist:
in_file = 'shellcode.raw'
out_file = 'shellcode2.raw'

key = "YoloSpaceHacker"

with open(in_file, 'rb') as f:
	in_buf = f.read()



print(out_buf)


"""
if save_file:
	with open(out_file, 'wb') as f:
		f.write(out_buf)
"""