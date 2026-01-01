from flask import Flask
from app.routes import main_bp
from app.auth import auth_bp


def create_app():
    app = Flask(__name__, template_folder="ui/template/")
    app.secret_key = "dev-secret-change-later"

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
