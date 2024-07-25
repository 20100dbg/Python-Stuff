import subprocess
import threading


p = subprocess.Popen("cmd", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

while True:
    print(p.stdout.readline())
    p.stdout.flush()


p.stdin.write("abc\n")
p.stdin.write("cat\n")
p.stdin.close()





