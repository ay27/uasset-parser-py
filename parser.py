from reader import BinaryReader
from structures import *


class UassetParser:
    def __init__(self, file_path):
        self.reader = BinaryReader(file_path)
        self.summary = FPackageFileSummary(self.reader)
        self.reader.setSummary(self.summary)
        self.nameMap = FNameMap(self.reader)
        self.reader.setNameMap(self.nameMap)
        self.importMap = FObjectImport(self.reader)
        self.reader.setImportMap(self.importMap)
        self.exportMap = FExportMap(self.reader)
        self.reader.setExportMap(self.exportMap)

    def __repr__(self):
        ret = f"[Summary]\n{self.summary}\n"
        ret += f"[NameMap]\n{self.nameMap}\n"
        ret += f"[ImportMap]\n{self.importMap}\n"
        ret += f"[ExportMap]\n{self.exportMap}\n"
        return ret


if __name__ == '__main__':
    test_file = "/Users/ay27/Downloads/ground.uasset"
    parser = UassetParser(test_file)
    print(parser)
