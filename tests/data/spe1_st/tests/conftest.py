import pytest


@pytest.fixture(scope="session", autouse=True)
def start_storage_server():
    try:
        from ert.services import StorageService as Storage
    except ImportError:
        from ert.services import Storage

    with Storage.start_server() as service:
        service.wait_until_ready(timeout=30)
        yield service
