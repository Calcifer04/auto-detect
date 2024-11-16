from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Import backend functions
from carIdentifier import identify_car  # Adjust to your filename and function

app = Flask(__name__)
CORS(app)

@app.route('/identify-car', methods=['POST'])
def identify_car_endpoint():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image = request.files['image']
    image_path = os.path.join('./uploads', image.filename)
    image.save(image_path)

    # Run the identify_car function with the uploaded image
    result = identify_car(image_path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
