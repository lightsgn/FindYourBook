from flask import Flask


def create_app():
    # Şablonların (HTML) ve Statik dosyaların (CSS/Resim) yerini gösteriyoruz:
    app = Flask(__name__,
                template_folder='ui/templates',
                static_folder='ui/static')

    app.config['SECRET_KEY'] = 'dev'  # Veya config'den alıyorsan oradan çek

    # --- Buradan sonrası senin eski kodunla aynı kalabilir ---

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import routes
    app.register_blueprint(routes.main_bp)

    return app