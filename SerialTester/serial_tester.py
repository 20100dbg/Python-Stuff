import serial
import threading
import time
import sys
import argparse

def str_hex_to_bytes(txt):
    txt = txt.replace(' ', '')
    return bytes.fromhex(txt)

def bytes_to_hex(arr):
    return ' '.join(['{:02X}'.format(b) for b in arr])


def listener():
    last_read = 0
    need_print = False
    buffer = b''

    while True:

        if ser.in_waiting:

            data = ser.read(ser.in_waiting)
            buffer += data
            need_print = True
            last_read = time.time()
            

        if need_print and time.time() - last_read > 0.1:

            if args.hex:
                print(f"{bytes_to_hex(buffer)}")
            
            elif args.ascii:
                try:
                    print(buffer.decode())
                except Exception as e:
                    print("DECODE ERROR : data received is not ASCII")

            else:
                if args.terminal:
                    buffer = buffer[len(last_cmd)+1:]
                    print(buffer.decode(), end="")

                else:
                    print(buffer)

            buffer = b''
            need_print = False

        time.sleep(0.001)


parser = argparse.ArgumentParser(description='')

group1 = parser.add_argument_group('Basic options')
group1.add_argument('-p', '--port', metavar='', required=True, help='Device to connect. Supports S0 or /dev/ttyS0')
group1.add_argument('-b', '--baudrate', metavar='', type=int, default=9600, required=False, help='')

group2 = parser.add_argument_group('Input/output type')
group2.add_argument('-x', '--hex', action='store_true', required=False, help='read/write bytes rendered as hex (ex : CA FE BA BE)')
group2.add_argument('-a', '--ascii', action='store_true', required=False, help='read/write ASCII')
group2.add_argument('-l', '--terminal', action='store_true', required=False, help='Like ASCII with tweaks to make terminal usable')
group2.add_argument('-i', '--pipe', action='store_true', required=False, help='read/write bytes, raw for easy piping')

group3 = parser.add_argument_group('Advanced serial connection options')
group3.add_argument('-s', '--bytesize', metavar='', type=int, default=8, choices=[5,6,7,8], required=False, help='')
group3.add_argument('-r', '--parity', metavar='', default="N", choices=["N","E","O","M", "S"], required=False, help='')
group3.add_argument('-o', '--stopbits', metavar='', type=float, default=1, choices=[1,1.5,2], required=False, help='')
group3.add_argument('-t', '--timeout', metavar='', type=float, default=0.1, required=False, help='')

args = parser.parse_args()


if args.bytesize == 5:
    args.bytesize = serial.FIVEBITS
elif args.bytesize == 6:
    args.bytesize = serial.SIXBITS
elif args.bytesize == 7:
    args.bytesize = serial.SEVENBITS
elif args.bytesize == 8:
    args.bytesize = serial.EIGHTBITS

if args.parity == "N":
    args.parity = serial.PARITY_NONE
elif args.parity == "E":
    args.parity = serial.PARITY_EVEN
elif args.parity == "O":
    args.parity = serial.PARITY_ODD
elif args.parity == "M":
    args.parity = serial.PARITY_MARK
elif args.parity == "S":
    args.parity = serial.PARITY_SPACE

if args.stopbits == 1:
    args.stopbits = serial.STOPBITS_ONE
elif args.stopbits == 1.5:
    args.stopbits = serial.STOPBITS_ONE_POINT_FIVE
elif args.stopbits == 2:
    args.stopbits = serial.STOPBITS_TWO

if args.port[0:4] != "/dev" and args.port[0:3] != "COM":
    args.port = "/dev/tty" + args.port


ser = serial.Serial(port=args.port, baudrate=args.baudrate, timeout=args.timeout,
                bytesize=args.bytesize, parity=args.parity, stopbits=args.stopbits)

print(f"{args.port} {args.baudrate} {args.bytesize}{args.parity}{args.stopbits} open : {ser.is_open}")

t_receive = threading.Thread(target=listener)
t_receive.start()

last_cmd = ""

while True:

    try:

        if args.pipe:
            b = sys.stdin.buffer.read()
        else:
            txt = input()

            if args.hex:
                b = str_hex_to_bytes(txt)
            else:
                b = txt.encode()

        if args.terminal:
            b += b"\n"


        last_cmd = b
        ser.write(b)

    except KeyboardInterrupt as e:
        break

ser.close()