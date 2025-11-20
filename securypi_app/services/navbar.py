from flask import url_for, request
from securypi_app.services.auth import is_logged_in_admin


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
        ("User settings", url_for("user_settings.index")),
        ("Logout", url_for("auth.logout"))
    ]
    if is_logged_in_admin():
        bottom_nav_links.insert(
            0, ("Configuration", url_for("configuration.index"))
        )

    return {
        "main_nav_links": main_nav_links,
        "bottom_nav_links": bottom_nav_links
    }


def inject_active_page():
    """ Return dictionary with the active page URL for context processor. """
    return {
        "active_page": url_for(request.endpoint)
    }
