from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv  


load_dotenv(dotenv_path=".env")  

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: API Key is missing! Please set GEMINI_API_KEY in .env file.")

genai.configure(api_key=GEMINI_API_KEY)

def generate_response(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  
        response = model.generate_content(user_input)

        if response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "I couldn't generate a response. Please try again!"
    except genai.errors.ApiError as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    response_text = generate_response(user_input)
    return jsonify({"response": response_text})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK", "message": "Server is running!"}), 200

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500

if __name__ == "__main__":
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
