import logging
from threading import Thread

from securypi_app.services.email import send_email_async

logger = logging.getLogger(__name__)


def parse_save_notification_prefs(prefs, form):
    """
    Parse and validate notification prefs form. Returns error string or None.
    """
    prefs.motion_capture_enabled = form.get("motion_capture_enabled") == "1"
    prefs.temp_enabled = form.get("temp_enabled") == "1"
    prefs.humidity_enabled = form.get("humidity_enabled") == "1"
    prefs.pressure_enabled = form.get("pressure_enabled") == "1"

    parsed = {}
    for field in ("temp_lower", "temp_upper",
                  "humidity_lower", "humidity_upper",
                  "pressure_lower", "pressure_upper"):
        raw = form.get(field, "").strip()
        if raw == "":
            parsed[field] = None
        else:
            try:
                parsed[field] = float(raw)
            except ValueError:
                return f"Invalid value for {field.replace('_', ' ')}: '{raw}'"

    # validate lower <= upper for each metric
    for metric in ("temp", "humidity", "pressure"):
        lower = parsed[f"{metric}_lower"]
        upper = parsed[f"{metric}_upper"]
        if lower is not None and upper is not None and lower > upper:
            label = {"temp": "temperature", "humidity": "humidity",
                     "pressure": "pressure"}[metric]
            return f"{label.capitalize()} lower limit must not exceed upper limit."

    cooldown_raw = form.get("cooldown_minutes", "60").strip()
    try:
        cooldown = int(cooldown_raw)
        if cooldown < 1:
            raise ValueError
    except ValueError:
        return "Cooldown must be a positive whole number of minutes."

    for field, value in parsed.items():
        setattr(prefs, field, value)
    prefs.cooldown_minutes = cooldown

    try:
        from securypi_app.models import db
        db.session.commit()
    except Exception:
        from securypi_app.models import db
        db.session.rollback()
        return "Failed to save preferences due to a database error."

    return None


def notify_motion_capture(app):
    """
    Send motion capture email alerts to all users who have
    motion_capture_enabled=True and a valid email address.
    Opens its own app context — safe to call from background threads.
    """
    def _run():
        try:
            with app.app_context():
                from securypi_app.models.notification_prefs import NotificationPrefs
                from securypi_app.models.user import User

                all_prefs = NotificationPrefs.get_all_motion_enabled()
                logger.debug("notify_motion_capture: %d user(s) with motion alerts enabled", len(all_prefs))

                for prefs in all_prefs:
                    if not prefs.is_cooldown_expired("motion"):
                        logger.debug("notify_motion_capture: user_id=%s cooldown not expired, skipping", prefs.user_id)
                        continue
                    user = User.get_by_id(prefs.user_id)
                    if not user or not user.email:
                        logger.debug("notify_motion_capture: user_id=%s has no email, skipping", prefs.user_id)
                        continue
                    subject = "SecuryPi: Motion detected"
                    body = (
                        "Motion was detected by your SecuryPi camera.\n\n"
                        "You can review it in the Recordings section of your SecuryPi."
                    )
                    send_email_async(user.email, subject, body)
                    logger.info("notify_motion_capture: sent to %s", user.email)
                    prefs.update_last_sent("motion")
        except Exception as e:
            logger.error("notify_motion_capture failed: %s", e)

    Thread(target=_run, daemon=True).start()


def notify_sensor_thresholds(app, measurements):
    """
    Check each user's sensor thresholds against the given measurements
    and send email alerts where thresholds are exceeded and cooldown has expired.

    measurements: dict with keys "temperature", "humidity", "pressure" (float | None)
    Opens its own app context — safe to call from background threads.
    """
    def _run():
        try:
            with app.app_context():
                from securypi_app.models.notification_prefs import NotificationPrefs
                from securypi_app.models.user import User

                all_prefs = NotificationPrefs.fetch_all()

                metric_map = [
                    ("temperature", "temp", "temp_lower", "temp_upper", "temp_enabled"),
                    ("humidity",    "humidity", "humidity_lower", "humidity_upper", "humidity_enabled"),
                    ("pressure",    "pressure", "pressure_lower", "pressure_upper", "pressure_enabled"),
                ]

                for prefs in all_prefs:
                    user = User.get_by_id(prefs.user_id)
                    if not user or not user.email:
                        continue

                    for meas_key, cooldown_key, lower_attr, upper_attr, enabled_attr in metric_map:
                        if not getattr(prefs, enabled_attr, False):
                            continue

                        value = measurements.get(meas_key)
                        if value is None:
                            continue

                        lower = getattr(prefs, lower_attr)
                        upper = getattr(prefs, upper_attr)
                        if lower is None and upper is None:
                            continue

                        exceeded = (
                            (lower is not None and value < lower) or
                            (upper is not None and value > upper)
                        )
                        if not exceeded:
                            continue

                        if not prefs.is_cooldown_expired(cooldown_key):
                            logger.debug("notify_sensor_thresholds: user_id=%s %s cooldown not expired", prefs.user_id, meas_key)
                            continue

                        subject = f"SecuryPi: {meas_key.capitalize()} alert"
                        body = _threshold_body(meas_key, value, lower, upper)
                        send_email_async(user.email, subject, body)
                        logger.info("notify_sensor_thresholds: sent %s alert to %s", meas_key, user.email)
                        prefs.update_last_sent(cooldown_key)
        except Exception as e:
            logger.error("notify_sensor_thresholds failed: %s", e)

    Thread(target=_run, daemon=True).start()


def _threshold_body(metric, value, lower, upper):
    lines = [f"Your SecuryPi has detected an out-of-range {metric} reading.\n"]
    lines.append(f"Current {metric}: {value}")
    if lower is not None:
        lines.append(f"Configured lower limit: {lower}")
    if upper is not None:
        lines.append(f"Configured upper limit: {upper}")
    lines.append("\nCheck your SecuryPi measurements page for details.")
    return "\n".join(lines)
