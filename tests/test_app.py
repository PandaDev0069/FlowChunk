from app.main import app, read_root


def test_app_metadata_and_root_message():
    assert app.title == "FlowChunk API"
    assert app.version == "1.0.0"
    assert read_root() == {"message": "Welcome to the FlowChunk API!"}