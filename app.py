import os
import traceback
import requests
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-for-development')

# Supabase API URL and API Key
SUPABASE_API_URL = "https://ipjwyakptfzyxpdjnsfs.supabase.co/rest/v1/school_infra_form"  # Supabase API URL
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlwand5YWtwdGZ6eXhwZGpuc2ZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU0MDk5NTEsImV4cCI6MjA2MDk4NTk1MX0.1LoGAdK7c34Kqh6s-jNL1sEr439cgrCf1zJwOhvs3fQ"  # Replace with your Supabase anon API key

# Headers for Supabase API authentication
headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# Store the form data temporarily
step_data = {}

# Define districts and corresponding schools (for dynamic loading)
district_data = {
    "District A": ["School A1", "School A2", "School A3"],
    "District B": ["School B1", "School B2"],
    "District C": ["School C1", "School C2", "School C3"]
}

# Step 1 Route (District, School, UDISE, Name, and Designation)
@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        # Get form data from step 1
        district = request.form['district']
        school = request.form['school']
        udise = request.form['udise']
        name = request.form['name']  # Get name from the form
        designation = request.form['designation']  # Get designation from the form
        
        # Validate UDISE Code (11 digits only)
        if len(udise) != 11:
            return "❌ UDISE code must be exactly 11 digits."
        
        step_data['district'] = district
        step_data['school'] = school
        step_data['udise'] = udise
        step_data['classrooms'] = int(request.form['classrooms'])
        step_data['benches'] = {}  # Initialize benches as an empty dictionary here
        step_data['name'] = name  # Store name in step_data
        step_data['designation'] = designation  # Store designation in step_data
        
        return redirect(url_for('step2'))  # Redirect to Step 2
    
    return render_template('step1.html', districts=district_data.keys())

# Step 2 Route (Number of Benches in each classroom)
@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if request.method == 'POST':
        # Store the number of benches per classroom as a dictionary
        step_data['benches'] = {
            f'classroom_{i}': int(request.form[f'classroom_{i}']) 
            for i in range(1, step_data['classrooms'] + 1)
        }
        
        return redirect(url_for('step3'))  # Redirect to Step 3
    
    return render_template('step2.html', classrooms=step_data['classrooms'], step_data=step_data)

# Step 3 Route (Students per class data for classes 6-12)
@app.route('/step3', methods=['GET', 'POST'])
def step3():
    # Ensure `name` is present in step_data
    if 'name' not in step_data:
        return redirect(url_for('step1'))  # If name is missing, redirect to Step 1
    
    # Initialize class_data if not already present
    if 'class_data' not in step_data:
        step_data['class_data'] = {f'Class {i}': {'boys': '', 'girls': '', 'total': ''} for i in range(6, 13)}

    if request.method == 'POST':
        class_data = {}
        for i in range(6, 13):
            boys = int(request.form.get(f'boys{i}', 0))
            girls = int(request.form.get(f'girls{i}', 0))
            total = boys + girls
            class_data[f'Class {i}'] = {'boys': boys, 'girls': girls, 'total': total}

        # Store student data
        step_data['class_data'] = class_data

        # After collecting all data, submit to Supabase
        submission_data = {
            "name": step_data['name'],  # Add name to submission data
            "designation": step_data['designation'],  # Add designation to submission data
            "district": step_data['district'],
            "school": step_data['school'],
            "udise_code": step_data['udise'],
            "classrooms": step_data['classrooms'],
            "benches": step_data['benches'],
            "class_data": class_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Send data to Supabase
        response = requests.post(
            SUPABASE_API_URL,  # Supabase table endpoint
            headers=headers,
            json=submission_data
        )

        if response.status_code == 201:
            return redirect(url_for('thank_you'))  # After successful submission
        else:
            return f"❌ Error: {response.text}"  # Display error if the request fails

    return render_template('step3.html', step_data=step_data)

# Step 4 Route (Thank You Page)
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/')
def index():
    return redirect(url_for('step1'))  # Redirect to the step1 form

# Run the app
if __name__ == '__main__':
    try:
        app.run(debug=True)  # Run the app in debug mode for development
    except Exception as e:
        print("❌ Failed to start Flask app:")
        traceback.print_exc()
