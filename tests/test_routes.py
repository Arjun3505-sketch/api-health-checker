import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_loads(client):
    response = client.get('/')
    assert response.status_code == 200

def test_check_returns_list(client):
    response = client.get('/check')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_add_endpoint_validation(client):
    response = client.post('/endpoints',
        json={'name': '', 'url': ''},
        content_type='application/json')
    assert response.status_code == 400

def test_add_endpoint_invalid_url(client):
    response = client.post('/endpoints',
        json={'name': 'Test', 'url': 'not-a-url'},
        content_type='application/json')
    assert response.status_code == 400

def test_delete_endpoint_missing_url(client):
    response = client.delete('/endpoints',
        json={},
        content_type='application/json')
    assert response.status_code == 400