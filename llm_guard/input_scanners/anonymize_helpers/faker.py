from typing import Optional

from faker import Faker

fake = Faker(seed=100)

_entity_faker_map = {
    "CREDIT_CARD": fake.credit_card_number,
    "EMAIL_ADDRESS": fake.email,
    "IBAN_CODE": fake.iban,
    "IP_ADDRESS": fake.ipv4,
    "PERSON": fake.name,
    "PHONE_NUMBER": fake.phone_number,
    "URL": fake.url,
    "US_SSN": fake.ssn,
    "CREDIT_CARD_RE": fake.credit_card_number,
    "UUID": fake.uuid4,
}


def get_fake_value(entity_type: str) -> Optional[str]:
    if entity_type not in _entity_faker_map:
        return None

    return _entity_faker_map[entity_type]()
