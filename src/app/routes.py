from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User, Resource, Booking
from .auth import admin_required, get_current_user
from .validators import (
    validate_email, validate_password, 
    validate_resource_data, validate_booking_times
)

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not validate_email(data.get('email')):
        return jsonify({'error': 'Invalid email'}), 400
    
    if not validate_password(data.get('password')):
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    if not data.get('full_name'):
        return jsonify({'error': 'Full name is required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'user_id': user.id,
        'token': access_token,
        'user': user.to_dict()
    }), 201

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'token': access_token,
        'user': user.to_dict()
    }), 200


@bp.route('/resources', methods=['GET'])
def get_resources():
    query = Resource.query.filter_by(is_active=True)
    
    resource_type = request.args.get('type')
    floor = request.args.get('floor')
    capacity = request.args.get('capacity')
    
    if resource_type:
        query = query.filter_by(type=resource_type)
    if floor:
        query = query.filter_by(floor=int(floor))
    if capacity:
        query = query.filter(Resource.capacity >= int(capacity))
    
    resources = query.all()
    return jsonify([r.to_dict() for r in resources]), 200

@bp.route('/resources/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    return jsonify(resource.to_dict()), 200

@bp.route('/resources', methods=['POST'])
@jwt_required()
@admin_required
def create_resource():
    data = request.get_json()
    
    errors = validate_resource_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    resource = Resource(
        name=data['name'],
        type=data['type'],
        capacity=data.get('capacity', 1),
        floor=data['floor'],
        description=data.get('description', '')
    )
    
    db.session.add(resource)
    db.session.commit()
    
    return jsonify(resource.to_dict()), 201

@bp.route('/resources/<int:resource_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    data = request.get_json()
    
    # Валидация
    errors = validate_resource_data(data, is_update=True)
    if errors:
        return jsonify({'errors': errors}), 400
    
    if 'name' in data:
        resource.name = data['name']
    if 'type' in data:
        resource.type = data['type']
    if 'capacity' in data:
        resource.capacity = data['capacity']
    if 'floor' in data:
        resource.floor = data['floor']
    if 'description' in data:
        resource.description = data['description']
    if 'is_active' in data:
        resource.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify(resource.to_dict()), 200

@bp.route('/resources/<int:resource_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    resource.is_active = False
    db.session.commit()
    
    return '', 204


@bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    current_user = get_current_user()
    
    query = Booking.query
    
    if current_user.role != 'admin':
        query = query.filter_by(user_id=current_user.id)
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    bookings = query.all()
    return jsonify([b.to_dict() for b in bookings]), 200

@bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    current_user = get_current_user()
    data = request.get_json()
    
    resource = Resource.query.get(data.get('resource_id'))
    if not resource or not resource.is_active:
        return jsonify({'error': 'Resource not found'}), 404
    
    time_validation = validate_booking_times(
        data.get('start_time'),
        data.get('end_time')
    )
    if 'error' in time_validation:
        return jsonify(time_validation), 400
    
    start_time = time_validation['start_time']
    end_time = time_validation['end_time']
    
    overlapping = Booking.query.filter(
        Booking.resource_id == resource.id,
        Booking.status == 'active',
        db.or_(
            db.and_(Booking.start_time <= start_time, Booking.end_time > start_time),
            db.and_(Booking.start_time < end_time, Booking.end_time >= end_time),
            db.and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
        )
    ).first()
    
    if overlapping:
        return jsonify({'error': 'Time slot already booked'}), 409
    
    booking = Booking(
        user_id=current_user.id,
        resource_id=resource.id,
        start_time=start_time,
        end_time=end_time
    )
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify(booking.to_dict()), 201

@bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    current_user = get_current_user()
    booking = Booking.query.get_or_404(booking_id)
    
    if current_user.role != 'admin' and booking.user_id != current_user.id:
        return jsonify({'error': 'You can only cancel your own bookings'}), 403
    
    if booking.status == 'completed':
        return jsonify({'error': 'Cannot cancel completed booking'}), 400
    
    booking.status = 'cancelled'
    db.session.commit()
    
    return '', 204