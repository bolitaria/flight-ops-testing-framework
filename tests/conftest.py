import sys
import os
import pytest
import subprocess
import time

# Añadir la raíz del proyecto al PYTHONPATH para que 'tests' sea un módulo importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session", autouse=True)
def docker_services():
    """Levanta Docker automáticamente para todas las pruebas."""
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    time.sleep(5)
    yield
    subprocess.run(["docker", "compose", "down"], check=True)
