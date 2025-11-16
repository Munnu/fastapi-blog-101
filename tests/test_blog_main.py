import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from blog import models, schemas
from blog.database import get_session
from blog.main import app


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_read_root(client: TestClient):
    """Test the root endpoint returns correct message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from your SQLModel/FastAPI app!"}


def test_create_blog_entry(client: TestClient):
    """Test creating a blog post."""
    blog_data = schemas.Blog(
        title="Test Blog",
        body="This is a test blog body"
    )
    response = client.post("/blog", json=blog_data.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Blog"
    assert data["body"] == "This is a test blog body"
    assert "id" in data


def test_create_blog_entry_missing_field(client: TestClient):
    """Test creating a blog post with missing required field (title)."""
    blog_data = {
        "body": "This is a test blog body without a title"
    }
    response = client.post("/blog", json=blog_data)
    assert response.status_code == 422
    assert "title" in response.json()["detail"][0]["loc"]


def test_create_blog_entry_invalid_field_type(client: TestClient):
    """Test creating a blog post with invalid field type (int instead of string)."""
    blog_data = {
        "title": 123,  # Should be string, not int
        "body": "This is a test blog body"
    }
    response = client.post("/blog", json=blog_data)
    assert response.status_code == 422
    assert "title" in response.json()["detail"][0]["loc"]


def test_show_all_blog_entries(client: TestClient, session: Session):
    """Test retrieving all blog entries."""
    # Create test blogs
    blog1 = models.Blog(title="Blog 1", body="Body 1")
    blog2 = models.Blog(title="Blog 2", body="Body 2")
    session.add(blog1)
    session.add(blog2)
    session.commit()

    response = client.get("/blog")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Blog 1"
    assert data[1]["title"] == "Blog 2"


def test_show_blog_entry(client: TestClient, session: Session):
    """Test retrieving a single blog entry by ID."""
    blog = models.Blog(title="Test Blog", body="Test Body")
    session.add(blog)
    session.commit()
    session.refresh(blog)

    response = client.get(f"/blog/{blog.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == blog.id
    assert data["title"] == "Test Blog"
    assert data["body"] == "Test Body"


def test_show_blog_entry_not_found(client: TestClient):
    """Test retrieving a non-existent blog entry."""
    response = client.get("/blog/999")
    assert response.status_code == 404
    assert "Blog post where id=999 is not found" in response.json()["detail"]


def test_update_blog_entry(client: TestClient, session: Session):
    """Test updating a blog entry."""
    blog = models.Blog(title="Original Title", body="Original Body")
    session.add(blog)
    session.commit()
    session.refresh(blog)

    updated_data = schemas.Blog(
        title="Updated Title",
        body="Updated Body"
    )
    response = client.put(f"/blog/{blog.id}", json=updated_data.model_dump())
    assert response.status_code == 202
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["body"] == "Updated Body"


def test_update_blog_entry_not_found(client: TestClient):
    """Test updating a non-existent blog entry."""
    update_data = schemas.Blog(
        title="Updated Title",
        body="Updated Body"
    )
    response = client.put("/blog/999", json=update_data.model_dump())
    assert response.status_code == 404
    assert "Blog post where id=999 is not found" in response.json()["detail"]


def test_delete_blog_entry(client: TestClient, session: Session):
    """Test deleting a blog entry."""
    blog = models.Blog(title="To Delete", body="Delete Me")
    session.add(blog)
    session.commit()
    session.refresh(blog)

    response = client.delete(f"/blog/{blog.id}")
    assert response.status_code == 204

    # Verify it's deleted
    response = client.get(f"/blog/{blog.id}")
    assert response.status_code == 404


def test_delete_blog_entry_not_found(client: TestClient):
    """Test deleting a non-existent blog entry."""
    response = client.delete("/blog/999")
    assert response.status_code == 404
    assert "Blog post where id=999 is not found" in response.json()["detail"]
