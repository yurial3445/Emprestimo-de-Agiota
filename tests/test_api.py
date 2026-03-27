import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models import User, Category, Item, Loan


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    app = create_app( TestConfig )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_full_flow(client):
    # Create user
    r = client.post('/users', json={'name': 'Alice', 'email': 'alice@example.com'})
    assert r.status_code == 201
    user_id = r.get_json()['id']

    # Create category
    r = client.post('/categories', json={'name': 'Ferramentas'})
    assert r.status_code == 201
    category_id = r.get_json()['id']

    # Create item
    r = client.post('/items', json={'name': 'Martelo', 'category_id': category_id})
    assert r.status_code == 201
    item_id = r.get_json()['id']

    # Create loan
    r = client.post('/loans', json={'user_id': user_id, 'item_id': item_id, 'due_date': '2099-12-31T12:00:00'})
    assert r.status_code == 201
    loan_id = r.get_json()['id']

    # Item no longer disponível
    r = client.get(f'/items/{item_id}')
    assert r.status_code == 404 or r.get_json().get('available') is False

    # Cannot loan again same item
    r = client.post('/loans', json={'user_id': user_id, 'item_id': item_id, 'due_date': '2099-12-31T12:00:00'})
    assert r.status_code == 400

    # Return loan com usuário correto
    r = client.post(f'/loans/{loan_id}/return', json={'user_id': user_id})
    assert r.status_code == 200

    # Delete loan
    r = client.delete(f'/loans/{loan_id}')
    assert r.status_code == 200

    # Delete item
    r = client.delete(f'/items/{item_id}')
    assert r.status_code == 200

    # Delete user
    r = client.delete(f'/users/{user_id}')
    assert r.status_code == 200
