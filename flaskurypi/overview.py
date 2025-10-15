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

from .sensors import mycam
from .sensors import temphum

### Globals ###
bp = Blueprint("overview", __name__)
camera = None # Shared camera instance


def get_camera():
    """Get or initialize the shared camera instance."""
    global camera
    if camera is None:
        camera = mycam.MyPicamera2()
    elif camera.started:
        camera.stop()
    return camera


@bp.route('/stream.mjpg')
def video_feed():
    """
    Video streaming route to the src attribute of an img tag.
    Uses a generator function to stream the response.
    Calls mycam, a picamera2 wrapper class contained in mycam.py
    """
    global camera
    camera = get_camera()
    
    output = mycam.StreamingOutput()
    
    camera.configureAndStartStream(output)
           
    return Response(mycam.generate_frames(output),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/picture.jpg')
def picture_feed():
    """Route for a single snapshot."""
    
    global camera
    camera = get_camera()
    
    try:
        jpeg_data = camera.configureAndTakePicture()
        
        return Response(jpeg_data, mimetype='image/jpeg')
    except Exception as e:
        print(f"Error capturing picture: {e}")
        # Return a simple error response or default image
        return Response(status=500)


@bp.route("/stop_camera", methods=["POST"])
def stop_camera():
    """Route to stop the camera and release resources.
       camera <- None
    """
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
    """Main overview page showing either live stream or snapshot based on mode.
       Also displays temperature and humidity readings.
    """
    
    # Get the desired mode from the request (default to 'picture')
    mode = request.args.get('mode', 'picture')
    
    # temperature and humidity sensor
    temperature_unit = 'C'
    temperature, humidity = temphum.measure_temp_hum(temperature_unit=temperature_unit)

    # Determine the template and URL for the <img> tag based on the mode
    if mode == 'stream':
        img_src = url_for('overview.video_feed')
    else: # Default is 'picture'
        img_src = url_for('overview.picture_feed')
    
    return render_template("overview/index.html", mode=mode, img_src=img_src, temperature=temperature, humidity=humidity, temperature_unit=temperature_unit)    