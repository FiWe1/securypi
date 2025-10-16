from flask import url_for
from flask import g


def inject_nav_links():
    """ Returns a dictionary with navigation links for the navbar.
        Used as a context processor in the Flask app to make nav_links
        available in all templates.
    """
    links = [
        ("Overview", url_for("overview.index")),
        ("Temp History", url_for("temp_history")),
        ("Camera Control", url_for("camera_control")),
        ("Recordings", url_for("recordings")),
        ("Settings", url_for("settings")),
        ("Account", url_for("account"))
    ]

    ##############################TODO: Add admin link if user is admin
    # getattr(g, "user", None)
    # if g.user.is_admin:
    #     links.append(("Admin", url_for("admin.index")))
    
    return {"nav_links": links}
