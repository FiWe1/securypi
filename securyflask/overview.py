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

from . import mycam


bp = Blueprint("overview", __name__)


@bp.route('/stream.mjpg')
def video_feed():
    """
    Video streaming route to the src attribute of an img tag.
    Uses a generator function to stream the response.
    Calls mycam, a picamera2 wrapper class contained in mycam.py
    """
    global camera
    
    output = mycam.StreamingOutput()
    
    camera = mycam.MyPicamera2()
    camera.configureAndStartStream(output)
           
    return Response(mycam.generate_frames(output),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route("/stop_camera", methods=["POST"])
def stop_camera():
    global camera
    if camera is not None:
        try:
            camera.stop_recording()
            camera.close()
        except Exception as e:
            print(f"Error stopping camera: {e}")
        finally:
            camera = None
    return ("Camera stopped", 200)
    

@bp.route("/")
def index():
    """Render overview page with camera feed."""
    return render_template("overview/stream.html")