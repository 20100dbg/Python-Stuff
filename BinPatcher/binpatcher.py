class BinPatcher:

    def __init__(self, file):
        self.file = file

        with open(file, 'rb') as f:
            self.content = f.read()

    def read(self, pos, length):
        return self.content[pos:length]

    def edit(self, pos, data):
        self.content = self.content[0:pos] + data + self.content[pos + len(data):]

    def save(self, fileDest=None):
        if fileDest is not None:
            self.file = fileDest
        
        f = open(self.file, 'wb')
        f.write(self.content)
        f.close()


bp = BinPatcher('test.zip')

if bp.read(0, 7) == b'PK\x03\x04\x14\x00\x06':
    print('ZIP detected')

bp.edit(0, b'\x00\x54\x52\x4f\x4c\x4c')

bp.save('test2.zip')
