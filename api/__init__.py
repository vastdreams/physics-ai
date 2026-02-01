# api/
"""
REST API layer for Physics AI system.

First Principle Analysis:
- API provides interface: I = {endpoints, methods, data_format}
- Endpoints: E = {/simulate, /nodes, /rules, /evolution, /cot}
- Mathematical foundation: REST principles, HTTP protocol, JSON serialization
- Architecture: Flask-based API with modular endpoints
"""

from flask import Flask

__all__ = ['create_app']

