import pytest


@pytest.fixture(scope="session", autouse=True)
def start_storage_server():
    try:
        from ert.services import StorageService as Storage  # noqa: PLC0415
    except ImportError:
        from ert.services import Storage  # noqa: PLC0415

    with Storage.start_server() as service:
        service.wait_until_ready(timeout=30)
        yield service
