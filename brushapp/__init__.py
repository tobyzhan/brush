import os
from flask import Flask, request

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config["DEBUG"] = True

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.before_request
    def log_request():
        print(f"Incoming request method: {request.method}")
        print(f"Request URL: {request.url}")
        print("Request Headers:")
        for header, value in request.headers.items():
            print(f"{header}: {value}")

    from brushapp.homepage import homepagebp  # Absolute import
    app.register_blueprint(homepagebp)
    
    return app