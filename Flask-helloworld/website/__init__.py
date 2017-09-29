from .views import test


def setup_website(app_instance):
    app_instance.register_blueprint(test.mod)

