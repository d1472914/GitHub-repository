from dotenv import load_dotenv
import os
from app import create_app

# Load environment variables from .env if it exists
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Run server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'True') == 'True')
