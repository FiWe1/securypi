from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("temp_history", __name__)



@bp.route("/temp_history")
def temp_history():
    return render_template("temp_history.html")    