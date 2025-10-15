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
    
    stop_camera() # This will ensure 'camera' is None if streaming was active
    
    camera = mycam.MyPicamera2()    
    camera.configureAndStartStream(output)
           
    return Response(mycam.generate_frames(output),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/picture.jpg')
def picture_feed():
    """Route for a single snapshot."""
    # Ensure no streaming camera is running before capturing a picture
    stop_camera() # This will ensure 'camera' is None if streaming was active
    
    try:
        temp_camera = mycam.MyPicamera2()
        jpeg_data = temp_camera.configureAndTakePicture()
        # The camera instance is short-lived and closed within configureAndTakePicture
        
        return Response(jpeg_data, mimetype='image/jpeg')
    except Exception as e:
        print(f"Error capturing picture: {e}")
        # Return a simple error response or default image
        return Response(status=500)


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
    if mode == 'live':
        img_src = url_for('overview.video_feed')
        return render_template("overview/stream.html", mode=mode, img_src=img_src)
    else: # Default is 'picture'
        img_src = url_for('overview.picture_feed')
        return render_template("overview/snapshot.html", mode=mode, img_src=img_src)