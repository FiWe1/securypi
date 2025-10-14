from flask import Flask, Response, render_template_string
from flask import Blueprint
from flask import render_template
# from flask import flash
# from flask import g
# from flask import redirect
# from flask import request
# from flask import url_for
# from flask import current_app
# from werkzeug.exceptions import abort

from mycam import mycam, StreamingOutput, generate_frames


bp = Blueprint("overview", __name__)


@bp.route('/stream.mjpg')
def video_feed():
    """
    Video streaming route to the src attribute of an img tag.
    Uses a generator function to stream the response.
    Calls mycam, a picamera2 wrapper class contained in mycam.py
    """    
    output = mycam.StreamingOutput()
    
    camera = mycam.MyPicamera2()
    camera.configureAndStartStream(output)
           
    return Response(mycam.generate_frames(output),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
    
@bp.route("/")
def index():
    """Render overview page with camera feed."""
    return render_template("overview/index.html")