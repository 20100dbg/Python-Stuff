import subprocess

output = subprocess.check_output(['cmd','/c','whoami'])
print(output)
