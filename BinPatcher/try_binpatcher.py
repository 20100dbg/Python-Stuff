from BinPatcher import *

bp = BinPatcher('file.zip')

if bp.read(0, 7) == b'PK\x03\x04\x14\x00\x06':
    print('ZIP detected')

bp.insert(1, b'\x00\x01\x02')

bp.save('file2.zip')
