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


def msg_usage(name=None):
    return f'''
Basic : 
    {name} -c 18 -a 10 -n 1
Specify performance settings : 
    {name} -c 18 -a 10 -n 1 -p 10 -d 9.6 -s 128
Repeater stuff :
    {name} -c 18 -a 10 -n 1 -x client
'''


print()
parser = argparse.ArgumentParser(description='HTTP POST bruteforcer')

group1 = parser.add_argument_group('Basic options')
group1.add_argument('-u', '--url', metavar='', required=True, help='URL to bruteforce')
group1.add_argument('-m', '--method', metavar='', default='POST', choices=['GET','POST'], help='HTTP METHOD')
group1.add_argument('-L', '--logins', metavar='', required=True, help='Login file')
group1.add_argument('-P', '--passwords', metavar='', required=True, help='Passwords file')

group2 = parser.add_argument_group('Request parameters')
group2.add_argument('-x', '--headers', metavar='', action='append', help='Additionnal headers, format HEADER=VALUE')
group2.add_argument('-c', '--cookies', metavar='', action='append', help='Cookies, format : NAME=VALUE')
group2.add_argument('-d', '--data', metavar='', required=True, help='POST body to send. Standard format : var1=val1&var2=val2 Use ^USER^ and ^PASS^ as placeholders')

group3 = parser.add_argument_group('String extraction')
group3.add_argument('-es', '--extract-start', metavar='', help='Extract string starting from')
group3.add_argument('-ee', '--extract-end', metavar='', help='Extract string until')
group3.add_argument('-ep', '--extract-print', metavar='', help='Just print extracted string')
group3.add_argument('-ec', '--extract-check', metavar='', help='String must contains')
group3.add_argument('-ei', '--extract-ignore', metavar='', help='String must not contains')

group4_container = parser.add_argument_group('Result detection')
group4 = group4_container.add_mutually_exclusive_group(required=True)
group4.add_argument('-s', '--success', metavar='', help='Success string to look for')
group4.add_argument('-f', '--failure', metavar='', help='Failure string to look for')
#args = parser.parse_args()
args, leftovers = parser.parse_known_args()

CONF['success'] = args.success
CONF['failure'] = args.failure
CONF['method'] = args.method.upper()

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
