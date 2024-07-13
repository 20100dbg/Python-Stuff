## BrutePost
A simple but flexible HTTP POST bruteforcer.

### How to use

Get a copy of brutepost.py, list arguments with
```
python brutepost.py -h
```

Use ^USER^ and ^PASS^ as placeholders in the -d/--data argument to replace with users/passwords to try.

Simple example
```
python brutepost.py -u http://localhost/ -L users.txt -P passwords.txt -d "login=^USER^&password=^PASS^" -s "Welcome"
```

Add headers and cookies

```
-x "X-Forwarded-For=127.0.0.1" -x "X-Forwarded-Host=127.0.0.1 -c "PHPSESSID=xxx" -c "role=admin"
```
