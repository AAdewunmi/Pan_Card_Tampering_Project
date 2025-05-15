from app import app
from flask import render_template, request
import os
from skimage.metrics import structural_similarity
import imutils
import cv2
from PIL import Image
from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
import os
# Adding path to config
app.config['INITIAL_FILE_UPLOADS'] = 'app/static/uploads'
app.config['EXISTING_FILE'] = 'app/static/original'
app.config['GENERATED_FILE'] = 'app/static/generated'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Ensure this directory exists

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        image_file = request.files.get('image_upload')
        logo_file = request.files.get('logo_upload')
        watermark_text = request.form.get('text_mark')
        option = request.form.get('options')

        if image_file:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
            image_file.save(image_path)

        if option == 'logo_watermark' and logo_file:
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(logo_file.filename))
            logo_file.save(logo_path)
            # Process image + logo watermark here...

        elif option == 'text_watermark' and watermark_text:
            # Process image + text watermark here...
            pass

        # Redirect or return result image
        return render_template('index.html')  # Or return a page showing results

    return render_template('index.html')  # Initial GET request

# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True)
# This code is part of a Flask web application that allows users to upload
# an image of a PAN card and compare it with an existing image.
# It uses OpenCV and scikit-image to compute the Structural Similarity
# Index (SSI)
# between the two images and highlights any differences.
# The app saves the uploaded image, the original image, and the generated
# images (with differences highlighted) in specified directories.
# The app is designed to run in debug mode for development purposes.
# The code includes necessary imports, configuration settings, and the main
# function to run the Flask application.
# The app uses Flask's routing to handle GET and POST requests, and it renders
# an HTML template to display the results.
# The app is structured to handle image processing tasks, including resizing
# images, converting them to grayscale, and computing the SSI.
# The app also uses the imutils library to handle contours and bounding
# boxes for highlighting differences in the images.
