import pytest
from app import app

collect_ignore = ["ai-service/routes/test_rag.py"]

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client