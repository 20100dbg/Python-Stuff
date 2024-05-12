#!/usr/bin/python3
# Script created by shroudri
# Edited by 20100dbg

import argparse
import os

def getFirstChars(word, nb):
    if len(word) > nb:
        return word[0:nb]
    else:
        return word


def transform(usersfile):

    sep = ['','.','-','_']

    with open(usersfile) as f:
        lines = f.readlines()    
        for line in lines:

            line = line.lower().strip()

            if not " " in line:
                print(line)
                continue

            firstWord = line.split()[0]
            secondWord = line.split()[1]                            
            
            print(firstWord)                                   # john
            print(secondWord)                                  # lennon

            for s in sep:
                print(firstWord + s + secondWord)              # johnlennon
                print(firstWord[0] + s + secondWord)           # jlennon
                print(firstWord + s + secondWord[0])           # johnl
                print(getFirstChars(firstWord, 3) + s + getFirstChars(secondWord, 3))     # johlen

                print(secondWord + s + firstWord)              # lennonjohn
                print(secondWord + s + firstWord[0])           # lennonj
                print(secondWord[0] + s + firstWord)           # ljohn
                print(getFirstChars(secondWord, 3) + s + getFirstChars(firstWord, 3))     # lenjoh

            #print(firstWord.capitalize()) 
            #print(firstWord.upper()) 


parser = argparse.ArgumentParser(description='Python script to generate user lists for bruteforcing!')
parser.add_argument('userlist', help="Specify path to the userlist file")
args = parser.parse_args()

if args.userlist:

    if os.path.isfile(args.userlist):
        transform(args.userlist)
    else:
        print("File not found")

