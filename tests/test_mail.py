from unittest.mock import Mock

from google_auth.email_sender import send_email


def test_send_email_calls_gmail_api():
    fake_service = Mock()

    fake_request = Mock()
    fake_request.execute.return_value = {"id": "message123"}

    fake_service.users.return_value.messages.return_value.send.return_value = fake_request

    result = send_email(
        service=fake_service,
        recipients=["test@example.com"],
        subject="Test Briefing",
        html_body="<h1>Hello</h1>",
    )

    assert result == {"id": "message123"}

    fake_service.users.return_value.messages.return_value.send.assert_called_once()
    fake_request.execute.assert_called_once()

    send_call = fake_service.users.return_value.messages.return_value.send

    call = send_call.call_args

    assert call.kwargs["userId"] == "me"
    assert "raw" in call.kwargs["body"]

    assert isinstance(call.kwargs["body"]["raw"], str)
    assert len(call.kwargs["body"]["raw"]) > 0
