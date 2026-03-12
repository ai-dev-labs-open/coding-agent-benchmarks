from notifications import reminder_message, welcome_message


def test_welcome_message() -> None:
    assert welcome_message("Levan") == "Hello Levan, welcome aboard."


def test_reminder_message() -> None:
    assert reminder_message("Levan") == "Hello Levan, please verify your email."


def test_helper_was_extracted() -> None:
    namespace: dict[str, object] = {}
    exec(open("notifications.py", encoding="utf-8").read(), namespace)
    assert "make_message" in namespace
