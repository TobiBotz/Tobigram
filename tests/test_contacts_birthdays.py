from unittest.mock import Mock

import pytest

import pyrogram
from pyrogram import raw, types


class FakeContactsClient(pyrogram.Client):
    def __init__(self):
        self.sent_queries = []
        self.me = Mock(id=111, is_bot=False)

    async def invoke(self, query, **kwargs):
        self.sent_queries.append(query)

        if isinstance(query, raw.functions.contacts.GetBirthdays):
            return raw.types.contacts.ContactBirthdays(
                contacts=[
                    raw.types.ContactBirthday(
                        contact_id=12345,
                        birthday=raw.types.Birthday(day=15, month=8, year=1995),
                    ),
                    raw.types.ContactBirthday(
                        contact_id=67890,
                        birthday=raw.types.Birthday(day=22, month=11),
                    ),
                ],
                users=[
                    raw.types.User(
                        id=12345,
                        first_name="Alice",
                        access_hash=111,
                    ),
                    raw.types.User(
                        id=67890,
                        first_name="Bob",
                        access_hash=222,
                    ),
                ],
            )

        if isinstance(query, raw.functions.contacts.GetSaved):
            return [
                raw.types.SavedPhoneContact(
                    phone="+1234567890",
                    first_name="Charlie",
                    last_name="Brown",
                    date=1700000000,
                ),
                raw.types.SavedPhoneContact(
                    phone="+9876543210",
                    first_name="David",
                    last_name="Smith",
                    date=1700000100,
                ),
            ]

        raise NotImplementedError(f"Unhandled query {query}")


@pytest.mark.asyncio
async def test_get_birthdays():
    app = FakeContactsClient()

    res = await app.get_birthdays()
    assert isinstance(res, types.List)
    assert len(res) == 2

    first = res[0]
    assert isinstance(first, types.ContactBirthday)
    assert first.contact_id == 12345
    assert isinstance(first.birthday, types.Birthday)
    assert first.birthday.day == 15
    assert first.birthday.month == 8
    assert first.birthday.year == 1995
    assert isinstance(first.user, types.User)
    assert first.user.first_name == "Alice"

    second = res[1]
    assert second.contact_id == 67890
    assert second.birthday.day == 22
    assert second.birthday.month == 11
    assert second.birthday.year is None
    assert second.user.first_name == "Bob"

    q = app.sent_queries[-1]
    assert isinstance(q, raw.functions.contacts.GetBirthdays)


@pytest.mark.asyncio
async def test_get_saved_contacts():
    app = FakeContactsClient()

    res = await app.get_saved_contacts()
    assert isinstance(res, types.List)
    assert len(res) == 2

    c1 = res[0]
    assert isinstance(c1, types.SavedPhoneContact)
    assert c1.phone == "+1234567890"
    assert c1.first_name == "Charlie"
    assert c1.last_name == "Brown"
    assert c1.date is not None

    c2 = res[1]
    assert c2.phone == "+9876543210"
    assert c2.first_name == "David"

    q = app.sent_queries[-1]
    assert isinstance(q, raw.functions.contacts.GetSaved)
