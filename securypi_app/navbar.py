from flask import url_for
from securypi_app.auth import is_logged_in_admin


def inject_nav_links():
    """
    Returns a dictionary with navigation links for the navbar.
    Used as a context processor in the Flask app to make nav_links
    available in all templates.
    """
    main_nav_links = [
        ("Overview", url_for("overview.index")),
        ("Temperature", url_for("temp_history.index")),
        ("Camera", url_for("camera_control.index")),
        ("Recordings", url_for("recordings.index"))
    ]
    bottom_nav_links = [
        ("Account", url_for("account.index")),
        ("Logout", url_for("auth.logout"))
    ]
    
    if is_logged_in_admin():
        bottom_nav_links.insert(0, ("Settings", url_for("settings.index")))
    
    return {"main_nav_links": main_nav_links,
            "bottom_nav_links": bottom_nav_links}
