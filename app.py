from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Mock system config
MIN_REQUIRED_VERSION = "2.0"

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/api/version', methods=['GET'])
def get_version():
    """
    Returns the minimum required version for the client to function properly.
    """
    return jsonify({
        "min_version": MIN_REQUIRED_VERSION
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
