## BinPatcher
Ultra basic library to easily open, edit and save any file in binary mode.

### How to use

Get a copy of BinPatcher.py, and import the module in your script
```
from BinPatcher import *
```

Open a file : `BinPatcher(filename)`
```
bp = BinPatcher('file.zip')
```

Read a part of the file : `data = read(start_index, length)`
```
header = bp.read(0, 7)
print(header)

if bp.read(0, 7) == b'PK\x03\x04\x14\x00\x06':
    print('ZIP detected')
```

Insert data : `insert(start_index, data)`
```
bp.insert(1, b'\x00\x01\x02')
```

Edit data (replace original data with data provided as argument)  : `edit(start_index, data)`
```
bp.edit(0, b'\x00\x54\x52\x4f\x4c\x4c')
```

Save file : `save([filename)`
```
bp.save() #save in original file
bp.save('file2.zip') #save in new file
```