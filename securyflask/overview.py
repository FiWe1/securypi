from flask import Flask, Response, render_template_string
from flask import Blueprint
from flask import render_template
# from flask import flash
# from flask import g
# from flask import redirect
from flask import request
from flask import url_for
# from flask import current_app
# from werkzeug.exceptions import abort

from . import mycam

### Globals ###
bp = Blueprint("overview", __name__)
camera = None


@bp.route('/stream.mjpg')
def video_feed():
    """
    Video streaming route to the src attribute of an img tag.
    Uses a generator function to stream the response.
    Calls mycam, a picamera2 wrapper class contained in mycam.py
    """
    global camera
    stop_recording() # This will stop recording if streaming was active
    camera = mycam.MyPicamera2()
    
    output = mycam.StreamingOutput()
    
    camera.configureAndStartStream(output)
           
    return Response(mycam.generate_frames(output),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/picture.jpg')
def picture_feed():
    """Route for a single snapshot."""
    global camera
    stop_camera() # This will stop recording if streaming was active, camera=None
    camera = mycam.MyPicamera2()
    
    try:
        jpeg_data = camera.configureAndTakePicture()
        # The camera instance is short-lived and closed within configureAndTakePicture
        
        return Response(jpeg_data, mimetype='image/jpeg')
    except Exception as e:
        print(f"Error capturing picture: {e}")
        # Return a simple error response or default image
        return Response(status=500)


def stop_recording():
    global camera
    if camera is not None:
        try:
            camera.stop_recording()
        except Exception as e:
            print(f"Error stopping camera: {e}")


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
    

@bp.route("/", methods=["GET"]) # Only need GET now
def index():
    """Render overview page with camera feed, handling mode switching."""
    
    # Get the desired mode from the request (default to 'picture')
    mode = request.args.get('mode', 'picture')
    
    # --- Remove POST handling block entirely ---

    # Determine the template and URL for the <img> tag based on the mode
    if mode == 'stream':
        img_src = url_for('overview.video_feed')
        return render_template("overview/stream.html", mode=mode, img_src=img_src)
    else: # Default is 'picture'
        img_src = url_for('overview.picture_feed')
        return render_template("overview/snapshot.html", mode=mode, img_src=img_src)