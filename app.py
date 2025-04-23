import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-for-development')

# ✅ Corrected: URL-encoded password
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234%40Strong@db.ipjwyakptfzyxpdjnsfs.supabase.co:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ School Infrastructure Model
class SchoolInfraForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    district = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(150), nullable=False)
    udise_code = db.Column(db.String(20), nullable=False)
    classrooms = db.Column(db.Integer, nullable=False)
    benches = db.Column(db.Integer, nullable=False)
    class_data = db.Column(JSON, nullable=False)

# ✅ Main Route
@app.route('/', methods=['GET', 'POST'])
def school_form():
    if request.method == 'POST':
        try:
            district = request.form['district']
            school = request.form['school']
            udise = request.form['udise']
            classrooms = int(request.form['classrooms'])
            benches = int(request.form['benches'])

            class_data = {}
            for i in range(6, 13):
                boys = int(request.form.get(f'boys{i}', 0))
                girls = int(request.form.get(f'girls{i}', 0))
                total = boys + girls
                class_data[f'Class {i}'] = {'boys': boys, 'girls': girls, 'total': total}

            submission = SchoolInfraForm(
                district=district,
                school=school,
                udise_code=udise,
                classrooms=classrooms,
                benches=benches,
                class_data=class_data
            )
            db.session.add(submission)
            db.session.commit()

            return redirect(url_for('school_form'))

        except Exception as e:
            print("❌ Error during submission:", e)
            return "Something went wrong. Check your inputs and try again."

    return render_template('school_form.html')

# ✅ Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
