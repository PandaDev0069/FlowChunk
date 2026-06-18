from app.app import app, read_root


def test_app_metadata_and_root_message() -> None:
    assert app.title == "FlowChunk API"
    assert app.version == "0.0.1"
    assert read_root() == {"message": "Welcome to the FlowChunk API!"}
