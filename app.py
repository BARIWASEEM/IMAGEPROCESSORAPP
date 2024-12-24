from flask import Flask, request, render_template, send_from_directory
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import os
import random

# Initialize Flask app
app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
FONT_FOLDER = 'fonts'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Ensure font exists (Place your 'arial.ttf' in the 'fonts/' folder)
FONT_PATH = os.path.join(FONT_FOLDER, "arial.ttf")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_images():
    # Get form data
    initial_timestamp = request.form.get('timestamp', datetime.now().strftime("%b %d, %Y at %I:%M:%S %p"))
    location = request.form.get('location', 'Default Location')
    uploaded_files = request.files.getlist('images')

    # Validate uploaded files
    if not uploaded_files or uploaded_files[0].filename == '':
        return "No files uploaded. Please try again.", 400

    # Parse timestamp
    try:
        timestamp_dt = datetime.strptime(initial_timestamp, "%b %d, %Y at %I:%M:%S %p")
    except ValueError:
        return "Invalid timestamp format. Use: Dec 28, 2024 at 8:07:32 PM", 400

    processed_files = []
    current_hour_folder = os.path.join(OUTPUT_FOLDER, datetime.now().strftime("%H"))
    os.makedirs(current_hour_folder, exist_ok=True)

    for uploaded_file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(file_path)

        # Process the image
        processed_file_name = process_image(file_path, current_hour_folder, timestamp_dt, location)
        processed_files.append(processed_file_name)

        # Increment timestamp randomly
        timestamp_dt += timedelta(seconds=random.randint(0, 60))

    # Return success message
    return f"Processed {len(processed_files)} images. Check the outputs folder."

def process_image(image_path, output_folder, timestamp_dt, location):
    """
    Process a single image: add timestamp and location, then save.
    """
    # Open the image
    image = Image.open(image_path)

    # Set up drawing context
    draw = ImageDraw.Draw(image)

    # Load font
    font_size = 130  # Adjust font size as needed
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Prepare text
    timestamp_str = timestamp_dt.strftime("%b %d, %Y at %I:%M:%S %p")
    text = f"{timestamp_str}\n{location}"

    # Determine text position (top-right corner)
    img_width, img_height = image.size
    margin = 15
    text_width, text_height = draw.textsize(text, font=font)
    text_x = img_width - text_width - margin
    text_y = margin

    # Add text to image
    draw.multiline_text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    # Save the processed image
    output_file_name = f"processed_{os.path.basename(image_path)}"
    output_path = os.path.join(output_folder, output_file_name)
    image.save(output_path)

    return output_file_name

@app.route('/download/<filename>')
def download_file(filename):
    """
    Endpoint to download a processed file.
    """
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
