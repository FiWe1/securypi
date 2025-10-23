from flask import url_for
from flask import g


def inject_nav_links():
    """ Returns a dictionary with navigation links for the navbar.
        Used as a context processor in the Flask app to make nav_links
        available in all templates.
    """
    main_nav_links = [
        ("Overview", url_for("overview.index")),
        ("Temp History", url_for("temp_history.index")),
        ("Camera Control", url_for("camera_control.index")),
        ("Recordings", url_for("recordings.index"))
    ]
    bottom_nav_links = [
        ("Account", url_for("account.index")),
        ("Logout", url_for("auth.logout"))
    ]
    
    if g.user is not None and g.user["is_admin"] == 1:
        bottom_nav_links.insert(0, ("Settings", url_for("settings.index")))

    ##############################TODO: Add /hide settings for admin
    # getattr(g, "user", None)
    # if g.user.is_admin:
    #     links.append(("Admin", url_for("admin.index")))
    
    return {"main_nav_links": main_nav_links, "bottom_nav_links": bottom_nav_links}
