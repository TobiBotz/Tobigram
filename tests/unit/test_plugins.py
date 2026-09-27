import logging
from pyrogram.client import _plugin_handlers, Client
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.handlers.handler import Handler


def test_plugin_handlers_valid():
    class DummyTarget:
        def __init__(self):
            self.handlers = [
                (MessageHandler(lambda c, m: None), 0),
                (CallbackQueryHandler(lambda c, q: None), 1),
            ]

    target = DummyTarget()
    pairs = _plugin_handlers(target)
    assert pairs is not None
    assert len(pairs) == 2
    assert isinstance(pairs[0][0], Handler)
    assert pairs[0][1] == 0
    assert isinstance(pairs[1][0], Handler)
    assert pairs[1][1] == 1


def test_plugin_handlers_no_handlers():
    class DummyTarget:
        pass

    assert _plugin_handlers(DummyTarget()) is None
    assert _plugin_handlers(None) is None
    assert _plugin_handlers(123) is None
    assert _plugin_handlers("str") is None


def test_plugin_handlers_invalid_format():
    class DummyTarget1:
        handlers = "not-a-list"

    class DummyTarget2:
        handlers = [("not-a-handler", 0)]

    class DummyTarget3:
        handlers = [(MessageHandler(lambda c, m: None), 0, "extra")]

    assert _plugin_handlers(DummyTarget1()) is None
    assert _plugin_handlers(DummyTarget2()) is None
    assert _plugin_handlers(DummyTarget3()) is None


def test_load_plugins_group_validation(caplog, monkeypatch, tmp_path):
    plugin_dir = tmp_path / "my_plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "plugin_test.py"
    plugin_file.write_text(
        """
from pyrogram.handlers import MessageHandler

def my_func(client, message):
    pass

my_func.handlers = [
    (MessageHandler(my_func), "not_an_int"),
    (MessageHandler(my_func), 5)
]
""",
        encoding="utf-8",
    )

    import sys

    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.chdir(tmp_path)

    client = Client("test_session", api_id=12345, api_hash="abcdef", plugins={"root": "my_plugins"})
    with caplog.at_level(logging.WARNING):
        client.load_plugins()

    assert any("the group must be an int, got 'not_an_int'" in r.message for r in caplog.records)
    # The valid handler with group 5 should have been added
    assert 5 in client.dispatcher.groups
