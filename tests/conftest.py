import pytest
import subprocess
import time

@pytest.fixture(scope="session", autouse=True)
def docker_services():
    """Start Docker services before tests and tear down after."""
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    time.sleep(5)  # wait for services to be healthy
    yield
    subprocess.run(["docker-compose", "down"], check=True)
