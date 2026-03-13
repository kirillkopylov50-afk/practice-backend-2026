from datetime import datetime

def validate_email(email):
    if not email or '@' not in email or len(email) > 120:
        return False
    return True

def validate_password(password):
    return password and len(password) >= 6

def validate_resource_data(data, is_update=False):
    errors = {}
    
    if not is_update:
        if not data.get('name') or len(data['name']) > 100:
            errors['name'] = 'Name is required (max 100 chars)'
    
    if 'type' in data:
        valid_types = ['desk', 'cabin', 'window_seat']
        if data['type'] not in valid_types:
            errors['type'] = f'Type must be one of: {", ".join(valid_types)}'
    
    if 'capacity' in data:
        if not isinstance(data['capacity'], int) or data['capacity'] < 1:
            errors['capacity'] = 'Capacity must be positive integer'
    
    if 'floor' in data:
        if not isinstance(data['floor'], int) or data['floor'] < 1:
            errors['floor'] = 'Floor must be positive integer'
    
    if 'description' in data and len(data['description']) > 1000:
        errors['description'] = 'Description too long (max 1000 chars)'
    
    return errors

def validate_booking_times(start_time_str, end_time_str):
    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
        
        if start_time >= end_time:
            return {'error': 'Start time must be before end time'}
        
        if start_time < datetime.utcnow():
            return {'error': 'Start time must be in the future'}
        
        return {'start_time': start_time, 'end_time': end_time}
    except ValueError:
        return {'error': 'Invalid datetime format. Use ISO 8601'}