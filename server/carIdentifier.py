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
            
            # Extract and print titles
            print("\nExtracted Titles:")
            print("----------------")
            for tag in json_response.get('tags', []):
                for action in tag.get('actions', []):
                    if 'displayName' in action:
                        print(f"- {action['displayName']}")
                        
            return json_response
        else:
            print(f"Bing search error: {response.status_code}, {response.text}")
            return None

def extract_keywords(titles):
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
    return most_common_keywords


def predict_car_model(common_keywords):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    keyword_counts = [f"{keyword} ({count} occurrences)" for keyword, count in common_keywords]
    
    prompt = (
        "You are a car identification expert. Analyze these keywords and their frequencies from image analysis:\n\n"
        f"Keywords by frequency:\n{', '.join(keyword_counts)}\n\n"
        "Important: Give more weight to keywords that appear more frequently. "
        "Words with higher occurrence counts are more likely to be significant identifiers of the vehicle.\n\n"
        "Based on this frequency analysis, identify the most likely vehicle and provide details in this exact format:\n"
        "Make and Model: [car make and model]\n"
        "Price Range: [price range in USD]\n"
        "Horsepower: [hp value]\n"
        "Top Speed: [speed in kph]\n"
        "Units Made: [total production numbers]\n"
        "Fun Fact: [interesting fact about the car]"
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
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
            'price_range': '',
            'horsepower': '',
            'top_speed': '',
            'units_made': '',
            'fun_fact': ''
        }
        
        lines = response_text.split('\n')
        
        for line in lines:
            if 'Make and Model:' in line:
                result['make_model'] = line.split('Make and Model:')[1].strip()
            elif 'Price Range:' in line:
                result['price_range'] = line.split('Price Range:')[1].strip()
            elif 'Horsepower:' in line:
                result['horsepower'] = line.split('Horsepower:')[1].strip()
            elif 'Top Speed:' in line:
                result['top_speed'] = line.split('Top Speed:')[1].strip()
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

def get_ranked_cars(car_boxes, image_width, image_height, min_size_ratio=0.01):
    """Rank detected car boxes based on multiple criteria."""
    ranked_boxes = []
    
    for box in car_boxes:
        x1, y1, x2, y2 = map(int, box)
        
        # Calculate box dimensions and metrics
        box_width = x2 - x1
        box_height = y2 - y1
        box_area = box_width * box_height
        aspect_ratio = box_width / box_height
        
        # Calculate relative size compared to image
        relative_size = box_area / (image_width * image_height)
        
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
            print(f"Detection: area={box_area}, aspect={aspect_ratio:.2f}, "
                  f"relative_size={relative_size:.3f}, center_score={center_score:.2f}, "
                  f"final_score={score:.2f}, position=({center_x:.2f}, {center_y:.2f})")
    
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
        print(f"Starting analysis of uploaded image: {image_path}")
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
            results = model(temp_path, conf=0.3)
            if not results:
                print("YOLO detection returned no results")
                return {"error": "Could not perform car detection"}
            
            # Get all detected cars and save individual crops
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
                            box_width = x2 - x1
                            box_height = y2 - y1
                            cropped = img.crop((x1, y1, x2, y2))
                            debug_path = os.path.join(debug_dir, f"car_detection_{i}_w{box_width}_h{box_height}.jpg")
                            cropped.save(debug_path)
                            print(f"Saved debug crop {i}: {debug_path}")
                            print(f"Dimensions: {box_width}x{box_height}, Aspect ratio: {box_width/box_height:.2f}")

            search_path = temp_path
            if car_boxes:
                # Get all cars ranked primarily by size (reduced min_size_ratio)
                ranked_cars = get_ranked_cars(car_boxes, img_width, img_height, min_size_ratio=0.01)
                
                # Take the highest scored (largest) car that meets minimum requirements
                for car_box, score in ranked_cars:
                    with Image.open(temp_path) as img:
                        x1, y1, x2, y2 = map(int, car_box)
                        # Minimal margins
                        margin_x = int((x2 - x1) * 0.02)
                        margin_y = int((y2 - y1) * 0.02)
                        x1 = max(0, x1 - margin_x)
                        y1 = max(0, y1 - margin_y)
                        x2 = min(img_width, x2 + margin_x)
                        y2 = min(img_height, y2 + margin_y)
                        
                        cropped_img = img.crop((x1, y1, x2, y2))
                        
                        # Very minimal size requirements
                        min_width = 50
                        min_height = 50
                        
                        if cropped_img.size[0] >= min_width and cropped_img.size[1] >= min_height:
                            cropped_path = os.path.join(temp_dir, f"cropped_{os.path.basename(image_path)}")
                            cropped_img.save(cropped_path)
                            search_path = cropped_path
                            print(f"Created cropped image at: {cropped_path}")
                            break
                
                if search_path == temp_path:
                    print("No car detections met the minimum size requirements")
            else:
                print("No car detected in image, using original image")

            # Use the original identify_car logic with the cropped image
            result = bing_visual_search(search_path)
            
            if result:
                titles = [image_info.get("name", "No title available")
                        for tag in result.get("tags", [])
                        for action in tag.get("actions", [])
                        if action["actionType"] in ["ImageSearch", "VisualSearch"]
                        for image_info in action.get("data", {}).get("value", [])]
                
                print("\nExtracted Titles:")
                print("----------------")
                for title in titles:
                    print(f"- {title}")

                if titles:
                    common_keywords = extract_keywords(titles)
                    
                    print("\nKeyword Counts:")
                    print("--------------")
                    for keyword, count in common_keywords:
                        print(f"{keyword}: {count} occurrences")

                    # Pass the full common_keywords list (with counts) to predict_car_model
                    prediction_text = predict_car_model(common_keywords)
                    if not prediction_text:
                        return {"error": "Could not generate prediction"}
                        
                    # Parse the structured response
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
