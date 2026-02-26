"""
Flask application for People on the Move dashboard.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask

from config import settings
from src.database.models import get_engine, get_session, init_db


def create_app():
    """Create and configure Flask application."""
    app = Flask(
        __name__,
        template_folder=str(project_root / 'src' / 'dashboard' / 'templates'),
        static_folder=str(project_root / 'static')
    )

    # Configuration
    app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
    app.config['DEBUG'] = settings.FLASK_DEBUG

    # Database setup
    app.config['DATABASE_URL'] = settings.DATABASE_URL
    engine = get_engine(settings.DATABASE_URL)

    # Ensure tables exist
    init_db(engine)

    # Store engine in app for access in routes
    app.engine = engine

    # Register routes
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Validate configuration on startup
    warnings = settings.validate_config()
    for warning in warnings:
        app.logger.warning(warning)

    return app


# Application factory
app = create_app()


if __name__ == '__main__':
    print("=" * 50)
    print("People on the Move Dashboard")
    print("=" * 50)
    print(f"\nStarting server at http://localhost:5001")
    print("Press Ctrl+C to stop\n")

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=settings.FLASK_DEBUG
    )
