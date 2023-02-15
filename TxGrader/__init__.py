import os

from flask import Flask

from . import api, html, passthrough


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="78f67392dd4663de39382a1cac88f0d5b845a400a8d1da46a856466d670e6136",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    app.register_blueprint(html.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(passthrough.bp)

    return app
