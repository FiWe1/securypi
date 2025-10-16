from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("settings", __name__)



@bp.route("/settings")
def settings():
    return render_template("settings.html")    