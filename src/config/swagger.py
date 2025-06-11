from flasgger import Swagger
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

def init_swagger(app):
    """Initialize Swagger documentation."""
    # Create APISpec
    spec = APISpec(
        title="Sprpsr API",
        version="1.0.0",
        openapi_version="3.0.2",
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
        info={
            "description": "API documentation for Sprpsr application",
            "contact": {
                "name": "API Support",
                "email": "support@sprpsr.com"
            }
        }
    )

    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Sprpsr API",
            "description": "API documentation for Sprpsr application",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@sprpsr.com"
            }
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    # Initialize Swagger
    swagger = Swagger(app, config=swagger_config, template=swagger_template)

    return spec 