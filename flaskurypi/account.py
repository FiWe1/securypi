from flask import Blueprint
from flask import render_template


### Globals ###
bp = Blueprint("account", __name__)



@bp.route("/account")
def account():
    return render_template("account.html")    