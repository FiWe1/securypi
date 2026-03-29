from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(400)
def error_400(error):
    return (
        render_template('errors/400.html', error_description=error.description),
        400
    )

@bp.app_errorhandler(404)
def error_404(error):
    return (
        render_template('errors/404.html', error_description=error.description),
        404
    )

@bp.app_errorhandler(500)
def error_500(error):
    return (
        render_template('errors/500.html', error_description=error.description),
        500
    )