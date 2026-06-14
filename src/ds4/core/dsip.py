import datetime
import itertools

from collections.abc import Iterable
from enum import StrEnum
from typing import (
    Literal,
    Optional,
    TypedDict,
    Unpack
)

from pydantic import BaseModel, validate_call

from . import common
from .. import xml


class Sex(StrEnum):
    FEMALE = "F"
    MALE = "M"


class MedicalInsuranceRecordType(StrEnum):
    REGULAR = "N"
    CORRECTION = "E"
    CANCELLED = "S"


class MedicalInsuranceRecord(BaseModel):
    type: MedicalInsuranceRecordType
    personal_insurance_number: str
    insurer_code: str


type MedicalInsuranceHistory = Iterable[MedicalInsuranceRecord]


class DisabilityRecord(BaseModel):
    pass


type DisabilityHistory = Iterable[DisabilityRecord]


class PaymentRelationshipType(StrEnum):
    LOCAL_INSURANCE_COMPANY = "ZP"


class LocalInsuranceCompany(BaseModel):
    type: Literal[PaymentRelationshipType.LOCAL_INSURANCE_COMPANY] = \
        PaymentRelationshipType.LOCAL_INSURANCE_COMPANY

    personal_insurance_number: str
    insurer_code: str



type PaymentRelationship = LocalInsuranceCompany


class ClinicalStatementType(StrEnum):
    OUTPATIENT_EXAMINATION = "AMB.VYS"


class ClinicalStatementPhase(StrEnum):
    FINAL = "ZF"


class ClinicalStatement(BaseModel):
    class Content(BaseModel):
        author: Optional[str] = None
        plain_text: str

    class Facility(BaseModel):
        name: str
        icp: str
        odb: str

    id: str
    type: ClinicalStatementType
    phase: ClinicalStatementPhase
    content: Content
    facility: Facility
    created_at: datetime.datetime


type ClinicalRecord = ClinicalStatement


type ClinicalHistory = Iterable[ClinicalRecord]


class Patient(BaseModel):
    personal_identity_number: str
    first_name: str
    last_name: str
    nationality: Optional[str] = None
    birth_date: datetime.datetime
    sex: Sex
    place_of_residence: common.Address
    payment_relationship: PaymentRelationship
    medical_insurance_history: MedicalInsuranceHistory
    disability_history: DisabilityHistory
    clinical_history: ClinicalHistory


def Cispoj(value: str) -> xml.Element:
    return xml.Element(
        "cispoj",
        namespace="dsip",
        children=(value,)
    )


def Kodpoj(value: str) -> xml.Element:
    return xml.Element(
        "kodpoj",
        namespace="dsip",
        children=(value,)
    )


class PProps(TypedDict):
    record: MedicalInsuranceRecord


def P(**props: Unpack[PProps]) -> xml.Element:
    rest = dict(props)
    record = rest.pop("record")

    return xml.Element(
        "p",
        namespace="dsip",
        ind_oprav_sd=str(record.type),
        children=(
            Cispoj(record.personal_insurance_number),
            Kodpoj(record.insurer_code)
        )
    )


class PnProps(TypedDict):
    record: Optional[DisabilityRecord]


def Pn(**props: Unpack[PnProps]) -> xml.Element:
    rest = dict(props)
    record = rest.pop("record")

    raise NotImplementedError


class IpProps(TypedDict):
    patient: Patient


class PvPacProps(TypedDict):
    payment_relationship: PaymentRelationship


@validate_call
def PvPac(**props: Unpack[PvPacProps]) -> xml.Element:
    """
    See: https://dastacr.cz/dasta/hypertext/WWBIP.htm
    """

    def PvPacZp(value: LocalInsuranceCompany) -> xml.Element:
        return xml.Element(
            "pv_zp",
            namespace="dsip",
            children=(
                Cispoj(value.personal_insurance_number),
                Kodpoj(value.insurer_code)
            )
        )

    rest = dict(props)
    payment_relationship = rest.pop("payment_relationship")
    children: tuple[xml.Element]
    attributes = {
        "typ_pv": str(payment_relationship.type)
    }

    match payment_relationship:
        case LocalInsuranceCompany():
            children = (PvPacZp(value=payment_relationship),)
        case _:
            raise NotImplementedError

    return xml.Element(
        "pv_pac",
        namespace="dsip",
        children=children,
        **attributes
    )


class KuZProps(TypedDict):
    statement: ClinicalStatement


@validate_call
def KuZ(**props: Unpack[KuZProps]) -> xml.Element:
    """
    See: https://dastacr.cz/dasta/hypertext/MZAUJ.htm
    """

    def Text(value: ClinicalStatement.Content) -> xml.Element:
        def Ptext(value: str) -> xml.Element:
            attributes = {
                "xml:space": "preserve"
            }

            return xml.Element(
                "ptext",
                namespace="dsip",
                children=(value,),
                **attributes
            )

        return xml.Element(
            "text",
            namespace="dsip",
            children=(
                Ptext(value=value.plain_text),
            )
        )

    def DatProv(value: datetime.datetime) -> xml.Element:
        return xml.Element(
            "dat_prov",
            namespace="dsip",
            children=(value.isoformat(timespec="seconds"),)
        )

    def DatRealOd(value: datetime.datetime) -> xml.Element:
        return xml.Element(
            "dat_real_od",
            namespace="dsip",
            children=(value.isoformat(timespec="seconds"),)
        )

    def DatRealDo(value: datetime.datetime) -> xml.Element:
        return xml.Element(
            "dat_real_do",
            namespace="dsip",
            children=(value.isoformat(timespec="seconds"),)
        )

    def DatVydani(value: datetime.datetime) -> xml.Element:
        return xml.Element(
            "dat_vydani",
            namespace="dsip",
            children=(value.isoformat(timespec="seconds"),)
        )

    def PPracoviste(value: ClinicalStatement.Facility) -> xml.Element:
        def Nazev(value: str) -> xml.Element:
            return xml.Element(
                "nazev",
                namespace="dsip",
                children=(value,)
            )

        return xml.Element(
            "p_pracoviste",
            namespace="dsip",
            icp=value.icp,
            odb=value.odb,
            children=(
                Nazev(value=value.name),
            )
        )

    rest = dict(props)
    statement = rest.pop("statement")

    return xml.Element(
        "ku_z",
        namespace="dsip",
        typku=str(statement.type),
        fazespec=str(statement.phase),
        idku=str(statement.id),
        children=(
            DatProv(value=statement.created_at),
            DatRealOd(value=statement.created_at),
            DatRealDo(value=statement.created_at),
            DatVydani(value=statement.created_at),
            PPracoviste(value=statement.facility),
            Text(value=statement.content)
        )
    )


class KuProps(TypedDict):
    history: ClinicalHistory


@validate_call
def Ku(**props: Unpack[KuProps]) -> xml.Element:
    """
    See: https://dastacr.cz/dasta/hypertext/MZAUK.htm
    """

    rest = dict(props)
    history = rest.pop("history")
    children = []

    for record in history:
        match record:
            case ClinicalStatement():
                children.append(KuZ(statement=record))
            case _:
                raise NotImplementedError

    return xml.Element(
        "ku",
        namespace="dsip",
        children=children
    )


@validate_call
def Ip(**props: Unpack[IpProps]) -> xml.Element:
    """
    See: https://dastacr.cz/dasta/hypertext/MZAUO.htm
    """

    def Rodcis(value: str) -> xml.Element:
        return xml.Element(
            "rodcis",
            namespace="dsip",
            children=(value,)
        )
    
    def Jmeno(value: str) -> xml.Element:
        return xml.Element(
            "jmeno",
            namespace="dsip",
            children=(value,)
        )

    def Prijmeni(value: str) -> xml.Element:
        return xml.Element(
            "prijmeni",
            namespace="dsip",
            children=(value,)
        )

    def StatPris(value: str) -> xml.Element:
        return xml.Element(
            "stat_pris",
            namespace="dsip",
            children=(value,)
        )


    def DatDn(value: datetime.datetime) -> xml.Element:
        return xml.Element(
            "dat_dn",
            namespace="dsip",
            format="D",
            children=(value.strftime("%Y-%m-%d"),)
        )

    def SexEl(value: Sex) -> xml.Element:
        return xml.Element(
            "sex",
            namespace="dsip",
            children=(str(value),)
        )

    rest = dict(props)
    patient = rest.pop("patient")
    medical_insurance_history = list(patient.medical_insurance_history)
    disability_history = list(patient.disability_history)
    clinical_history = list(patient.clinical_history)

    main_elements = [
        Rodcis(patient.personal_identity_number),
        Jmeno(patient.first_name),
        Prijmeni(patient.last_name),
        DatDn(patient.birth_date)
    ]

    if patient.nationality:
        main_elements.append(StatPris(patient.nationality))

    main_elements.extend([
        SexEl(patient.sex),
        common.A(namespace="ds", address=patient.place_of_residence),
        PvPac(payment_relationship=patient.payment_relationship)
    ])

    medical_insurance_history_elements = (
        P(record=record) for record in medical_insurance_history
    )

    disability_history_elements = (
        Pn(record=record) for record in disability_history
    )

    clinical_history_elements: Iterable[xml.Element]

    if clinical_history:
        clinical_history_elements = (Ku(history=clinical_history),)
    else:
        clinical_history_elements = ()

    return xml.Element(
        "ip",
        namespace="dsip",
        typ_id_pac="0",
        id_pac=patient.personal_identity_number,
        children=itertools.chain(
            main_elements,
            medical_insurance_history_elements,
            disability_history_elements,
            clinical_history_elements
        )
    )
