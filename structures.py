import struct
from typing import List

from ue_version import UE5Versions, UE4Versions


class PrintableBase:
    def __repr__(self):
        ret = f"{self.__class__.__name__}("
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            ret += f"{k}={v}, "
        ret = ret[:-2]
        ret += ")"
        return ret


class FGuid(PrintableBase):
    A: int
    B: int
    C: int
    D: int

    def __init__(self, f):
        self.A, self.B, self.C, self.D = struct.unpack('<IIII', f.read(16))


class FEngineVersion(PrintableBase):
    Major: int
    Minor: int
    Patch: int
    Changelist: int
    Branch: str

    def __init__(self, f):
        self.Major = f.readUInt16()
        self.Minor = f.readUInt16()
        self.Patch = f.readUInt16()
        self.Changelist = f.readUInt32()
        self.Branch = f.readFString()


class FCustomVersion(PrintableBase):
    key: FGuid
    Version: int

    def __init__(self, f):
        self.key = FGuid(f)
        self.Version = f.readInt32()


class FEnumCustomVersion_DEPRECATED(PrintableBase):
    Tag: int
    Version: int

    def __init__(self, f):
        self.Tag = f.readUInt32()
        self.Version = f.readInt32()


class FGuidCustomVersion_DEPRECATED(PrintableBase):
    Key: FGuid
    Version: int
    FriendlyName: str

    def __init__(self, f):
        self.Key = FGuid(f)
        self.Version = f.readInt32()
        self.FriendlyName = f.readFString()


class FCustomVersionContainer(PrintableBase):
    Versions: List[FCustomVersion]

    def __init__(self, f, LegacyFileVersion):
        if LegacyFileVersion == -2:
            format = "Enums"
            version_cls = FEnumCustomVersion_DEPRECATED
        elif -5 <= LegacyFileVersion < -2:
            format = "Guids"
            version_cls = FGuidCustomVersion_DEPRECATED
        elif LegacyFileVersion < -5:
            format = "Optimized"
            version_cls = FCustomVersion
        else:
            raise NotImplementedError("CustomVersionContainer is not implemented for this version")
        self.Versions = f.readTArray(version_cls)


class FGenerationInfo(PrintableBase):
    ExportCount: int
    NameCount: int

    def __init__(self, f):
        self.ExportCount = f.readInt32()
        self.NameCount = f.readInt32()


class FCompressedChunk(PrintableBase):
    UncompressedOffset: int
    UncompressedSize: int
    CompressedOffset: int
    CompressedSize: int

    def __init__(self, f):
        self.UncompressedOffset = f.readInt64()
        self.UncompressedSize = f.readInt64()
        self.CompressedOffset = f.readInt64()
        self.CompressedSize = f.readInt64()


PACKAGE_FILE_TAG = 0x9E2A83C1
PACKAGE_FILE_TAG_SWAPPED = 0xC1832A9E


class FPackageFileSummary(PrintableBase):
    Tag: int
    LegacyFileVersion: int
    LegacyUE3version: int
    FileVersionUE4: int
    FileVersionUE5: int
    FileVersionLicenseeUE4: int
    CustomVersionContainer: FCustomVersionContainer
    bUnversioned: bool
    TotalHeaderSize: int
    PackageName: str
    PackageFlags: int
    NameCount: int
    NameOffset: int
    SoftObjectPathsCount: int
    SoftObjectPathsOffset: int
    LocalizationId: str
    GatherableTextDataCount: int
    GatherableTextDataOffset: int
    ExportCount: int
    ExportOffset: int
    ImportCount: int
    ImportOffset: int
    DependsOffset: int
    SoftPackageReferencesCount: int
    SoftPackageReferencesOffset: int
    SearchableNamesOffset: int
    ThumbnailTableOffset: int
    Guid: FGuid
    PersistentGuid: FGuid
    OwnerPersistentGuid: FGuid
    GenerationCount: int
    Generations: List
    SavedByEngineVersion: FEngineVersion
    EngineChangelist: int
    CompatibleWithEngineVersion: FEngineVersion
    CompressionFlags: int
    CompressedChunks: List
    PackageSource: int
    AdditionalPackagesToCook: List
    NumTextureAllocations: int
    AssetRegistryDataOffset: int
    BulkDataStartOffset: int
    WorldTileInfoDataOffset: int
    ChunkIDs: List
    PreloadDependencyCount: int
    PreloadDependencyOffset: int
    NamesReferencedFromExportDataCount: int
    PayloadTocOffset: int
    DataResourceOffset: int

    def __init__(self, f):
        self.Tag = f.readUInt32()
        assert self.Tag == PACKAGE_FILE_TAG or self.Tag == PACKAGE_FILE_TAG_SWAPPED
        if self.Tag == PACKAGE_FILE_TAG_SWAPPED:
            raise ValueError("Swapped package files are not supported.")
        self.LegacyFileVersion = f.readInt32()
        if self.LegacyFileVersion >= 0:
            raise ValueError("Can not load UE3 packages.")
        if self.LegacyFileVersion != -4:
            self.LegacyUE3version = f.readInt32()
        self.FileVersionUE4 = f.readInt32()
        if self.LegacyFileVersion <= -8:
            self.FileVersionUE5 = f.readInt32()
        else:
            self.FileVersionUE5 = 0
        self.FileVersionLicenseeUE4 = f.readInt32()
        if self.LegacyFileVersion <= -2:
            self.CustomVersionContainer = FCustomVersionContainer(f, self.LegacyFileVersion)

        if (not self.FileVersionUE4) and (not self.FileVersionUE5) and (not self.FileVersionLicenseeUE4):
            self.bUnversioned = True
        else:
            self.bUnversioned = False

        self.TotalHeaderSize = f.readInt32()
        self.PackageName = f.readFString()
        self.PackageFlags = f.readUInt32()

        self.NameCount = f.readInt32()
        self.NameOffset = f.readInt32()

        if self.FileVersionUE5 >= UE5Versions.ADD_SOFTOBJECTPATH_LIST:
            self.SoftObjectPathsCount = f.readInt32()
            self.SoftObjectPathsOffset = f.readInt32()

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_ADDED_PACKAGE_SUMMARY_LOCALIZATION_ID:
            self.LocalizationId = f.readFString()

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_SERIALIZE_TEXT_IN_PACKAGES:
            self.GatherableTextDataCount = f.readInt32()
            self.GatherableTextDataOffset = f.readInt32()

        self.ExportCount = f.readInt32()
        self.ExportOffset = f.readInt32()
        self.ImportCount = f.readInt32()
        self.ImportOffset = f.readInt32()
        self.DependsOffset = f.readInt32()

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_ADD_STRING_ASSET_REFERENCES_MAP:
            self.SoftPackageReferencesCount = f.readInt32()
            self.SoftPackageReferencesOffset = f.readInt32()

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_ADDED_SEARCHABLE_NAMES:
            self.SearchableNamesOffset = f.readInt32()

        self.ThumbnailTableOffset = f.readInt32()
        self.Guid = FGuid(f)

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_ADDED_PACKAGE_OWNER:
            self.PersistentGuid = FGuid(f)

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_ADDED_PACKAGE_OWNER and \
                self.FileVersionUE4 < UE4Versions.VER_UE4_NON_OUTER_PACKAGE_IMPORT:
            self.OwnerPersistentGuid = FGuid(f)

        self.GenerationCount = f.readInt32()
        self.Generations = []
        if self.GenerationCount > 0:
            for _ in range(self.GenerationCount):
                self.Generations.append(FGenerationInfo(f))

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_ENGINE_VERSION_OBJECT:
            self.SavedByEngineVersion = FEngineVersion(f)
        else:
            self.EngineChangelist = f.readInt32()

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_PACKAGE_SUMMARY_HAS_COMPATIBLE_ENGINE_VERSION:
            self.CompatibleWithEngineVersion = FEngineVersion(f)

        self.CompressionFlags = f.readUInt32()
        self.CompressedChunks = f.readTArray(FCompressedChunk)
        if len(self.CompressedChunks) > 0:
            raise ValueError("Package level compression is enabled")

        self.PackageSource = f.readUInt32()
        self.AdditionalPackagesToCook = f.readTArray(f.readFString)

        if self.LegacyFileVersion > -7:
            self.NumTextureAllocations = f.readInt32()

        self.AssetRegistryDataOffset = f.readInt32()
        self.BulkDataStartOffset = f.readInt64()

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_WORLD_LEVEL_INFO:
            self.WorldTileInfoDataOffset = f.readInt32()

        if self.FileVersionUE4 >= UE4Versions.VER_UE4_CHANGED_CHUNKID_TO_BE_AN_ARRAY_OF_CHUNKIDS:
            self.ChunkIDs = f.readTArray(f.readInt32)

        self.PreloadDependencyCount = f.readInt32()
        self.PreloadDependencyOffset = f.readInt32()

        if self.FileVersionUE5 >= UE5Versions.NAMES_REFERENCED_FROM_EXPORT_DATA:
            self.NamesReferencedFromExportDataCount = f.readInt32()

        if self.FileVersionUE5 >= UE5Versions.PAYLOAD_TOC:
            self.PayloadTocOffset = f.readInt32()

        if self.FileVersionUE5 >= UE5Versions.DATA_RESOURCES:
            self.DataResourceOffset = f.readInt32()


class FNameEntry(PrintableBase):
    Path: str
    NonCasePreservingHash: int
    CasePreservingHash: int

    def __init__(self, f):
        self.Path = f.readFString()
        self.NonCasePreservingHash = f.readUInt16()
        self.CasePreservingHash = f.readUInt16()


class FNameMap(list, PrintableBase):
    def __init__(self, f):
        super().__init__()
        f.seek(f.summary.NameOffset, 0)
        if f.summary.NameCount == 0:
            return

        for _ in range(f.summary.NameCount):
            self.append(FNameEntry(f))


class FObjectImport(PrintableBase):
    ClassPackage: FNameEntry
    ClassName: FNameEntry
    OuterIndex: int
    ObjectName: FNameEntry
    PackageName: FNameEntry
    bImportOptional: bool

    def __init__(self, f):
        self.ClassPackage = f.readFName()
        self.ClassName = f.readFName()
        self.OuterIndex = f.readInt32()
        self.ObjectName = f.readFName()

        if f.summary.FileVersionUE4 >= UE4Versions.VER_UE4_NON_OUTER_PACKAGE_IMPORT:
            self.PackageName = f.readFName()

        if f.summary.FileVersionUE5 >= UE5Versions.OPTIONAL_RESOURCES:
            self.bImportOptional = f.readBool()


class FImportMap(list, PrintableBase):
    def __init__(self, f):
        super().__init__()
        f.seek(f.summary.ImportOffset, 0)
        if f.summary.ImportCount == 0:
            return

        for _ in range(f.summary.ImportCount):
            self.append(FObjectImport(f))


class FObjectExport(PrintableBase):
    def __init__(self, f):
        self.ClassIndex = f.readInt32()
        self.SuperIndex = f.readInt32()
        if f.summary.FileVersionUE4 >= UE4Versions.VER_UE4_TemplateIndex_IN_COOKED_EXPORTS:
            self.TemplateIndex = f.readInt32()

        self.OuterIndex = f.readInt32()
        self.ObjectName = f.readFName()
        self.ObjectFlags = f.readUInt32()

        if f.summary.FileVersionUE4 < UE4Versions.VER_UE4_64BIT_EXPORTMAP_SERIALSIZES:
            self.SerialSize = f.readInt32()
            self.SerialOffset = f.readInt32()
        else:
            self.SerialSize = f.readInt64()
            self.SerialOffset = f.readInt64()

        self.bForcedExport = f.readBool()
        self.bNotForClient = f.readBool()
        self.bNotForServer = f.readBool()

        if f.summary.FileVersionUE5 < UE5Versions.REMOVE_OBJECT_EXPORT_PACKAGE_GUID:
            self.PackageGuid = FGuid(f)

        if f.summary.FileVersionUE5 >= UE5Versions.TRACK_OBJECT_EXPORT_IS_INHERITED:
            self.bIsInheritedInstance = f.readBool()
        self.PackageFlags = f.readUInt32()

        if f.summary.FileVersionUE4 >= UE4Versions.VER_UE4_LOAD_FOR_EDITOR_GAME:
            self.bNotAlwaysLoadedForEditorGame = f.readBool()

        if f.summary.FileVersionUE4 >= UE4Versions.VER_UE4_COOKED_ASSETS_IN_EDITOR_SUPPORT:
            self.bIsAsset = f.readBool()

        if f.summary.FileVersionUE5 >= UE5Versions.OPTIONAL_RESOURCES:
            self.bGeneratePublicHash = f.readBool()

        if f.summary.FileVersionUE4 >= UE4Versions.VER_UE4_PRELOAD_DEPENDENCIES_IN_COOKED_EXPORTS:
            self.FirstExportDependency = f.readInt32()
            self.SerializationBeforeSerializationDependencies = f.readInt32()
            self.CreateBeforeSerializationDependencies = f.readInt32()
            self.SerializationBeforeCreateDependencies = f.readInt32()
            self.CreateBeforeCreateDependencies = f.readInt32()


class FExportMap(list, PrintableBase):
    def __init__(self, f):
        super().__init__()
        f.seek(f.summary.ExportOffset, 0)
        if f.summary.ExportCount == 0:
            return

        for _ in range(f.summary.ExportCount):
            self.append(FObjectExport(f))
