"""
Models Package
===============
Imports all models so SQLAlchemy can discover them for table creation.

WHY THIS FILE EXISTS:
    Python needs __init__.py to treat 'models/' as an importable package.
    Importing all models here ensures db.create_all() finds every table.
"""

from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.resume import Resume

__all__ = ['User', 'Job', 'Application', 'Resume']
