from flask import Flask


def create_app():
    app = Flask(__name__,
                template_folder='ui/templates',
                static_folder='ui/static')

    app.config['SECRET_KEY'] = 'dev'



    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import routes
    app.register_blueprint(routes.main_bp)

    return app