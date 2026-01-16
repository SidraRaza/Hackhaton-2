#!/usr/bin/env python3
"""
Script to generate API documentation from FastAPI application
"""

import json
import yaml
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import os

def generate_api_documentation(app: FastAPI, output_path: str = "docs/openapi.json"):
    """
    Generate OpenAPI documentation for the FastAPI application
    """
    # Generate the OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"OpenAPI documentation saved to {output_path}")

    # Also save as YAML
    yaml_output_path = output_path.replace('.json', '.yaml')
    with open(yaml_output_path, 'w', encoding='utf-8') as f:
        yaml.dump(openapi_schema, f, default_flow_style=False, allow_unicode=True)

    print(f"OpenAPI documentation saved to {yaml_output_path}")

    return openapi_schema

def validate_api_documentation(docs_path: str = "docs/openapi.json"):
    """
    Validate the generated API documentation
    """
    try:
        with open(docs_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)

        # Basic validation checks
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in docs:
                raise ValueError(f"Missing required field: {field}")

        print("API documentation validation passed!")
        return True

    except Exception as e:
        print(f"API documentation validation failed: {e}")
        return False

if __name__ == "__main__":
    # This would normally import your main app
    # For now, we'll just validate that the docs exist and are valid
    docs_path = "docs/openapi.json"

    if os.path.exists(docs_path):
        validate_api_documentation(docs_path)
    else:
        print(f"API documentation not found at {docs_path}")
        print("Run this script from your backend directory after importing your main app")