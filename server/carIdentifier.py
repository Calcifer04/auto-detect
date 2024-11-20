import requests
from dotenv import load_dotenv
import os
from collections import Counter
import re
import openai
from ultralytics import YOLO
from PIL import Image
import numpy as np


def bing_visual_search(image_path): 
    print(f"Starting Bing visual search with image: {image_path}")
    url = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
    headers = {"Ocp-Apim-Subscription-Key": os.getenv("BING_SEARCH_API_KEY")}
    
    with open(image_path, "rb") as image_file:
        files = {"image": image_file}
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            print("Bing search successful")
            json_response = response.json()
                        
            return json_response
        else:
            print(f"Bing search error: {response.status_code}, {response.text}")
            return None

def extract_keywords(titles):
    # Modified regex to ensure complete 4-digit years and count occurrences
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', ' '.join(titles))
    if years:
        year_counts = Counter(years)
        print("\nExtracted Years:")
        print("--------------")
        for year, count in year_counts.most_common():
            print(f"- {year}: {count} occurrences")
    
    # Use regex to split titles into words and normalize to lowercase
    words = []
    for title in titles:
        words.extend(re.findall(r'\b\w+\b', title.lower()))
    
    # Define a list of common stopwords to ignore
    stopwords = {"the", "a", "and", "in", "of", "for", "with", "to", "on", "new", "used"}
    filtered_words = [word for word in words if word not in stopwords]
    
    # Count keyword occurrences
    keyword_counts = Counter(filtered_words)
    
    # Get the most common keywords
    most_common_keywords = keyword_counts.most_common(10)
    
    # Print the most common keywords and their counts
    print("\nMost Common Keywords:")
    print("---------------------")
    for keyword, count in most_common_keywords:
        print(f"- {keyword}: {count} occurrences")
    
    return most_common_keywords


def predict_car_model(common_keywords, model_year=None):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    keyword_counts = [f"{keyword} ({count} occurrences)" for keyword, count in common_keywords]
    year_info = f"\nDetected Model Year: {model_year}" if model_year else ""
    
    prompt = (
        "You are a car identification expert. Analyze these keywords and their frequencies from image analysis:"
        f"{year_info}\n\n"
        f"Keywords by frequency:\n{', '.join(keyword_counts)}\n\n"
        "Important: Give more weight to keywords that appear more frequently. "
        "Words with higher occurrence counts are more likely to be significant identifiers of the vehicle.\n\n"
        "Based on this frequency analysis, identify the most likely vehicle and provide details in this exact format:\n"
        "Make and Model: [car make and model]\n"
        f"Model Year: {model_year if model_year else '[estimated year]'}\n"
        "Estimated Value: [value in USD]\n"
        "Horsepower: [bhp value] bhp ([kW value] kW)\n"
        "Top Speed: [speed in km/h]\n"
        "0-100 km/h: [acceleration in seconds] seconds\n"
        "Engine: [engine configuration, displacement, and type]\n"
        "Transmission: [transmission type and details]\n"
        "Fuel Consumption: [value in km/L and (L/100 km)]\n"
        "Weight: [value in kg]\n"
        "Units Made: [total production numbers]\n"
        "Fun Fact: [interesting fact about the car]"
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a car identification expert who analyzes keyword frequencies to identify vehicles. Higher frequency keywords should be given more weight in your analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error in GPT request: {e}")
        return None

def parse_gpt_response(response_text):
    try:
        result = {
            'make_model': '',
            'model_year': '',
            'estimated_value': '',
            'horsepower': '',
            'top_speed': '',
            'acceleration': '',
            'engine': '',
            'transmission': '',
            'fuel_consumption': '',
            'weight': '',
            'units_made': '',
            'fun_fact': ''
        }
        
        lines = response_text.split('\n')
        
        for line in lines:
            if 'Make and Model:' in line:
                result['make_model'] = line.split('Make and Model:')[1].strip()
            elif 'Model Year:' in line:
                result['model_year'] = line.split('Model Year:')[1].strip()
            elif 'Estimated Value:' in line:
                result['estimated_value'] = line.split('Estimated Value:')[1].strip()
            elif 'Horsepower:' in line:
                result['horsepower'] = line.split('Horsepower:')[1].strip()
            elif 'Top Speed:' in line:
                result['top_speed'] = line.split('Top Speed:')[1].strip()
            elif '0-100 km/h:' in line:
                result['acceleration'] = line.split('0-100 km/h:')[1].strip()
            elif 'Engine:' in line:
                result['engine'] = line.split('Engine:')[1].strip()
            elif 'Transmission:' in line:
                result['transmission'] = line.split('Transmission:')[1].strip()
            elif 'Fuel Consumption:' in line:
                result['fuel_consumption'] = line.split('Fuel Consumption:')[1].strip()
            elif 'Weight:' in line:
                result['weight'] = line.split('Weight:')[1].strip()
            elif 'Units Made:' in line:
                result['units_made'] = line.split('Units Made:')[1].strip()
            elif 'Fun Fact:' in line:
                result['fun_fact'] = line.split('Fun Fact:')[1].strip()
        
        return result
    except Exception as e:
        print(f"Error parsing GPT response: {e}")
        return None


def crop_car_image(image_path):
    """Crop the image to contain just the car using YOLOv8."""
    # Load the YOLO model
    model = YOLO('yolov8n.pt')
    
    # Create a copy of the original image for cropping
    original_img = Image.open(image_path)
    img_copy_path = f"{image_path.rsplit('.', 1)[0]}_copy.{image_path.rsplit('.', 1)[1]}"
    original_img.save(img_copy_path)
    
    # Perform detection on the copy
    results = model(img_copy_path)
    
    # Get the first detected car (class 2 in COCO dataset)
    car_boxes = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            if box.cls == 2:  # class 2 is 'car' in COCO
                car_boxes.append(box.xyxy[0].cpu().numpy())
    
    if not car_boxes:
        os.remove(img_copy_path)  # Clean up the copy
        return image_path  # Return original if no car detected
    
    # Get the first car detected
    box = car_boxes[0]
    
    # Load and crop image
    img = Image.open(img_copy_path)
    x1, y1, x2, y2 = map(int, box)
    cropped_img = img.crop((x1, y1, x2, y2))
    
    # Save cropped image
    crop_path = f"{image_path.rsplit('.', 1)[0]}_cropped.{image_path.rsplit('.', 1)[1]}"
    cropped_img.save(crop_path)
    
    # Clean up the copy
    os.remove(img_copy_path)
    
    return crop_path

def get_ranked_cars(car_boxes, image_width, image_height, min_size_ratio=0.005):
    """Rank detected car boxes based on multiple criteria."""
    ranked_boxes = []
    
    print("\nDetection Details:")
    print("----------------")
    
    for box in car_boxes:
        x1, y1, x2, y2 = map(int, box)
        
        # Calculate box dimensions and metrics
        box_width = x2 - x1
        box_height = y2 - y1
        box_area = box_width * box_height
        aspect_ratio = box_width / box_height
        relative_size = box_area / (image_width * image_height)
        
        print("Detection found:")
        print(f"- Size: {box_width}x{box_height} pixels")
        print(f"- Area: {box_area} pixels²")
        print(f"- Relative size: {relative_size:.3f}")
        print(f"- Aspect ratio: {aspect_ratio:.2f}")
        
        # Calculate centrality scores
        center_x = (x1 + x2) / 2 / image_width
        center_y = (y1 + y2) / 2 / image_height
        
        # Exponential penalty for distance from center
        center_score = np.exp(-2 * (abs(0.5 - center_x) + abs(0.5 - center_y)))
        
        # Adjust aspect ratio scoring to be more lenient
        aspect_score = 0
        if 1.0 <= aspect_ratio <= 3.0:  # Wider range for aspect ratios
            aspect_score = 1.0 - min(abs(1.8 - aspect_ratio) / 1.8, 1.0)
        
        # Enhanced size scoring - give more weight to larger objects
        size_score = min(relative_size * 10, 1.0)  # Increased multiplier
        
        # Adjusted weights to prioritize size and centrality
        score = (
            size_score * 0.4 +      # Size is very important
            center_score * 0.4 +    # Centrality is equally important
            aspect_score * 0.2      # Aspect ratio is less critical
        )
        
        # Lower the minimum size threshold
        if relative_size >= min_size_ratio:
            ranked_boxes.append((box, score))
            # print(f"Detection: area={box_area}, aspect={aspect_ratio:.2f}, "
            #       f"relative_size={relative_size:.3f}, center_score={center_score:.2f}, "
            #       f"final_score={score:.2f}, position=({center_x:.2f}, {center_y:.2f})")
    
    return sorted(ranked_boxes, key=lambda x: x[1], reverse=True)

def process_multiple_detections(image_path, ranked_cars, temp_dir):
    """Process multiple car detections and return the best candidates."""
    results = []
    
    with Image.open(image_path) as img:
        img_width, img_height = img.size
        
        for i, (car_box, score) in enumerate(ranked_cars[:3]):  # Process top 3 candidates
            x1, y1, x2, y2 = map(int, car_box)
            
            # Add dynamic margins based on detection size
            margin_x = int((x2 - x1) * 0.05)  # 5% margin
            margin_y = int((y2 - y1) * 0.05)
            
            # Ensure margins don't go outside image bounds
            x1 = max(0, x1 - margin_x)
            y1 = max(0, y1 - margin_y)
            x2 = min(img_width, x2 + margin_x)
            y2 = min(img_height, y2 + margin_y)
            
            cropped = img.crop((x1, y1, x2, y2))
            crop_path = os.path.join(temp_dir, f"car_candidate_{i}_score_{score:.2f}.jpg")
            cropped.save(crop_path)
            
            results.append({
                'path': crop_path,
                'score': score,
                'dimensions': (x2-x1, y2-y1),
                'aspect_ratio': (x2-x1)/(y2-y1)
            })
    
    return results

def identify_car(image_path):
    try:
        os.environ['YOLO_VERBOSE'] = 'False'
        
        with Image.open(image_path) as img:
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"temp_{os.path.basename(image_path)}")
            img.save(temp_path)
            img_width, img_height = img.size

        model_path = 'yolov8n.pt'
        if not os.path.exists(model_path):
            print(f"YOLO model not found at: {model_path}")
            return {"error": "Car detection model not found"}
            
        model = YOLO(model_path)
        
        try:
            results = model(temp_path, conf=0.2)
            if not results:
                print("YOLO detection returned no results")
                return {"error": "Could not perform car detection"}
            
            car_boxes = []
            debug_dir = os.path.join(temp_dir, "debug_crops")
            os.makedirs(debug_dir, exist_ok=True)
            
            for result in results:
                if not hasattr(result, 'boxes'):
                    continue
                boxes = result.boxes
                for i, box in enumerate(boxes):
                    if box.cls == 2:  # class 2 is 'car' in COCO
                        box_coords = box.xyxy[0].cpu().numpy()
                        car_boxes.append(box_coords)
                        # Save debug crop of each detected car
                        with Image.open(temp_path) as img:
                            x1, y1, x2, y2 = map(int, box_coords)
                            cropped = img.crop((x1, y1, x2, y2))
                            debug_path = os.path.join(debug_dir, f"car_detection_{i}.jpg")
                            cropped.save(debug_path)

            search_path = temp_path
            if car_boxes:
                ranked_cars = get_ranked_cars(car_boxes, img_width, img_height, min_size_ratio=0.005)
                
                # Save all detected car crops
                for i, (car_box, score) in enumerate(ranked_cars):
                    with Image.open(temp_path) as img:
                        x1, y1, x2, y2 = map(int, car_box)
                        margin_x = int((x2 - x1) * 0.02)
                        margin_y = int((y2 - y1) * 0.02)
                        x1 = max(0, x1 - margin_x)
                        y1 = max(0, y1 - margin_y)
                        x2 = min(img_width, x2 + margin_x)
                        y2 = min(img_height, y2 + margin_y)
                        
                        cropped_img = img.crop((x1, y1, x2, y2))
                        
                        min_width = 50
                        min_height = 50
                        
                        # Ensure all detected cars are saved
                        cropped_path = os.path.join(temp_dir, f"cropped_{i}_{os.path.basename(image_path)}")
                        cropped_img.save(cropped_path)
                        if i == 0 and cropped_img.size[0] >= min_width and cropped_img.size[1] >= min_height:
                            search_path = cropped_path
                
                if search_path == temp_path:
                    print("No car detections met the minimum size requirements")
            else:
                print("No car detected in image, using original image")

            result = bing_visual_search(search_path)
            
            if result:
                titles = [image_info.get("name", "No title available")
                        for tag in result.get("tags", [])
                        for action in tag.get("actions", [])
                        if action["actionType"] in ["ImageSearch", "VisualSearch"]
                        for image_info in action.get("data", {}).get("value", [])]
                
                if titles:
                    years = re.findall(r'\b(19\d{2}|20\d{2})\b', ' '.join(titles))
                    model_year = None
                    if years:
                        year_counts = Counter(years)
                        most_common_year = year_counts.most_common(1)[0][0]
                        model_year = most_common_year
                    
                    common_keywords = extract_keywords(titles)
                    
                    prediction_text = predict_car_model(common_keywords, model_year)
                    
                    if not prediction_text:
                        return {"error": "Could not generate prediction"}
                        
                    prediction = parse_gpt_response(prediction_text)
                    if not prediction:
                        return {"error": "Could not parse prediction"}
                        
                    return prediction
                else:
                    return {"error": "No related car images found."}
            else:
                return {"error": "No relevant information found."}

        except Exception as e:
            print(f"Error in YOLO detection: {str(e)}")
            return {"error": f"Car detection failed: {str(e)}"}

    except Exception as e:
        print(f"Error in identify_car: {str(e)}")
        return {"error": f"An error occurred while processing the image: {str(e)}"}
