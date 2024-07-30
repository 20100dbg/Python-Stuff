
def nonrepeatxor(text, key):
    sk = len(key)
    res = ''

    for i in range(0, 2 * sk, 2):
        x = int(text[i:i + 2], 16)
        y = ord(key[i // 2])

        if (x ^ y > 31):
            #print(chr(x ^ y), end='')
            res += chr(x ^ y)
        else:
            #print('\\x%x' % (x ^ y), end='')
            res += '\\x%x' % (x ^ y)

    return res


def xor_hex(hex1, hex2):
    hex1 = bytes.fromhex(hex1)
    hex2 = bytes.fromhex(hex2)

    return ''.join([chr(x ^ y) for x,y in zip(hex1,hex2)])


c1 = '213c234c2322282057730b32492e720b35732b2124553d354c22352224237f1826283d7b0651'
c2 = '3b3b463829225b3632630b542623767f39674431343b353435412223243b7f162028397a103e'


cribs = ['utflag{', 'CATEGORY']

#res = nonrepeatxor(c1, crib)
#print(res)

for i in range(10):
    x = xor_hex(c1,c2)
    c =  ' ' * i + 'CATEGORY'
    print(xor_hex(x.encode().hex(), c.encode().hex()))

