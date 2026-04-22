import pytest
from unittest.mock import patch, MagicMock
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
    mock_endpoints = [
        {'endpoint_url': 'https://api.github.com', 'name': 'GitHub API'},
        {'endpoint_url': 'https://httpbin.org/get', 'name': 'HTTPBin'}
    ]
    with patch('app.routes.get_all_endpoints', return_value=mock_endpoints), \
         patch('app.routes.save_result', return_value=None):
        response = client.get('/check')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

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