import sys
import os
import pytest
import subprocess
import time

# Make the project root discoverable so that `tests` is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session", autouse=True)
def docker_services():
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    time.sleep(5)
    yield
    subprocess.run(["docker", "compose", "down"], check=True)
