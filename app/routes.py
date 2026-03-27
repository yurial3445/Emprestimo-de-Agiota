from flask import Blueprint, request, jsonify, send_from_directory, current_app
from app import db
from app.models import User, Category, Item, Loan
from datetime import datetime
from pathlib import Path

bp = Blueprint('main', __name__)

FRONTEND_DIR = Path(__file__).resolve().parent / 'static'

@bp.route('/', methods=['GET'])
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@bp.route('/static/<path:filename>', methods=['GET'])
def frontend_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

# Users CRUD
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'name and email are required'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'email already exists'}), 400

    user = User(name=data['name'], email=data['email'], phone=data.get('phone'))
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@bp.route('/users', methods=['GET'])
def list_users():
    return jsonify([u.to_dict() for u in User.query.all()])

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    if data.get('name'):
        user.name = data['name']
    if data.get('email'):
        user.email = data['email']
    if 'phone' in data:
        user.phone = data.get('phone')
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'deleted': user_id})

# Categories CRUD
@bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'category already exists'}), 400

    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201

@bp.route('/categories', methods=['GET'])
def list_categories():
    return jsonify([c.to_dict() for c in Category.query.all()])

@bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json() or {}
    if data.get('name'):
        category.name = data['name']
    db.session.commit()
    return jsonify(category.to_dict())

@bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'deleted': category_id})

# Items CRUD
@bp.route('/items', methods=['POST'])
def create_item():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('category_id'):
        return jsonify({'error': 'name and category_id are required'}), 400

    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'error': 'category not found'}), 404

    item = Item(
        name=data['name'],
        description=data.get('description'),
        category_id=data['category_id'],
        available=True,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@bp.route('/items', methods=['GET'])
def list_items():
    return jsonify([i.to_dict() for i in Item.query.all()])

@bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())

@bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json() or {}
    if data.get('name'):
        item.name = data['name']
    if 'description' in data:
        item.description = data.get('description')
    if data.get('category_id'):
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'category not found'}), 404
        item.category_id = category.id
    if 'available' in data:
        item.available = bool(data['available'])
    db.session.commit()
    return jsonify(item.to_dict())

@bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'deleted': item_id})

# Loans CRUD + business rules
@bp.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json() or {}
    required = ['user_id', 'item_id', 'due_date']
    if not all(data.get(key) for key in required):
        return jsonify({'error': 'user_id, item_id and due_date are required'}), 400

    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'user not found'}), 404

    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'item not found'}), 404

    if not item.available:
        return jsonify({'error': 'item is already loaned'}), 400

    try:
        due_date = datetime.fromisoformat(data['due_date'])
    except ValueError:
        return jsonify({'error': 'due_date must be ISO format'}), 400

    loan = Loan(user_id=user.id, item_id=item.id, due_date=due_date, status='borrowed')
    item.available = False
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201

@bp.route('/loans', methods=['GET'])
def list_loans():
    return jsonify([l.to_dict() for l in Loan.query.order_by(Loan.id.desc()).all()])

@bp.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    return jsonify(loan.to_dict())

@bp.route('/loans/<int:loan_id>/return', methods=['POST'])
def return_loan(loan_id):
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({'error': 'user_id is required to process return'}), 400

    loan = Loan.query.get_or_404(loan_id)
    if loan.status == 'returned':
        return jsonify({'error': 'loan already returned'}), 400

    if loan.user_id != user_id:
        return jsonify({'error': 'only the borrower can return this item'}), 403

    loan.return_date = datetime.utcnow()
    loan.status = 'returned'
    loan.item.available = True
    db.session.commit()

    return jsonify(loan.to_dict())

@bp.route('/loans/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.status == 'borrowed':
        loan.item.available = True
    db.session.delete(loan)
    db.session.commit()
    return jsonify({'deleted': loan_id})
