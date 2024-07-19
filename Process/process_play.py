import subprocess

output = subprocess.check_output(['cmd','arg1','arg2'])
print(output)


process = subprocess.Popen(["python", "-u", "child.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)

proc = subprocess.Popen(["python", "say_my_name.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


proc.stdin.write("matthew\n")
proc.stdin.write("mark\n")
proc.stdin.write("luke\n")



while True:
    cmd = input('> ')

    #payload = '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d","registered_commands":["HELP","CMD","SYS"],"pub_topic":"U4vyqNlQtf/0vozmaZyLT/15H9TF6CHg/pub","sub_topic":"XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub"}'
    payload = '{"id":"cdd1b1c0-1c40-4b0f-8e22-61b357548b7d", "cmd": "CMD", "arg": "'+ cmd +'", "sub_topic":"U4vyqNlQtf/0vozmaZyLT/15H9TF6CHg/pub","pub_topic":"XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub"}'

    payload = base64.b64encode(payload.encode()).decode()
    payload = f"mosquitto_pub -h 10.10.136.186 -t 'XD2rfR9Bez/GqMpRSEobh/TvLQehMg0E/sub' -m '{payload}'"
    #print(payload)

    p = subprocess.Popen(payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    (output, error) = p.communicate()
    if output or error:
        print(output, error)





p = subprocess.Popen("mosquitto_sub -h 10.10.136.186 -t '#'", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

for line in iter(p.stdout.readline, ""):
    xxx(line)

