from app import create_app, db
from app.models import User, Resource, Booking, Review

app = create_app()

with app.app_context():
    print("🗄️  Creating database tables...")
    db.create_all()
    
    if not User.query.filter_by(email='admin@coworking.com').first():
        print("👤 Creating admin user...")
        admin = User(
            email='admin@coworking.com',
            full_name='Admin User',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    if not User.query.filter_by(email='user@coworking.com').first():
        print("👤 Creating test user...")
        user = User(
            email='user@coworking.com',
            full_name='Test User',
            role='user'
        )
        user.set_password('user123')
        db.session.add(user)
    
    if Resource.query.count() == 0:
        print("🪑 Creating test resources...")
        resources = [
            Resource(name='Стол А-1', type='desk', capacity=1, floor=1, description='Обычный рабочий стол'),
            Resource(name='Стол А-2', type='desk', capacity=1, floor=1, description='Обычный рабочий стол'),
            Resource(name='Кабинет Б-1', type='cabin', capacity=4, floor=2, description='Переговорная с проектором'),
            Resource(name='Место у окна', type='window_seat', capacity=1, floor=3, description='С видом на город'),
        ]
        for resource in resources:
            db.session.add(resource)
    
    db.session.commit()
    print("✅ Database initialized successfully!")
    print("🔑 Admin: admin@coworking.com / admin123")
    print("🔑 User: user@coworking.com / user123")