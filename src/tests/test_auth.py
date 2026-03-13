import pytest
import json
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_user(client):
    response = client.post('/api/auth/register',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123',
            'full_name': 'Test User'
        }),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'token' in data
    assert data['user']['email'] == 'test@example.com'

def test_login(client):
    client.post('/api/auth/register',
        data=json.dumps({
            'email': 'login@test.com',
            'password': 'password123',
            'full_name': 'Login Test'
        }),
        content_type='application/json'
    )
    
    response = client.post('/api/auth/login',
        data=json.dumps({
            'email': 'login@test.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert 'token' in json.loads(response.data)

def test_create_resource_without_auth(client):
    response = client.post('/api/resources',
        data=json.dumps({
            'name': 'Test Resource',
            'type': 'desk',
            'capacity': 1,
            'floor': 1
        }),
        content_type='application/json'
    )
    assert response.status_code == 401

def test_create_resource_as_user(client):
    client.post('/api/auth/register',
        data=json.dumps({
            'email': 'regular@test.com',
            'password': 'password123',
            'full_name': 'Regular User'
        }),
        content_type='application/json'
    )
    
    login_response = client.post('/api/auth/login',
        data=json.dumps({
            'email': 'regular@test.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    token = json.loads(login_response.data)['token']
    
    response = client.post('/api/resources',
        data=json.dumps({
            'name': 'Test Resource',
            'type': 'desk',
            'capacity': 1,
            'floor': 1
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403