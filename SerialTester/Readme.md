# SerialTester

Easily connect to your serial devices.


#### Basic options

##### -p / --port
Device to connect. Supports COMx, S0 or /dev/ttyS0.

##### -b / --baudrate
Baudrate to use. Usually 9600 (default) or 115200, other values are possible.


#### Input/output type

##### -x / --hex
Read/write bytes rendered as hex (ex : CA FE BA BE)

##### -a / --ascii
Read/write ASCII

##### -l / --terminal
Like ASCII with tweaks to make terminal usable

##### -i / --pipe
Read/write bytes, raw for easy piping


#### Advanced serial connection options

##### -s / --bytesize
Set byte size between 5,6,7,8 (Default is 8)

##### -s / --bytesize
Set byte parity between N, E, O, M, S (Default is N)

##### -o / --stopbits
Set stop bit between 1, 1.5, 2 (Default is 1)

##### -t / --timeout
Set timeout duration in seconds (Default is 0.1)

