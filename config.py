"""Environment-backed configuration for the Flask application."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
	"""Central configuration values; secrets must come from environment variables."""

	SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///pesaflow.db")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-only-change-me")
	MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")
	MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
	MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
	MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "")
	MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
	MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "")