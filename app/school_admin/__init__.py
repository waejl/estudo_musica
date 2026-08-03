# app/school_admin/__init__.py
from flask import Blueprint

school_admin_bp = Blueprint(
    "school_admin", 
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/guitar-study/school-admin/static"
)

from . import routes
