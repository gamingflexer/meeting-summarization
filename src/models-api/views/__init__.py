from flask import Blueprint

# create blueprint to group views
app_mbp = Blueprint('app', __name__, template_folder="/templates/", url_prefix="/")