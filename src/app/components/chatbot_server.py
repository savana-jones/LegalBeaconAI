from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

responses = {
    "hi": "Hello! Welcome to Art Mingle. How can I assist you today?",
    "hello": "Hello! Welcome to Art Mingle. How can I assist you today?",
    "art prints": "Yes, we have a variety of AI generated images available for viewing.",
    "buy": "The AI generated artwork is not for sale, but feel free to explore our gallery!",
    "why aren't the paintings for sale": "Our focus is on showcasing AI creativity, not on selling artwork.",
    "commission piece": "Currently, we do not offer commission services for AI generated art.",
    "bye": "Thank you for visiting Art Mingle. If you have more questions, feel free to ask. Goodbye!",
    "what is AI art": "AI art is created using algorithms and artificial intelligence to generate unique images."
}

def get_bot_response(user_input):
    user_input = user_input.lower()
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    return "I'm not sure how to respond to that. Can you try asking something else?"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    print(f"Received message: {user_input}")  # Debug print
    response_text = get_bot_response(user_input)
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)