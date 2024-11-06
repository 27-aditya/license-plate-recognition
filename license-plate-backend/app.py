from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import easyocr
import re

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Preprocess the image to enhance it for license plate detection
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresholded = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresholded

# Detect license plate using contours
def detect_plate(image):
    processed_image = preprocess_image(image)
    contours, _ = cv2.findContours(processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            return image[y:y + h, x:x + w]
    return None

# Perform OCR on the detected plate
def recognize_plate(plate_img):
    if plate_img is not None:
        gray_plate = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        result = reader.readtext(gray_plate, detail=0)
        if result:
            return clean_text(result[0])
    return None

# Clean OCR results to remove non-alphanumeric characters
def clean_text(text):
    return "".join(re.split("[^a-zA-Z0-9]", text)).upper()

# Main pipeline to detect and recognize license plate
def license_plate_recognition(image):
    image_resized = cv2.resize(image, (400, 600))
    plate_image = detect_plate(image_resized)
    if plate_image is not None:
        plate_text = recognize_plate(plate_image)
        return plate_text if plate_text else "Could not recognize the license plate."
    return "License plate not detected."

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files.get('image')
    if file:
        # Convert the uploaded file to a NumPy array
        file_bytes = np.fromstring(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Process the image and extract the license plate number
        number = license_plate_recognition(image)
        return jsonify({'number': number})
    
    return jsonify({'error': 'No file uploaded'}), 400

if __name__ == '__main__':
    app.run(debug=True)
