from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Optional, Protocol, get_type_hints

from lxml import etree


XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"


type Children = Iterable[str | Element | None]


class PropType(Protocol):
    __annotations__: dict[str, Any]


class Element:
    namespace: Optional[str]
    name: str
    attributes: Mapping[str, str]
    children: Children

    def __init__(
        self,
        name: str,
        /,
        namespace: Optional[str] = None,
        children: Children = (),
        **attributes: str
    ) -> None:
        self.namespace = namespace
        self.name = name
        self.attributes = attributes
        self.children = children


type Namespaces = Mapping[str, tuple[str, Optional[str]]]


def build_nsmap(
    namespaces: Namespaces,
    exclude: tuple[str, ...] = ("xml",)
) -> Mapping[str, str]:
    return {
        prefix: uri
        for prefix, (uri, _) in namespaces.items()
        if prefix not in exclude
    }


def build_schema_location(namespaces: Namespaces) -> str:
    items = []

    for uri, url in namespaces.values():
        if url is not None:
            items.append(f"{uri} {url}")

    return " ".join(items)


def translate_attribute(name: str, namespaces: Namespaces) -> str:
    if ":" not in name:
        return name

    namespace, name = name.split(":", 1)
    uri, _ = namespaces[namespace]

    return f"{{{uri}}}{name}"


def build_attributes(
    attributes: Mapping[str, str],
    namespaces: Namespaces
) -> Mapping[str, str]:
    return {
        translate_attribute(key, namespaces): value
        for key, value in attributes.items()
    }


def render(
    element: Element,
    /,
    namespaces: Namespaces = {},
    root: bool = True
) -> etree._Element:
    tag: str

    if root:
        namespaces = {
            "xml": (
                XML_NAMESPACE,
                None
            ),
            "xsi": (
                XSI_NAMESPACE,
                None
            ),
            **namespaces
        }

    if element.namespace is not None:
        uri, _ = namespaces[element.namespace]
        tag = f"{{{uri}}}{element.name}"
    else:
        tag = element.name

    result = etree.Element(
        tag,
        nsmap=build_nsmap(namespaces) if root else None,
        **build_attributes(element.attributes, namespaces)
    )

    if root:
        uri, _ = namespaces["xsi"]
        prop = f"{{{uri}}}schemaLocation"
        value = build_schema_location(namespaces)

        if value:
            result.set(prop, value)

    for child in element.children:
        if child is None:
            continue
        elif isinstance(child, Element):
            result.append(render(child, namespaces=namespaces, root=False))
        else:
            result.text = child

    return result
