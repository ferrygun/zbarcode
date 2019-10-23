#Usage: python app.py
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify,json
from werkzeug import secure_filename 
import numpy as np
import argparse
import imutils
import cv2
import time
import uuid
import base64

from pyzbar import pyzbar

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG'])

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def template_test():
    return render_template('template.html', label='', imagesource='../uploads/template.jpg')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        import time
        start_time = time.time()
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            image = cv2.imread(file_path)
            print(file_path)
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            frame = imutils.resize(image_gray, width=image.shape[1])

            barcodes = pyzbar.decode(frame)

            barcodeList = []

			# loop over the detected barcodes
            for barcode in barcodes:
			    # extract the bounding box location of the barcode and draw the
	            # bounding box surrounding the barcode on the image
	            #(x, y, w, h) = barcode.rect
	            #cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 10)
 
	            # the barcode data is a bytes object so if we want to draw it on
	            # our output image we need to convert it to a string first
	            barcodeData = barcode.data.decode("utf-8")
	            barcodeType = barcode.type
 
	            # draw the barcode data and barcode type on the image
	            #text = "{} ({})".format(barcodeData, barcodeType)
	            #cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,	0.5, (0, 0, 255), 2)
 
	            # print the barcode type and data to the terminal
	            print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
	            empDict = {'barcodeType': barcodeType, 'barcodeData': barcodeData }
	            barcodeList.append(empDict)
 
 
            filename = my_random_string(6) + filename
            cv2.imwrite(filename, image)
            label = jsonStr = json.dumps(barcodeList)

            os.rename(file_path, os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("--- %s seconds ---" % str (time.time() - start_time))
            
            return render_template('template.html', label=label, imagesource='../uploads/' + filename)
        else:
            return render_template('template.html', label='', imagesource='../uploads/template.jpg')

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

from werkzeug import SharedDataMiddleware
app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

if __name__ == "__main__":
    app.debug=False
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)