from flask import Flask
from extensions import db, migrate, jwt
from config import Config
from routes import register_routes
from flask_migrate import upgrade as migrate_upgrade

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_routes(app)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
