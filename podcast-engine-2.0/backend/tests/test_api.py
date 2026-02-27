import pytest
from fastapi.testclient import TestClient

# Mock the database to prevent creating files
import app.db.database as db
db.DB_PATH = "data/test_database_api.sqlite"

from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_feed_endpoint_empty_db():
    # Make sure DB is empty
    import os
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    db.init_db()

    response = client.get("/api/feed")
    assert response.status_code == 200
    data = response.json()
    assert "feed" in data
    # Should return mock data if db is empty
    assert len(data["feed"]) > 0
    assert "mock_" in data["feed"][0]["id"]
    
def test_feed_endpoint_with_data():
    # Insert test data
    db.init_db()
    db.add_feed_item(
        "test_api_id", "Test API Title", "Source", "/media/api.mp3", 10.0, ["tag"], "High"
    )
    
    response = client.get("/api/feed")
    assert response.status_code == 200
    data = response.json()
    
    # Let's verify our inserted data is returned, not the mock data
    assert data["feed"][0]["id"] == "test_api_id"
    assert data["feed"][0]["title"] == "Test API Title"
