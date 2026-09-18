import os


def sanitize_file_name(file_name: str) -> str:
    if file_name:
        file_name = os.path.basename(file_name.replace("\\", "/")).replace("\x00", "")
        if not file_name or file_name in (".", ".."):
            file_name = ""
    return file_name


def test_path_traversal_unix_traversal():
    assert sanitize_file_name("../../../../etc/passwd") == "passwd"
    assert sanitize_file_name("../../malicious.sh") == "malicious.sh"


def test_path_traversal_windows_traversal():
    assert sanitize_file_name("..\\..\\Windows\\System32\\calc.exe") == "calc.exe"
    assert sanitize_file_name("C:\\Users\\admin\\desktop\\file.txt") == "file.txt"


def test_path_traversal_null_bytes():
    assert sanitize_file_name("evil.exe\x00.png") == "evil.exe.png"


def test_path_traversal_dots():
    assert sanitize_file_name(".") == ""
    assert sanitize_file_name("..") == ""
    assert sanitize_file_name("../../..") == ""


def test_path_traversal_clean_filename():
    assert sanitize_file_name("my_photo.jpg") == "my_photo.jpg"
    assert sanitize_file_name("video_123.mp4") == "video_123.mp4"
