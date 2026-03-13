from flask import Flask
from flask_jwt_extended import JWTManager
from .models import db

def create_app():
    app = Flask(__name__)
    
    # онфигурация
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/coworking'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
    
    # нициализация расширений
    db.init_app(app)
    jwt = JWTManager(app)
    
    # егистрация blueprint
    from .routes import bp
    app.register_blueprint(bp)
    
    # Создание таблиц при запуске
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
    
    return app
