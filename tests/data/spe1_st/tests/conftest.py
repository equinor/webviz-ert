import pytest


@pytest.fixture(scope="session", autouse=True)
def start_storage_server():
    from ert.services import StorageService

    with StorageService.start_server() as service:
        service.wait_until_ready(timeout=30)
        yield service
