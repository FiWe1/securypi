from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("camera_control", __name__)



@bp.route("/camera_control")
def camera_control():
    return render_template("camera_control.html")    