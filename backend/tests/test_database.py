import pytest
import os
from app.db.database import init_db, add_feed_item, get_feed

# Override DB path for testing
import app.db.database as db
db.DB_PATH = "data/test_database.sqlite"

@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown the test database for each test."""
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    init_db()
    yield
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)

def test_database_initialization():
    """Test that the database initializes correctly without errors."""
    assert os.path.exists(db.DB_PATH)

def test_add_and_retrieve_feed_item():
    """Test inserting a parsed podcast segment and retrieving it."""
    test_id = "test_seg_123"
    add_feed_item(
        item_id=test_id,
        title="Test AGI Concept",
        source="Test Source",
        audio_url="/media/test.mp3",
        duration=45.5,
        tags=["Test", "Concept"],
        density="High"
    )
    
    feed = get_feed(limit=5)
    assert len(feed) == 1
    assert feed[0]["id"] == test_id
    assert feed[0]["title"] == "Test AGI Concept"
    assert "Test" in feed[0]["tags"]
