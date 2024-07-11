import subprocess

output = subprocess.check_output(['cmd','arg1','arg2'])
print(output)


process = subprocess.Popen(["python", "-u", "child.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)



proc = subprocess.Popen(["python", "say_my_name.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


proc.stdin.write("matthew\n")
proc.stdin.write("mark\n")
proc.stdin.write("luke\n")