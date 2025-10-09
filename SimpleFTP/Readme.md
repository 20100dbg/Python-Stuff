# SimpleFTP

Really simple FTP server, without installing a service or complex configuration.


Now in two flavour :
- full-server.py : more features, supports more clients
- minimal-server.py : only basic features, supports only tnftp (your ftp command)


#### Basic Features

- Upload / download files
- Basic navigation
- Passive mode only
- Logins or anonymous mode
- Path safety checks


#### Full Features

- Tested against tnftp, gFtp, Filezilla
- PASV and EPSV modes
- Multiple clients at once (not tested but I feel lucky)


#### Basic options

##### -p / --port
Port to listen (Default is 21)

##### -r / --root_dir
TP root directory (Default is data/)

##### -l / --login
Login to use (Default is anonymous)

##### -a / --password
Password to use (Default is anonymous)

##### -d / --debug
Output debug informations

