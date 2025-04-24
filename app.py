import os
import traceback
import requests
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-for-development')

# ✅ Supabase API URL and API Key
SUPABASE_API_URL = "https://ipjwyakptfzyxpdjnsfs.supabase.co/rest/v1"  # Supabase API URL
SUPABASE_API_KEY = "your-anon-key-here"  # Replace with your Supabase anon API key

# Headers for Supabase API authentication
headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

# ✅ Main Route to Show the Form
@app.route('/', methods=['GET', 'POST'])
def school_form():
    if request.method == 'POST':
        try:
            # Get form data from the HTML form
            district = request.form['district']
            school = request.form['school']
            udise = request.form['udise']
            classrooms = int(request.form['classrooms'])
            benches = int(request.form['benches'])

            # Collect class data for 6th to 12th grade
            class_data = {}
            for i in range(6, 13):
                boys = int(request.form.get(f'boys{i}', 0))
                girls = int(request.form.get(f'girls{i}', 0))
                total = boys + girls  # Calculate total students in each class
                class_data[f'Class {i}'] = {'boys': boys, 'girls': girls, 'total': total}

            # Prepare data to be sent to Supabase API
            submission_data = {
                "district": district,
                "school": school,
                "udise_code": udise,
                "classrooms": classrooms,
                "benches": benches,
                "class_data": class_data,  # Class data for each grade
                "timestamp": datetime.utcnow().isoformat()  # Timestamp when the data is submitted
            }

            # Make POST request to Supabase API to insert data into the table
            response = requests.post(
                f"{SUPABASE_API_URL}/school_infra_form",  # Supabase table endpoint
                headers=headers,
                json=submission_data  # Data will be sent as JSON
            )

            # Log the response for debugging
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            # If the POST request is successful, redirect to the thank you page
            if response.status_code == 201:
                print("✅ Data submitted successfully to Supabase.")
                return redirect(url_for('thank_you'))  # Redirect to thank_you page after successful submission
            else:
                print(f"❌ Error: {response.text}")
                return "Something went wrong. Please try again."

        except Exception as e:
            # Catch exceptions and print them
            print("❌ Error during submission:", e)
            traceback.print_exc()
            return "Something went wrong. Check your inputs and try again."

    return render_template('school_form.html')  # Render the form template for GET request

# ✅ Thank You Route
@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')  # Redirect to the thank you page

# ✅ Run the app
if __name__ == '__main__':
    try:
        app.run(debug=True)  # Run the app in debug mode for development
    except Exception as e:
        print("❌ Failed to start Flask app:")
        traceback.print_exc()
