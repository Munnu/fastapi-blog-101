import pytest
from fastapi.testclient import TestClient

from main import Blog, app

client = TestClient(app)


@pytest.fixture
def test_client():
    """Fixture to provide a test client for the FastAPI app."""
    return TestClient(app)


def test_index(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"data": "blog list"}


def test_published_blogs_without_published_filter(test_client):
    """Test /blog endpoint without published filter."""
    response = test_client.get("/blog?limit=5")
    assert response.status_code == 200
    assert "blogs from the db" in response.json()["data"]


def test_published_blogs_with_published_filter(test_client):
    """Test /blog endpoint with published=true filter."""
    response = test_client.get("/blog?limit=5&published=true")
    assert response.status_code == 200
    assert "published blogs from the db" in response.json()["data"]


def test_published_blogs_without_limit(test_client):
    """Test /blog endpoint without limit parameter."""
    response = test_client.get("/blog")
    assert response.status_code == 200
    assert response.json()["data"] == "None blogs from the db"


def test_unpublished_blogs(test_client):
    """Test the unpublished blogs endpoint."""
    response = test_client.get("/blog/unpublished")
    assert response.status_code == 200
    assert response.json() == {"data": "all unpublished blogs"}


def test_show_blog_by_id(test_client):
    """Test getting a blog by ID."""
    response = test_client.get("/blog/1")
    assert response.status_code == 200
    assert response.json() == {"data": 1}


def test_show_blog_with_different_id(test_client):
    """Test getting a blog with different ID."""
    response = test_client.get("/blog/42")
    assert response.status_code == 200
    assert response.json() == {"data": 42}


def test_blog_comments_default_limit(test_client):
    """Test blog comments endpoint with default limit."""
    response = test_client.get("/blog/1/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert isinstance(data["data"], list)
    assert data["data"] == ["1", "2"]


def test_blog_comments_custom_limit(test_client):
    """Test blog comments endpoint with custom limit."""
    custom_limit = 50
    response = test_client.get(f"/blog/1/comments?limit={custom_limit}")
    assert response.status_code == 200
    assert response.json()["limit"] == custom_limit


def test_create_blog(test_client):
    """Test creating a blog post."""
    blog = Blog(title="Test Blog Title", body="This is a test blog body", published=True)
    response = test_client.post("/blog", json=blog.model_dump())
    assert response.status_code == 200
    assert "Test Blog Title" in response.json()["data"]


def test_create_blog_without_published(test_client):
    """Test creating a blog without published field."""
    blog = Blog(title="Another Test", body="Another test body")
    response = test_client.post("/blog", json=blog.model_dump())
    assert response.status_code == 200
    assert "Another Test" in response.json()["data"]


def test_create_blog_missing_title():
    """Test creating a blog without required title field."""
    # Blog model requires title, so this will raise ValidationError at creation time
    with pytest.raises(ValueError):
        # Telling Pylance/Pyright that you know you're missing an argument
        Blog(body="Missing title") # type: ignore [reportMissingArgument]
