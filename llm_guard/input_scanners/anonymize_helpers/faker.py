from __future__ import annotations

import string
from typing import Any, Callable, cast

from faker import Faker

fake = Faker()
fake.seed_instance(100)


_entity_faker_map: dict[str, Callable[[], Any]] = {
    # Global entities
    "CREDIT_CARD": fake.credit_card_number,
    "EMAIL_ADDRESS": fake.email,
    "IBAN_CODE": fake.iban,
    "IP_ADDRESS": fake.ipv4_public,
    "PERSON": fake.name,
    "PHONE_NUMBER": fake.phone_number,
    "URL": fake.url,
    "CREDIT_CARD_RE": fake.credit_card_number,
    "UUID": fake.uuid4,
    "LOCATION": fake.city,
    "DATE_TIME": fake.date,
    "CRYPTO": cast(
        Callable[[], str],
        lambda _: "bc1"
        + "".join(fake.random_choices(string.ascii_lowercase + string.digits, length=26)),
    ),
    "NRP": cast(Callable[[], str], lambda _: str(fake.random_number(digits=8, fix_len=True))),
    "MEDICAL_LICENSE": cast(Callable[[], str], lambda _: fake.bothify(text="??######").upper()),
    # US-specific entities
    "US_BANK_NUMBER": fake.bban,
    "US_SSN": fake.ssn,
    "US_DRIVER_LICENSE": cast(
        Callable[[], str], lambda _: str(fake.random_number(digits=9, fix_len=True))
    ),
    "US_ITIN": cast(Callable[[], str], lambda _: fake.bothify(text="9##-7#-####")),
    "US_PASSPORT": cast(Callable[[], str], lambda _: fake.bothify(text="#####??").upper()),
    # UK-specific entities
    "UK_NHS": cast(Callable[[], str], lambda _: str(fake.random_number(digits=10, fix_len=True))),
    # Spain-specific entities
    "ES_NIF": cast(Callable[[], str], lambda _: fake.bothify(text="########?").upper()),
    # Italy-specific entities
    "IT_FISCAL_CODE": cast(
        Callable[[], str], lambda _: fake.bothify(text="??????##?##?###?").upper()
    ),
    "IT_DRIVER_LICENSE": cast(Callable[[], str], lambda _: fake.bothify(text="?A#######?").upper()),
    "IT_VAT_CODE": cast(Callable[[], str], lambda _: fake.bothify(text="IT???????????")),
    "IT_PASSPORT": cast(
        Callable[[], str], lambda _: str(fake.random_number(digits=9, fix_len=True))
    ),
    "IT_IDENTITY_CARD": cast(
        Callable[[], str], lambda _: lambda _: str(fake.random_number(digits=7, fix_len=True))
    ),
    # Singapore-specific entities
    "SG_NRIC_FIN": cast(Callable[[], str], lambda _: fake.bothify(text="????####?").upper()),
    # Australia-specific entities
    "AU_ABN": cast(Callable[[], str], lambda _: str(fake.random_number(digits=11, fix_len=True))),
    "AU_ACN": cast(Callable[[], str], lambda _: str(fake.random_number(digits=9, fix_len=True))),
    "AU_TFN": cast(Callable[[], str], lambda _: str(fake.random_number(digits=9, fix_len=True))),
    "AU_MEDICARE": cast(
        Callable[[], str], lambda _: str(fake.random_number(digits=10, fix_len=True))
    ),
}


def get_fake_value(entity_type: str) -> str | None:
    if entity_type not in _entity_faker_map:
        return None

    return _entity_faker_map[entity_type]()
