import io
import os
import pathlib
import tempfile

import pytest

from pyrogram import utils


class FsPath:
    def __init__(self, path):
        self.path = path

    def __fspath__(self):
        return self.path


@pytest.fixture
def sample():
    directory = tempfile.mkdtemp()
    path = os.path.join(directory, "holiday.bin")

    with open(path, "wb") as handle:
        handle.write(b"payload")

    return path


def test_an_os_pathlike_keeps_its_real_name(sample):
    assert utils.get_file_name(FsPath(sample), fallback="file.zip") == "holiday.bin"


def test_a_pathlib_path_keeps_its_real_name(sample):
    assert utils.get_file_name(pathlib.Path(sample), fallback="file.zip") == "holiday.bin"


def test_a_string_path_keeps_its_real_name(sample):
    assert utils.get_file_name(sample, fallback="file.zip") == "holiday.bin"


def test_an_open_handle_does_not_send_its_directory(sample):
    with open(sample, "rb") as handle:
        name = utils.get_file_name(handle, fallback="file.zip")

    assert name == "holiday.bin"
    assert os.sep not in name
    assert "/" not in name


def test_a_named_buffer_is_reduced_to_its_base_name():
    buffer = io.BytesIO(b"payload")
    buffer.name = os.path.join("secret", "dir", "shared.bin")

    assert utils.get_file_name(buffer, fallback="file.zip") == "shared.bin"


def test_an_explicit_name_still_wins(sample):
    assert (
        utils.get_file_name(FsPath(sample), file_name="chosen.bin", fallback="file.zip")
        == "chosen.bin"
    )


@pytest.mark.parametrize("value", [b"raw", bytearray(b"raw"), 5, None, object()])
def test_something_that_is_not_a_file_falls_back(value):
    assert utils.get_file_name(value, fallback="file.zip") == "file.zip"


def test_a_nameless_buffer_falls_back():
    assert utils.get_file_name(io.BytesIO(b"payload"), fallback="file.zip") == "file.zip"


async def test_save_file_accepts_an_os_pathlike(sample):
    from types import SimpleNamespace
    import pyrogram

    client = pyrogram.Client("uploadkinds", api_id=1, api_hash="x", in_memory=True)
    client.me = SimpleNamespace(is_bot=False, is_premium=False, id=1)

    class PoolContext:
        async def __aenter__(self):
            raise RuntimeError("stop here")

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    client._media_pool = lambda dc_id, n: PoolContext()

    with pytest.raises(Exception) as caught:
        await client.save_file(FsPath(sample))

    assert "Invalid file" not in str(caught.value)


async def test_save_file_still_refuses_bytes():
    from types import SimpleNamespace
    import pyrogram

    client = pyrogram.Client("uploadbytes", api_id=1, api_hash="x", in_memory=True)
    client.me = SimpleNamespace(is_bot=False, is_premium=False, id=1)

    with pytest.raises(ValueError, match="Invalid file"):
        await client.save_file(b"payload")
