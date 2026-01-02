from flask import Flask


def create_app():
    # ÖNEMLİ: template_folder='ui/templates' diyerek HTML'lerin yerini gösteriyoruz
    app = Flask(__name__,
                template_folder='ui/templates',
                static_folder='ui/static')

    app.config['SECRET_KEY'] = 'dev'

    # Veritabanı başlatma (Eğer db/__init__.py içinde init_app varsa)
    # Yoksa bu satırları silebilirsin veya yorum satırı yapabilirsin
    # from . import db
    # db.init_app(app)

    # Blueprints (Sayfa yönlendirmeleri)
    from . import auth
    app.register_blueprint(auth.bp)

    from . import routes
    app.register_blueprint(routes.main_bp)

    return app