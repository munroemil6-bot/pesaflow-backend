"""Application factory and shared Flask extensions for PesaFlow."""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_object="config.Config"):
	"""Create and configure the PesaFlow Flask application."""
	app = Flask(__name__)
	app.config.from_object(config_object)

	db.init_app(app)
	migrate.init_app(app, db)
	jwt.init_app(app)
	CORS(app)

	from app.routes import register_routes

	register_routes(app)
	return app