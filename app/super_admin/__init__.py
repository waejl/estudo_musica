# app/super_admin/__init__.py
from flask import Blueprint

super_admin_bp = Blueprint(
    "super_admin",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/super-admin/static"
)

from . import routes
