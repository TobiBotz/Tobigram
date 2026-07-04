from pyrogram.types import User as PyroUser


class Client:
    def __init__(self):
        self.me = PyroUser(
            id=123, is_self=False, is_contact=False, is_mutual_contact=False,
            is_deleted=False, is_bot=False, is_premium=False, is_support=False,
            first_name="User", username="username"
        )

    async def get_me(self):
        return self.me


class Message:
    def __init__(self, text: str = None, caption: str = None):
        self.text = text
        self.caption = caption
        self.command = None
