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
def checkMsg(text, success, failure):
    if success is not None and success in text:
        return True            
    if failure is not None and failure not in text:
        return True
    return False


def check(res_code, res_text):
    if res_code >= 200 and res_code < 400:
        return checkMsg(res_text, CONF['success'], CONF['failure'])

    else:
        print('[-]', res_code)
        return False


def query(url, data, method="POST"):

    if method == "POST":
        result = requests.post(url, data=data, headers=CONF['headers'], cookies=CONF['cookies'])
    else:
        result = requests.get(url + "?" + data, headers=CONF['headers'], cookies=CONF['cookies'])

    return result.status_code, result.text


def extractText(start_text, end_text):

    if type(start_text) == 'int':
        idx_start = start_text
        idx_end = end_text
    else:
        idx_start = txt.find(start_text)
        idx_end = txt.find(end_text, idx_start)

    txt = txt[idx_start+len(start_text):idx_end].strip()
    return txt
    

def fileReader(filename):
    with open(filename,'r') as file:
        while True:
            x = file.readline()
            if x:
                yield x.strip()
            else:
                yield False

def get_file_length(filename):
    nb = 0
    with open(filename,'r') as file:
        while file.readline():
            nb += 1
    return nb

print()
parser = argparse.ArgumentParser(description='HTTP POST bruteforcer')
parser.add_argument('-u', '--url', required=True, help='URL to bruteforce')
parser.add_argument('-L', '--logins', required=True, help='Login file')
parser.add_argument('-P', '--passwords', required=True, help='Passwords file')
parser.add_argument('-x', '--headers', action='append', help='Additionnal headers, format HEADER=VALUE')
parser.add_argument('-c', '--cookies', action='append', help='Cookies, format : NAME=VALUE')
parser.add_argument('-m', '--method', help='HTTP METHOD : GET / POST')
parser.add_argument('-d', '--data', required=True, help='POST body to send. Standard format : var1=val1&var2=val2 Use ^USER^ and ^PASS^ as placeholders')
parser.add_argument('-es', '--extract-start', help='Extract string starting from')
parser.add_argument('-ee', '--extract-end', help='Extract string until')
parser.add_argument('-ep', '--extract-print', help='Just print extracted string')
parser.add_argument('-ec', '--extract-check', help='String must contains')
parser.add_argument('-ei', '--extract-ignore', help='String must not contains')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-s', '--success', help='Success string to look for')
group.add_argument('-f', '--failure', help='Failure string to look for')
#args = parser.parse_args()
args, leftovers = parser.parse_known_args()

CONF['success'] = args.success
CONF['failure'] = args.failure

if args.method:
    CONF['method'] = args.method.upper()
else:
    CONF['method'] = "GET"

if args.cookies:
    for c in args.cookies:
        idx = c.find('=')
        if idx > -1:
            CONF['cookies'][c[0:idx].strip()] = c[idx+1:].strip()

if args.headers:
    for h in args.headers:
        idx = h.find('=')
        if idx > -1:
            CONF['headers'][h[0:idx].strip()] = h[idx+1:].strip()

if args.extract_start and args.extract_end:
    try:
        args.extract_start = int(args.extract_start)
        args.extract_end = int(args.extract_end)
    except Exception as e:
        args.extract_start = str(args.extract_start)
        args.extract_end = str(args.extract_end)


total_tries = get_file_length(args.logins) * get_file_length(args.passwords)

print("[+] URL :", args.url)


#check URL with random data
#
login = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
datatmp = args.data.replace("^USER^", login).replace("^PASS^", password)
res_code, res_text = query(args.url, datatmp)

if res_code != 200:
    print('[!] Beware URL is returning status code', res_code)

if checkMsg(res_text, CONF['success'], CONF['failure']):
    print('[!] Beware URL is validating your success/failure condition with random credentials')


#Start actual bruteforce
#
loginIterator = fileReader(args.logins)

nb_tries = 0
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

    res_code, res_text = query(args.url, datatmp)

    if args.extract_start and args.extract_end:
        extracted_text = extractText(res_text, args.extract_start, args.extract_end)

        check_text = checkMsg(extracted_text, args.extract_check, args.extract_ignore)

        if check_text and args.extract_print:
            print(f"[+] Found text with {login} / {password} : {extracted_text}")


    nb_tries += 1
    print(f"\rTry {nb_tries}/{total_tries}", end='')

    if check(res_code, res_text):
        print(f"\r[+] Found valid credentials : {login} / {password}")
        found = True

    password = next(passwordIterator)

print("\n[+] Done")
