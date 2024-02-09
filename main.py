import logging
from flask import Flask, abort, request
import cadquery as cq

from model3d_file import Model3DFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def convert():
    try:
        uploaded_file = request.files['file']
        file = Model3DFile(uploaded_file.filename, uploaded_file.stream.read, '.tmp')
        del file
        return 'File converted successfully'
    except Exception as e:
        logger.error("Unhandled exception: %s", e)
        abort(500, 'Internal server error')
    

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0', use_reloader=False)