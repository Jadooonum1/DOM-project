from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os
import time

app = Flask(__name__, template_folder='templates')

# Load the trained model
def load_model(cryptocurrency):
    model_path = os.path.join('models', f'{cryptocurrency}_model.pkl')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        return model
    return None

@app.route('/')
def index():
    # Render the index.html file located in the 'templates' folder
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train():
    try:
        data = request.json
        if not data or 'cryptocurrency' not in data:
            return jsonify({'error': 'Invalid input data'}), 400
        
        cryptocurrency = data['cryptocurrency']
        # Train the model for the selected cryptocurrency
        from train_model import train_model
        train_model(cryptocurrency)
        return jsonify({"message": f"Model trained for {cryptocurrency}."}), 200
    
    except Exception as e:
        print(f"Error in training model: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data or 'cryptocurrency' not in data or 'days_since' not in data:
            return jsonify({'error': 'Invalid input data'}), 400
        
        cryptocurrency = data['cryptocurrency']
        days_since = data['days_since']

        # Load the model
        model = load_model(cryptocurrency)
        if model is None:
            return jsonify({'error': f'Model for {cryptocurrency} not found.'}), 400

        # Predict the price
        predicted_price = model.predict(np.array([[days_since]]))
        return jsonify({"predicted_price": predicted_price[0]})

    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
