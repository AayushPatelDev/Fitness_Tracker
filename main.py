from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
GENDER = "male"
WEIGHT_KG = 80
HEIGHT_CM = 178
AGE = 20

APP_ID = os.getenv("API_ID")
API_KEY = os.getenv("API_KEY")
SPREAD_SHEET_URL = os.getenv("SPREAD_SHEET_URL")
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")

EXERCISE_API_URL = "https://trackapi.nutritionix.com/v2/natural/exercise"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track():
    try:
        exercise_text = request.form.get("exercise")
        
        if not exercise_text:
            return jsonify({"error": "Exercise text is required"}), 400

        if not all([APP_ID, API_KEY]):
            return jsonify({"error": "API credentials not configured"}), 500

        headers = {
            "Content-Type": "application/json",
            "x-app-id": APP_ID,
            "x-app-key": API_KEY
        }
        
        data = {
            "query": exercise_text,
            "gender": GENDER,
            "weight_kg": WEIGHT_KG,
            "height_cm": HEIGHT_CM,
            "age": AGE
        }
        
        # Call Nutritionix API
        response = requests.post(EXERCISE_API_URL, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        exercises = result.get("exercises", [])
        
        if not exercises:
            return jsonify({"message": "No exercises found"}), 404

        # Record exercises in spreadsheet
        todays_date = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%H:%M:%S")
        
        for exercise in exercises:
            sheet_inputs = {
                "workout": {
                    "date": todays_date,
                    "time": time_now,
                    "exercise": exercise["name"].title(),
                    "duration": exercise["duration_min"],
                    "calories": exercise["nf_calories"]
                }
            }
            
            try:
                sheet_response = requests.post(
                    SPREAD_SHEET_URL,
                    json=sheet_inputs,
                    auth=(USER_NAME, PASSWORD)
                )
                sheet_response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Failed to save to spreadsheet: {str(e)}")
                return jsonify({"error": "Failed to save workout"}), 500
        
        return jsonify(exercises)

    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return jsonify({"error": "Failed to process exercise"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
