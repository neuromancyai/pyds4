from enum import StrEnum

from typing import Literal, Optional, TypedDict, Union, Unpack

from pydantic import BaseModel, validate_call

from .. import xml


class ContactType(StrEnum):
    INTERNAL = "I"
    TELEPHONE = "T"


class InternalContact(BaseModel):
    type: Literal[ContactType.INTERNAL] = ContactType.INTERNAL
    value: Optional[str] = None
    priority: Optional[int] = None


class TelephoneContact(BaseModel):
    type: Literal[ContactType.TELEPHONE] = ContactType.TELEPHONE
    value: str
    priority: Optional[int] = None


type Contact = Union[
    InternalContact,
    TelephoneContact
]


class AddressType(StrEnum):
    RECIPIENT = "P"
    SENDER = "O"
    PLACE_OF_RESIDENCE = "1"


class Address(BaseModel):
    type: AddressType
    name: str
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    contact: Optional[Contact] = None


class AProps(TypedDict):
    namespace: str
    address: Address


@validate_call
def A(**props: Unpack[AProps]) -> xml.Element:
    rest = dict(props)
    namespace = rest.pop("namespace")
    address = rest.pop("address")

    def Jmeno(value: str) -> xml.Element:
        return xml.Element(
            "jmeno",
            namespace=namespace,
            children=(value,)
        )

    def Adr(value: str) -> xml.Element:
        return xml.Element(
            "adr",
            namespace=namespace,
            children=(value,)
        )

    def Dop1(value: str) -> xml.Element:
        return xml.Element(
            "dop1",
            namespace=namespace,
            children=(value,)
        )

    def Psc(value: str) -> xml.Element:
        return xml.Element(
            "psc",
            namespace=namespace,
            children=(value,)
        )

    def Mesto(value: str) -> xml.Element:
        return xml.Element(
            "mesto",
            namespace=namespace,
            children=(value,)
        )

    children = [Jmeno(address.name)]

    if address.address_line_1:
        children.append(Adr(address.address_line_1))

    if address.address_line_2:
        children.append(Dop1(address.address_line_2))

    if address.postal_code:
        children.append(Psc(address.postal_code))

    if address.city:
        children.append(Mesto(address.city))

    if address.contact:
        children.append(As(namespace=namespace, contact=address.contact))

    return xml.Element(
        "a",
        namespace=namespace,
        typ=str(address.type),
        children=children
    )


class AsProps(TypedDict):
    namespace: str
    contact: Contact


@validate_call
def As(**props: Unpack[AsProps]) -> xml.Element:
    rest = dict(props)
    namespace = rest.pop("namespace")
    contact = rest.pop("contact")

    def Vnitrni(value: str) -> xml.Element:
        return xml.Element(
            "vnitrni",
            namespace=namespace,
            children=(value,)
        )

    def Obsah(value: str) -> xml.Element:
        return xml.Element(
            "obsah",
            namespace=namespace,
            children=(value,)
        )

    attributes = {
        "typ": str(contact.type)
    }

    if contact.priority is not None:
        attributes["poradi"] = str(contact.priority)

    children: xml.Children

    if contact.type == ContactType.INTERNAL:
        if contact.value is not None:
            children = (Vnitrni(contact.value),)
        else:
            children = ()
    elif contact.type == ContactType.TELEPHONE:
        children = (Obsah(contact.value),)

    return xml.Element(
        "as",
        namespace=namespace,
        children=children,
        **attributes
    )
