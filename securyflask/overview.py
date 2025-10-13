from flask import Flask, Response, render_template_string
from flask import Blueprint
# from flask import flash
# from flask import g
# from flask import redirect
from flask import render_template
# from flask import request
# from flask import url_for
# from flask import current_app
# from werkzeug.exceptions import abort

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from threading import Condition
import io


bp = Blueprint("overview", __name__)



class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


def generate_frames():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n\r\n' +
               frame + b'\r\n')


@bp.route('/stream.mjpg')
def video_feed():
    global picam2, output
    
    output = StreamingOutput()
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
    picam2.start_recording(JpegEncoder(), FileOutput(output))
   
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
    
@bp.route("/")
def index():
    """Render overview page with camera feed."""
    return render_template("overview/index.html")