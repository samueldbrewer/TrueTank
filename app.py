import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/job-board')
def job_board():
    return render_template('job_board.html')

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'TrueTank'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)