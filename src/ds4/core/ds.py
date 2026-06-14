import datetime
import itertools

from collections.abc import Iterable
from enum import StrEnum
from typing import (
    Annotated,
    Any,
    Literal,
    NotRequired,
    Optional,
    TypedDict,
    Union,
    Unpack
)

from pydantic import BaseModel, StringConstraints, validate_call

from . import common
from . import dsip
from .. import __version__
from .. import xml


class AttachementType(StrEnum):
    BINARY = "B"
    TEXT = "T"


class PayloadIntent(StrEnum):
    ROUTINE_PATIENT_DATA = "R"
    STATIM_PATIENT_DATA = "S"
    VITAL_PATIENT_DATA = "V"
    UZIS_REPORTS = "U"
    GENERAL_DATA = "O"
    LABORATORY_BLOCKS = "B"
    CODE_LISTS = "C"
    HYGIENE_EPIDEMIOLOGY = "H"
    TECHNICAL_TEST = "T"
    SOCIAL_SECURITY = "N"


class PmProps(TypedDict):
    address: common.Address
    contact: common.Contact


@validate_call
def Pm(**props: Unpack[PmProps]) -> xml.Element:
    """
    See: https://dastacr.cz/dasta/hypertext/DSAAD.htm
    """

    rest = dict(props)
    contact = rest.pop("contact")
    address = rest.pop("address")

    return xml.Element(
        "pm",
        namespace="ds",
        children=(
            common.As(namespace="ds", contact=contact),
            common.A(namespace="ds", address=address)
        )
    )


class ZdrojIsProps(TypedDict):
    company_id: Annotated[str, StringConstraints(max_length=8)]
    generator_id: str
    generator_version: str


@validate_call
def ZdrojIs(**props: Unpack[ZdrojIsProps]) -> xml.Element:
    rest = dict(props)

    company_id = rest.pop("company_id")
    generator_id = rest.pop("generator_id")
    generator_version = rest.pop("generator_version")

    return xml.Element(
        "zdroj_is",
        namespace="ds",
        kod_firmy=company_id,
        kod_prog=generator_id,
        verze_prog=generator_version
    )


class Sender(BaseModel):
    ic: Optional[str] = None
    icz: Optional[str] = None
    icp: Optional[str] = None
    contact: common.Contact
    address: common.Address
    patients: Iterable[dsip.Patient]


class IsProps(TypedDict):
    sender: Sender


@validate_call
def Is(**props: Unpack[IsProps]) -> xml.Element:
    rest = dict(props)

    sender = rest.pop("sender")
    
    attributes = {}

    if sender.ic:
        attributes["ico"] = sender.ic

    if sender.icz:
        attributes["icz"] = sender.icz

    if sender.icp:
        attributes["icp"] = sender.icp

    metadata_elements = (
        common.As(namespace="ds", contact=sender.contact),
        common.A(namespace="ds", address=sender.address)
    )

    patient_elements = (
        dsip.Ip(patient=patient) for patient in sender.patients
    )

    return xml.Element(
        "is",
        namespace="ds",
        children=itertools.chain(
            metadata_elements,
            patient_elements
        ),
        **attributes
    )


class DastaProps(TypedDict):
    file_id: str
    generator_metadata_props: NotRequired[ZdrojIsProps]
    recipient_metadata_props: PmProps
    attachement_type: NotRequired[AttachementType]
    intent: NotRequired[PayloadIntent]
    ds_version: NotRequired[str]
    nclp_version: NotRequired[str]
    sender_type: NotRequired[str]
    created_at: NotRequired[datetime.datetime]
    senders: Iterable[Sender]


@validate_call
def Dasta(**props: Unpack[DastaProps]) -> xml.Element:
    """
    See: https://dastacr.cz/dasta/hypertext/DSBFE.htm
    """

    rest = dict(props)

    file_id = rest.pop("file_id")
    generator_metadata_props = rest.pop(
        "generator_metadata_props",
        {
            "company_id": "NRMNCY",
            "generator_id": "pyds4",
            "generator_version": __version__
        }
    )

    recipient_metadata_props = rest.pop("recipient_metadata_props")

    attachement_type = rest.pop(
        "attachement_type",
        AttachementType.TEXT
    )

    intent = rest.pop("intent", PayloadIntent.ROUTINE_PATIENT_DATA)
    ds_version = rest.pop("ds_version", "4.28.05")
    nclp_version = rest.pop("nclp_version", "2.97.01")
    sender_type = rest.pop("sender_type", "PP")
    created_at = rest.pop("created_at", datetime.datetime.now())
    senders = rest.pop("senders")

    metadata_elements = (
        ZdrojIs(**generator_metadata_props),
        Pm(**recipient_metadata_props)
    )

    sender_elements = (Is(sender=sender) for sender in senders)

    return xml.Element(
        "dasta",
        namespace="ds",
        id_soubor=file_id,
        verze_ds=ds_version,
        verze_nclp=nclp_version,
        bin_priloha=str(attachement_type),
        ur=str(intent),
        typ_odesm=sender_type,
        dat_vb=created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        children=itertools.chain(
            metadata_elements,
            sender_elements
        ),
        **rest
    )
