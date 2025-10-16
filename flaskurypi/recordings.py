from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("recordings", __name__)



@bp.route("/recordings")
def recordings():
    return render_template("recordings.html")    