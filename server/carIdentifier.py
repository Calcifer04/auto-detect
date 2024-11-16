import requests
from dotenv import load_dotenv
import os
from collections import Counter
import re
import openai

def bing_visual_search(image_path): 
    url = "https://api.bing.microsoft.com/v7.0/images/visualsearch"
    headers = {"Ocp-Apim-Subscription-Key": os.getenv("BING_API_KEY")}
    
    with open(image_path, "rb") as image_file:
        files = {"image": image_file}
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
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

import openai

def predict_car_model(keywords):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Create a prompt with the extracted keywords
    prompt = (
        f"Based on the following keywords related to car images, estimate the possible car model: {', '.join(keywords)}."
        " Suggest a specific make and model if possible. Just give the make and model in your reply with estimated price, horsepower and a fun fact."
    )
    
    # Make an API request to OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Use an appropriate model like 'gpt-3.5-turbo' or 'gpt-4' if available
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.5
    )
    
    # Extract and return the prediction
    if response.choices:
        return response.choices[0].message['content'].strip()
    else:
        return "No prediction available."


def identify_car(image_path):
    result = bing_visual_search(image_path)
    
    if result:
        titles = [image_info.get("name", "No title available")
                for tag in result.get("tags", [])
                for action in tag.get("actions", [])
                if action["actionType"] in ["ImageSearch", "VisualSearch"]
                for image_info in action.get("data", {}).get("value", [])]
        
        if titles:
            common_keywords = extract_keywords(titles)
            keywords = [keyword for keyword, count in common_keywords]
            prediction = predict_car_model(keywords)

            # Initialize response data with default values
            response_data = {
                "make_model": "N/A",
                "price_range": "N/A",
                "horsepower": "N/A",
                "fun_fact": "N/A"
            }

            # Split the prediction text by lines and process each line
            lines = prediction.splitlines()
            
            # Capture the first line as make and model if it doesn’t start with a label
            if lines and "Make and Model:" not in lines[0] and "Estimated Price:" not in lines[0]:
                response_data["make_model"] = lines[0].strip()

            # Process remaining lines for other fields
            for line in lines:
                if "Make and Model:" in line:
                    response_data["make_model"] = line.split("Make and Model:")[1].strip()
                elif "Estimated Price:" in line:
                    response_data["price_range"] = line.split("Estimated Price:")[1].strip()
                elif "Horsepower:" in line:
                    response_data["horsepower"] = line.split("Horsepower:")[1].strip()
                elif "Fun Fact:" in line:
                    response_data["fun_fact"] = line.split("Fun Fact:")[1].strip()

            # Return the structured data
            return response_data
        else:
            return {"error": "No related car images found."}
    else:
        return {"error": "No relevant information found."}
