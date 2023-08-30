"""Seed for DICOM"""
from enum import Enum

from pydicom import dcmread
from pydicom.dataset import Dataset, FileDataset


from seed.arg import NumberArg, StringArg, Arg, EnumArg 
from seed.fn import Fn
from seed import Seed
from utils import PATH_DUMMY

dummy_file = PATH_DUMMY.joinpath("test.dcm")


def defaul_dataset() -> Dataset:
    ds = Dataset()
    ds.QueryRetrieveLevel = 'SERIES'
    ds.PatientID = '1234567'
    ds.StudyInstanceUID = '1.2.3'
    ds.SeriesInstanceUID = '1.2.3.4'
    return ds


class DICOMDatasetArg(Arg[Dataset]):
    def mutate(self) -> None:
        return super().mutate()

    def unpack(self):
        return self.value


class DICOMFileDatasetArg(Arg[FileDataset]):
    def mutate(self) -> None:
        # A lot of mutation can be done
        return 

    def unpack(self):
        return self.value


class SOPClassFind(Enum):
    PatientRootQueryRetrieveInformationModelFind = "1.2.840.10008.5.1.4.1.2.1.1"
    ModalityWorklistInformationFind = "1.2.840.10008.5.1.4.31"
    ColorPaletteInformationModelFind = "1.2.840.10008.5.1.4.39.2"
    DefinedProcedureProtocolInformationModelFind = "1.2.840.10008.5.1.4.20.1"
    HangingProtocolInformationModelFind = "1.2.840.10008.5.1.4.38.2"
    GenericImplantTemplateInformationModelFind = "1.2.840.10008.5.1.4.43.2"
    ImplantAssemblyTemplateInformationModelFind = "1.2.840.10008.5.1.4.44.2"
    ImplantTemplateGroupInformationModelFind = "1.2.840.10008.5.1.4.45.2"
    ProtocolApprovalInformationModelFind = "1.2.840.10008.5.1.4.1.1.200.4"
    StudyRootQueryRetrieveInformationModelFind = "1.2.840.10008.5.1.4.1.2.2.1"
    PatientStudyOnlyQueryRetrieveInformationModelFind = "1.2.840.10008.5.1.4.1.2.3.1"


class SOPClassGet(Enum):
    PatientRootQueryRetrieveInformationModelGet = "1.2.840.10008.5.1.4.1.2.1.3"
    ColorPaletteInformationModelGet = "1.2.840.10008.5.1.4.39.4"
    DefinedProcedureProtocolInformationModelGet = "1.2.840.10008.5.1.4.20.3"
    HangingProtocolInformationModelGet = "1.2.840.10008.5.1.4.38.4"
    GenericImplantTemplateInformationModelGet = "1.2.840.10008.5.1.4.43.4"
    ImplantAssemblyTemplateInformationModelGet = "1.2.840.10008.5.1.4.44.4"
    ImplantTemplateGroupInformationModelGet = "1.2.840.10008.5.1.4.45.4"
    ProtocolApprovalInformationModelGet = "1.2.840.10008.5.1.4.1.1.200.6"
    StudyRootQueryRetrieveInformationModelGet = "1.2.840.10008.5.1.4.1.2.2.3"
    PatientStudyOnlyQueryRetrieveInformationModelGet = "1.2.840.10008.5.1.4.1.2.3.3"
    CompositeInstanceRootRetrieveGet = "1.2.840.10008.5.1.4.1.2.4.3"
    CompositeInstanceRetrieveWithoutBulkDataGet = "1.2.840.10008.5.1.4.1.2.5.3"


class SOPClassMove(Enum):
    ColorPaletteInformationModelMove = "1.2.840.10008.5.1.4.39.3"
    PatientRootQueryRetrieveInformationModelMove = "1.2.840.10008.5.1.4.1.2.1.2"
    DefinedProcedureProtocolInformationModelMove = "1.2.840.10008.5.1.4.20.2"
    HangingProtocolInformationModelMove = "1.2.840.10008.5.1.4.38.3"
    GenericImplantTemplateInformationModelMove = "1.2.840.10008.5.1.4.43.3"
    ImplantAssemblyTemplateInformationModelMove = "1.2.840.10008.5.1.4.44.3"
    ImplantTemplateGroupInformationModelMove = "1.2.840.10008.5.1.4.45.3"
    ProtocolApprovalInformationModelMove = "1.2.840.10008.5.1.4.1.1.200.5"
    StudyRootQueryRetrieveInformationModelMove = "1.2.840.10008.5.1.4.1.2.2.2"
    PatientStudyOnlyQueryRetrieveInformationModelMove = "1.2.840.10008.5.1.4.1.2.3.2"
    CompositeInstanceRootRetrieveMove = "1.2.840.10008.5.1.4.1.2.4.2"


class SOPClassStore(Enum):
    pass


SEED = Seed([
    Fn('send_c_echo', [NumberArg(1, name='msg_id')]),
    Fn('send_c_store', [DICOMFileDatasetArg(dcmread(dummy_file))]),
    Fn('send_c_find', [
        DICOMDatasetArg(defaul_dataset()), 
        EnumArg(SOPClassFind.PatientRootQueryRetrieveInformationModelFind, use_value=True), 
        NumberArg(1, name="msg_id"), 
        NumberArg(2, name='priority')
    ]),
    Fn('send_c_get', [
        DICOMDatasetArg(defaul_dataset()), 
        EnumArg(SOPClassGet.PatientRootQueryRetrieveInformationModelGet, use_value=True),
        NumberArg(1, name="msg_id"), 
        NumberArg(2, name='priority')
    ]),
    Fn('send_c_move', [
        DICOMDatasetArg(defaul_dataset()), 
        StringArg('PYNETDICOM'), 
        EnumArg(SOPClassMove.PatientRootQueryRetrieveInformationModelMove, use_value=True),
        NumberArg(1, name="msg_id"), 
        NumberArg(2, name='priority')
    ]),
    Fn('send_c_cancel', [NumberArg(1), NumberArg(1, nullable=True), EnumArg(SOPClassGet.PatientRootQueryRetrieveInformationModelGet)]),
    Fn('release', is_last=True)
])