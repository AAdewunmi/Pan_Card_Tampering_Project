from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import cv2
from skimage.metrics import structural_similarity as ssim

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def compare_images(original_path, tampered_path, result_path, side_by_side_path):
    import cv2
    import numpy as np
    from skimage.metrics import structural_similarity as ssim

    imageA = cv2.imread(original_path)
    imageB = cv2.imread(tampered_path)

    # Resize tampered image to match original
    if imageA.shape != imageB.shape:
        imageB = cv2.resize(imageB, (imageA.shape[1], imageA.shape[0]))

    # Check for color
    if len(imageA.shape) == 3 and imageA.shape[2] == 3:
        score, diff = ssim(imageA, imageB, full=True, channel_axis=-1)
        diff_gray = cv2.cvtColor((diff * 255).astype("uint8"), cv2.COLOR_BGR2GRAY)
    else:
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
        score, diff = ssim(grayA, grayB, full=True)
        diff_gray = (diff * 255).astype("uint8")

    # Threshold the difference image
    _, thresh = cv2.threshold(diff_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    cv2.imwrite(result_path, thresh)

    # Convert threshold to BGR
    diff_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    # Add borders with labels
    def add_border_with_label(img, label):
        # Map label to color
        color_map = {
            "Original": (50, 150, 255),     # Orange-Blue
            "Tampered": (0, 200, 0),        # Green
            "Differences": (0, 0, 255)      # Red
        }
        label_color = color_map.get(label, (0, 0, 0))

        # Add white border around image
        bordered = cv2.copyMakeBorder(img, 50, 10, 10, 10, cv2.BORDER_CONSTANT, value=(255, 255, 255))

        # Put label text at top
        cv2.putText(bordered, label, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, label_color, 2, cv2.LINE_AA)

        return bordered

    labeled_original = add_border_with_label(imageA, "Original")
    labeled_tampered = add_border_with_label(imageB, "Tampered")
    labeled_diff = add_border_with_label(diff_color, "Differences")

    # Stack all together
    comparison = cv2.hconcat([labeled_original, labeled_tampered, labeled_diff])
    cv2.imwrite(side_by_side_path, comparison)

    return score

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle Clear button
        if request.form.get('clear') == 'true':
            # Optionally delete old results
            for f in ['diff.png', 'comparison.png']:
                path = os.path.join(app.config['RESULT_FOLDER'], f)
                if os.path.exists(path):
                    os.remove(path)
            for f in os.listdir(app.config['UPLOAD_FOLDER']):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))

            return render_template('index.html')  # Render with no data

        # Handle normal submission
        original = request.files.get('original')
        tampered = request.files.get('tampered')

        if original and tampered:
            original_filename = secure_filename(original.filename)
            tampered_filename = secure_filename(tampered.filename)

            original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            tampered_path = os.path.join(app.config['UPLOAD_FOLDER'], tampered_filename)

            original.save(original_path)
            tampered.save(tampered_path)

            result_path = os.path.join(app.config['RESULT_FOLDER'], 'diff.png')
            side_by_side_path = os.path.join(app.config['RESULT_FOLDER'], 'comparison.png')

            score = compare_images(original_path, tampered_path, result_path, side_by_side_path)

            return render_template(
                'index.html',
                ssim_score=round(score, 4),
                result_image='static/results/diff.png',
                comparison_image='static/results/comparison.png',
                original_image=original_filename,
                tampered_image=tampered_filename
            )


if __name__ == '__main__':
    app.run(debug=True)

