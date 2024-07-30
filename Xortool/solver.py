import string
import base64


def GetAsciiRatio(mystring):
    charset = string.ascii_letters + string.digits + " "
    ratio = sum([x in charset for x in mystring]) / len(mystring)
    return ratio


def isAscii(mystring, min_ratio):
    ratio = GetAsciiRatio(mystring)
    return (ratio > min_ratio)


def hamming(str1, str2):

    #si les deux chaines sont de tailles différentes, il faut adapter la boucle
    #et ajouter le nombre de bits en trop à la distance

    #version bytes
    str1 = ''.join(format(x, '08b') for x in str1)
    str2 = ''.join(format(x, '08b') for x in str2)

    #version str
    #str1 = ''.join(format(ord(i), '08b') for i in str1)
    #str2 = ''.join(format(ord(i), '08b') for i in str2)
    dist = 0

    for idx in range(len(str1)):
        if str1[idx] != str2[idx]:
            dist += 1

    return dist


def check_distance(data, keysize):

    total_dist = 0
    idx = 0
    nbChunks = 1

    while idx+keysize+keysize < len(data):
        
        c1 = data[idx:idx+keysize]
        c2 = data[idx+keysize:idx+keysize+keysize]

        dist = hamming(c1, c2)
        total_dist += dist

        idx += keysize
        nbChunks += 1

    total_dist /= keysize
    total_dist /= nbChunks

    return total_dist


def bf_chunk(data):
    
    possible_keys = {}

    for key in range(255):

        res = ""
        for x in data:
            res += chr(x ^ key)

        ascii_ratio = GetAsciiRatio(res)
        possible_keys[chr(key)] = ascii_ratio

    possible_keys = dict(sorted(possible_keys.items(), key=lambda x:x[1], reverse=True))

    return list(possible_keys.keys())[0]


def readfile(filename):
    cipher = ''
    with open(filename, 'r') as f:
        cipher = f.read()

    cipher = base64.b64decode(cipher)

    print("Cipher preview :", cipher[0:10],"...")
    return cipher


def find_keysize(cipher):
    #lets find keysize from byte distance between two potential bloc
    #could use moyenne for each keysize
    #and / or keep 2/3 shortest distance and try them all for next steps

    dicKeysize = {}

    for keysize in range(2,49):
        x = check_distance(cipher, keysize)
        dicKeysize[keysize] = x


    dicKeysize = dict(sorted(dicKeysize.items(), key=lambda x:x[1]))
    default_keysize = list(dicKeysize.keys())[0]
    
    print("possible keysize :", ', '.join([str(x) for x in list(dicKeysize.keys())[:3]]))

    keysize = input("Enter keysize (empty to use first keysize) : ")
    if not keysize:
        keysize = default_keysize
    else:
        keysize = int(keysize)

    return keysize


def transpose(cipher, keysize):

    #transpose : create blocks in keysize size
    #first block contains every first bloc, second only second blocs, etc
    tabBlocks = []

    for idx in range(len(cipher)):
        
        if idx < keysize:
            tabBlocks.append([cipher[idx]])
        else:
            tabBlocks[idx % keysize].append(cipher[idx])


    #try to bruteforce single key for each bloc

    possible_key = ""

    for bloc in tabBlocks:
        chunk_key = bf_chunk(bloc)
        possible_key += chunk_key
        
    print("Possible key :", possible_key)

    final_key = input("Enter key (empty to use possible key) : ")
    if not final_key:
        final_key = possible_key

    return final_key


def decrypt(cipher, final_key):
    idxKey = 0
    plaintext = ""
    for x in cipher:
        
        if idxKey >= len(final_key):
            idxKey = 0

        plaintext += chr(x ^ ord(final_key[idxKey]))
        idxKey += 1

    return plaintext


def solver(filename):

    cipher = readfile(filename)

    keysize = find_keysize(cipher)

    final_key = transpose(cipher, keysize)

    plaintext = decrypt(cipher, final_key)

    print("\n")
    print("PLAINTEXT : \n\n", plaintext, sep='')



solver("cipher.txt")

