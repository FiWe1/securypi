from flask import Blueprint, render_template, redirect, url_for, flash, request

from securypi_app.services.auth import login_required, admin_rights_required
from securypi_app.peripherals.measurements.weather_station import WeatherStation
from securypi_app.models.app_config import AppConfig
from securypi_app.models.app_secrets import AppSecrets
from securypi_app.services.email import send_email_async


### Globals ###
bp = Blueprint("configure", __name__, url_prefix="/configure")


@bp.route("/start_weather_logging")
@login_required
@admin_rights_required
def start_weather_logging():
    sensor = WeatherStation.get_instance()

    try:
        sensor.measurement_logger.set_log_in_background(True)
        message = "Started logging data from sensors."
    except Exception as e:
        print(f"Error starting weather logging: {e}")
        message = "An error occured during starting weather logging."
    
    flash(message)
    return redirect(url_for("configure.index"))


@bp.route("/stop_weather_logging")
@login_required
@admin_rights_required
def stop_weather_logging():
    sensor = WeatherStation.get_instance()

    try:
        sensor.measurement_logger.set_log_in_background(False)
        message = "Stopped logging data from sensors."
    except Exception as e:
        print(f"Error stopping weather logging: {e}")
        message = "An error occured during stopping weather logging."

    flash(message)
    return redirect(url_for("configure.index"))


@bp.route("/")
@login_required
@admin_rights_required
def index():
    """ Default (index) route for configure blueprint. """
    sensor = WeatherStation.get_instance()
    is_weather_logging = sensor.measurement_logger.is_logging()
    return render_template("configure/index.html",
                           is_weather_logging=is_weather_logging)


@bp.route("/email", methods=("GET", "POST"))
@login_required
@admin_rights_required
def email_config():
    """ SMTP email configuration page. """
    config = AppConfig.get()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "save_smtp":
            try:
                config.email.smtp_host = request.form.get("smtp_host", "").strip()
                config.email.smtp_port = int(request.form.get("smtp_port", 587))
                config.email.smtp_username = request.form.get("smtp_username", "").strip()
                config.email.smtp_use_tls = request.form.get("smtp_use_tls") == "1"
                config.save()
                smtp_password = request.form.get("smtp_password", "")
                if smtp_password:  # only update password if a new one was entered
                    secrets = AppSecrets.get()
                    secrets.smtp_password = smtp_password
                    secrets.save()
                flash("SMTP settings saved.")
            except Exception as e:
                flash(f"Failed to save SMTP settings: {e}")
        return redirect(url_for("configure.email_config"))

    return render_template("configure/email.html", email_config=config.email)


@bp.route("/email/test", methods=("POST",))
@login_required
@admin_rights_required
def send_test_email():
    """ Send a test email to verify SMTP configuration. """
    to_addr = request.form.get("test_recipient", "").strip()
    if not to_addr:
        flash("Please enter a recipient email address.")
        return redirect(url_for("configure.email_config"))

    send_email_async(to_addr, "SecuryPi Test Email",
                     "This is a test email from your SecuryPi system.\n\n"
                     "If you received this, SMTP is configured correctly.")
    flash(f"Test email dispatched to {to_addr}.")
    return redirect(url_for("configure.email_config"))
