import string
from typing import Optional

from faker import Faker

fake = Faker()
fake.seed_instance(100)

_entity_faker_map = {
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
    "CRYPTO": lambda _: "bc1"
    + "".join(fake.random_choices(string.ascii_lowercase + string.digits, length=26)),
    "NRP": lambda _: str(fake.random_number(digits=8, fix_len=True)),
    "MEDICAL_LICENSE": lambda _: fake.bothify(text="??######").upper(),
    # US-specific entities
    "US_BANK_NUMBER": fake.bban,
    "US_SSN": fake.ssn,
    "US_DRIVER_LICENSE": lambda _: str(fake.random_number(digits=9, fix_len=True)),
    "US_ITIN": lambda _: fake.bothify(text="9##-7#-####"),
    "US_PASSPORT": lambda _: fake.bothify(text="#####??").upper(),
    # UK-specific entities
    "UK_NHS": lambda _: str(fake.random_number(digits=10, fix_len=True)),
    # Spain-specific entities
    "ES_NIF": lambda _: fake.bothify(text="########?").upper(),
    # Italy-specific entities
    "IT_FISCAL_CODE": lambda _: fake.bothify(text="??????##?##?###?").upper(),
    "IT_DRIVER_LICENSE": lambda _: fake.bothify(text="?A#######?").upper(),
    "IT_VAT_CODE": lambda _: fake.bothify(text="IT???????????"),
    "IT_PASSPORT": lambda _: str(fake.random_number(digits=9, fix_len=True)),
    "IT_IDENTITY_CARD": lambda _: lambda _: str(fake.random_number(digits=7, fix_len=True)),
    # Singapore-specific entities
    "SG_NRIC_FIN": lambda _: fake.bothify(text="????####?").upper(),
    # Australia-specific entities
    "AU_ABN": lambda _: str(fake.random_number(digits=11, fix_len=True)),
    "AU_ACN": lambda _: str(fake.random_number(digits=9, fix_len=True)),
    "AU_TFN": lambda _: str(fake.random_number(digits=9, fix_len=True)),
    "AU_MEDICARE": lambda _: str(fake.random_number(digits=10, fix_len=True)),
}


def get_fake_value(entity_type: str) -> Optional[str]:
    if entity_type not in _entity_faker_map:
        return None

    return _entity_faker_map[entity_type]()
