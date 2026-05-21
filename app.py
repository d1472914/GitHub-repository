from app import create_app

app = create_app()

<<<<<<< D1483362
if __name__ == '__main__':
=======
if __name__ == "__main__":
>>>>>>> master
    app.run(debug=True, port=5000)
from dotenv import load_dotenv
import os
from app import create_app

# Load environment variables from .env if it exists
load_dotenv()

app = create_app()

if __name__  '__main__':
    # Run server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'True')  'True')

import os
from dotenv import load_dotenv
from app import create_app

<<<<<<< HEAD
# 優先載入 .env 中的環境變數
load_dotenv()
=======
app = Flask(__name__)
app.secret_key  'super_secret_key_for_development'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'habits.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b

# 使用 Flask 工廠模式建立應用程式實例
app = create_app()

<<<<<<< HEAD
if __name__ == '__main__':
    # 從環境變數讀取執行參數，或使用預設值
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    
    print(f"✨ 宿舍共好系統正在啟動... 網址: http://{host}:{port} (Debug={debug})")
    app.run(host=host, port=port, debug=debug)
=======
if __name__  '__main__':
    app.run(debug=True)

>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
