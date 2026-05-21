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
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key  'super_secret_key_for_development'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'habits.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 定義資料庫模型：室友生活習慣
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    bedtime = db.Column(db.String(20), nullable=False)
    ac_temp = db.Column(db.Float, nullable=False)
    light_noise = db.Column(db.String(100), nullable=False)
    smell_tolerance = db.Column(db.String(100), nullable=False)

# 初始化資料庫
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        bedtime = request.form.get('bedtime')
        ac_temp_str = request.form.get('ac_temp')
        light_noise = request.form.get('light_noise')
        smell_tolerance = request.form.get('smell_tolerance')
        
        try:
            ac_temp = float(ac_temp_str)
            # 儲存到資料庫
            new_habit = Habit(
                name=name, 
                bedtime=bedtime, 
                ac_temp=ac_temp,
                light_noise=light_noise,
                smell_tolerance=smell_tolerance
            )
            db.session.add(new_habit)
            db.session.commit()
            flash('你的生活習慣已成功儲存！', 'success')
            return redirect(url_for('index'))
        except ValueError:
            flash('冷氣溫度請輸入有效的數字。', 'danger')
            return redirect(url_for('index'))
            
    # 讀取所有室友的習慣
    habits = Habit.query.all()
    return render_template('index.html', habits=habits)

if __name__  '__main__':
    app.run(debug=True)

