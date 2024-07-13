class BinPatcher:

    def __init__(self, file):
        self.file = file

        with open(file, 'rb') as f:
            self.content = f.read()

    def read(self, pos, length):
        return self.content[pos:length]

    def edit(self, pos, data):
        self.content = self.content[0:pos] + data + self.content[pos + len(data):]

    def insert(self, pos, data):
        self.content = self.content[0:pos] + data + self.content[pos:]

    def save(self, fileDest=None):
        if fileDest is not None:
            self.file = fileDest
        
        f = open(self.file, 'wb')
        f.write(self.content)
        f.close()
