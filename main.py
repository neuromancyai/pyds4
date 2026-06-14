import datetime

import ds4.core.common
import ds4.core.ds
import ds4.core.dsip
import ds4.xml

from lxml import etree


def main():
    senders = [
        ds4.core.ds.Sender(
            contact=ds4.core.common.InternalContact(
                priority=1,
                value="pyds4"
            ),
            address=ds4.core.common.Address(
                type=ds4.core.common.AddressType.SENDER,
                name="HOME",
                address_line_1="Škrobárenská",
                address_line_2="6",
                city="Brno",
                postal_code="61700",
                contact=ds4.core.common.TelephoneContact(
                    value="603716991"
                )
            ),
            patients=[
                ds4.core.dsip.Patient(
                    personal_identity_number="6159291425",
                    first_name="Blanka",
                    last_name="Nováková",
                    birth_date=datetime.datetime.strptime("1961-09-29", "%Y-%m-%d"),
                    sex=ds4.core.dsip.Sex.FEMALE,
                    place_of_residence=ds4.core.common.Address(
                        type=ds4.core.common.AddressType.PLACE_OF_RESIDENCE,
                        name="Nováková Blanka"
                    ),
                    payment_relationship=ds4.core.dsip.LocalInsuranceCompany(
                        personal_insurance_number="6159291424",
                        insurer_code="201"
                    ),
                    medical_insurance_history=[
                        ds4.core.dsip.MedicalInsuranceRecord(
                            type=ds4.core.dsip.MedicalInsuranceRecordType.REGULAR,
                            personal_insurance_number="6159291424",
                            insurer_code="201"
                        )
                    ],
                    disability_history=[],
                    clinical_history=[
                        ds4.core.dsip.ClinicalStatement(
                            type=ds4.core.dsip.ClinicalStatementType.OUTPATIENT_EXAMINATION,
                            id="CGM_____IAD:??????3990?????????1",
                            phase=ds4.core.dsip.ClinicalStatementPhase.FINAL,
                            content=ds4.core.dsip.ClinicalStatement.Content(
                                plain_text="FIKTIVNI DEKURZ"
                            ),
                            facility=ds4.core.dsip.ClinicalStatement.Facility(
                                name="Gastroenterologie Česká",
                                icp="65240832",
                                odb="918"
                            ),
                            created_at=datetime.datetime.fromisoformat("2004-11-03T00:00:00")
                        )
                    ]
                )
            ]
        )
    ]

    root = ds4.core.ds.Dasta(
        file_id="asdf",
        recipient_metadata_props={
            "contact": ds4.core.common.InternalContact(),
            "address": ds4.core.common.Address(
                type=ds4.core.common.AddressType.RECIPIENT,
                name="GCM"
            )
        },
        senders=senders
    )

    tree = ds4.xml.render(
        root,
        namespaces={
            "ds": (
                "urn:cz-mzcr:ns:dasta:ds4:ds_dasta",
                "http://ciselniky.dasta.mzcr.cz/xmlschema/ds_dasta-4.03.34.xsd"
            ),
            "dsip": (
                "urn:cz-mzcr:ns:dasta:ds4:ds_ip",
                "http://ciselniky.dasta.mzcr.cz/xmlschema/ds_ip-4.15.12.xsd"
            )
        }
    )

    print(etree.tostring(tree, encoding="utf-8", pretty_print=True).decode("utf-8"))


if __name__ == "__main__":
    main()
