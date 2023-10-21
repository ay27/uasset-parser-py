import struct


class BinaryReader(object):
    def __init__(self, filepath):
        self.f = open(filepath, 'rb')

    def read(self, size=1):
        return self.f.read(size)

    def seek(self, offset, whence=0):
        self.f.seek(offset, whence)

    def skip(self, offset):
        self.f.read(offset)

    def tell(self):
        return self.f.tell()

    def readBool(self):
        """Booleans in UE are serialized as int32"""
        val = self.readInt32()
        if val not in [0, 1]:
            raise ValueError("Invalid boolean value")
        return val != 0

    def readUInt16(self):
        v, = struct.unpack('<H', self.f.read(2))
        return v

    def readUInt32(self):
        v, = struct.unpack('<I', self.f.read(4))
        return v

    def readInt32(self):
        v, = struct.unpack('<i', self.f.read(4))
        return v

    def readInt64(self):
        v, = struct.unpack('<q', self.f.read(8))
        return v

    def readUInt64(self):
        v, = struct.unpack('<Q', self.f.read(8))
        return v

    def readFString(self) -> str:
        length = self.readInt32()
        if length < 0:
            raise ValueError(f"do not support wide char, length: {length}")
        byte = self.f.read(length)[:-1]
        return byte.decode("utf-8")

    def readTArray(self, item_cls):
        ret = []
        SerializeNum = self.readInt32()
        for _ in range(SerializeNum):
            ret.append(item_cls(self))
        return ret

    def readFName(self):
        NameMap = self.nameMap
        NameIndex = self.readInt32()
        Number = self.readInt32()

        if not 0 <= NameIndex < len(NameMap):
            raise ValueError(f"NameIndex out of range: {NameIndex}")

        return NameMap[NameIndex]

    def setSummary(self, summary):
        self.summary = summary

    def setNameMap(self, nameMap):
        self.nameMap = nameMap

    def setImportMap(self, importMap):
        self.importMap = importMap

    def setExportMap(self, exportMap):
        self.exportMap = exportMap
