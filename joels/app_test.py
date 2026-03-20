# app_test.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    return jsonify({'success': True, 'message': 'Working!'})

if __name__ == '__main__':
    app.run(debug=True)