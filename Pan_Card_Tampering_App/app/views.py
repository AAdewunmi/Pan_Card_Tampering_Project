from app import app
from flask import render_template, request
import os
from skimage.metrics import structural_similarity
import imutils
import cv2
from PIL import Image

# Adding path to config
app.config['INITIAL_FILE_UPLOADS'] = 'app/static/uploads'
app.config['EXISTING_FILE'] = 'app/static/original'
app.config['GENERATED_FILE'] = 'app/static/generated'


# Route to home page
@app.route('/', methods=['GET', 'POST'])
def index():
    # Execute if request is GET
    if request.method == 'GET':
        return render_template('index.html')
    # Execute if request is POST
    if request.method == 'POST':
        # Get the uploaded image
        file_upload = request.files['file_upload']
        filename = file_upload.filename
        # Resize and save the uploaded image
        uploaded_image = Image.open(file_upload).resize((250, 160))
        uploaded_image.save(
            os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg')
        )

        # Resize and save the original image to ensure both uploaded and
        # original images match in size
        original_image = Image.open(
            os.path.join(app.config['EXISTING_FILE'], 'image.jpg')
        ).resize((250, 160))
        original_image.save(
            os.path.join(app.config['EXISTING_FILE'], 'image.jpg')
        )

        # Read uploaded and original images as arrays
        original_image = cv2.imread(
            os.path.join(app.config['EXISTING_FILE'], 'image.jpg')
        )
        uploaded_image = cv2.imread(
            os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.jpg')
        )

        # Convert images to grayscale
        original_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        uploaded_gray = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2GRAY)

        # Compute the Structural Similarity Index (SSI)
        (score, diff) = structural_similarity(
            original_gray, uploaded_gray, full=True
        )
        diff = (diff * 255).astype("uint8")

        # Calculate threshold and contours
        threshold = cv2.threshold(
            diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )[1]
        cnts = cv2.findContours(
            threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cnts = imutils.grab_contours(cnts)

        # Draw contours on image
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(
                original_image, (x, y), (x + w, y + h), (0, 255, 0), 2
            )
            cv2.rectangle(
                uploaded_image, (x, y), (x + w, y + h), (0, 255, 0), 2
            )

        # Save all output images
        cv2.imwrite(
            os.path.join(app.config['GENERATED_FILE'], 'image_original.jpg'),
            original_image
        )
        cv2.imwrite(
            os.path.join(app.config['GENERATED_FILE'], 'image_uploaded.jpg'),
            uploaded_image
        )
        cv2.imwrite(
            os.path.join(app.config['GENERATED_FILE'], 'image_diff.jpg'),
            diff
        )
        cv2.imwrite(
            os.path.join(app.config['GENERATED_FILE'], 'image_thresh.jpg'),
            threshold
        )
        prediction = str(round(score * 100, 2)) + '%' + ' correct'
        return render_template(
            'index.html',
            pred=prediction,
            filename=filename
        )


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
