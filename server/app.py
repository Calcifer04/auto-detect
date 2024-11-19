from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from carIdentifier import identify_car

app = Flask(__name__)
CORS(app)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/identify-car', methods=['POST'])
def identify_car_endpoint():
    image_path = None
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        image = request.files['image']
        if image.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}_{image.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save the uploaded file
        image.save(image_path)
        print(f"Processing image: {image_path}")
        
        # Process the image
        result = identify_car(image_path)
        
        if result is None:
            return jsonify({"error": "Could not process image"}), 400
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
        
    finally:
        # Clean up the original uploaded file
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Warning: Could not remove temporary file: {e}")

if __name__ == '__main__':
    app.run(debug=True)
