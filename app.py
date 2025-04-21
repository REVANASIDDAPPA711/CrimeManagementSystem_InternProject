
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# Connect to MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/crime_management_db"
mongo = PyMongo(app)

# Comprehensive Crime Data Dictionary
crime_data = {
    "Theft": {
        "types": {
            "Petty Theft": {"section": "IPC 378", "description": "Stealing low-value items.", "punishment": "Up to 1 year imprisonment or fine"},
            "Grand Theft": {"section": "IPC 378", "description": "Stealing high-value items.", "punishment": "Up to 3 years imprisonment or fine"},
            "Shoplifting": {"section": "IPC 378", "description": "Stealing from a store.", "punishment": "Up to 1 year imprisonment or fine"},
            "Auto Theft": {"section": "IPC 379", "description": "Stealing a vehicle.", "punishment": "Up to 7 years imprisonment and fine"},
            "Burglary Theft": {"section": "IPC 445", "description": "Stealing from a house break-in.", "punishment": "Up to 10 years imprisonment"},
            "Pickpocketing": {"section": "IPC 379", "description": "Stealing from someone's pocket.", "punishment": "Up to 3 years imprisonment"},
        }
    },
    "Assault": {
        "types": {
            "Simple Assault": {"section": "IPC 351", "description": "Causing harm without a weapon.", "punishment": "Up to 1 year imprisonment or fine"},
            "Aggravated Assault": {"section": "IPC 355", "description": "Causing serious harm or using a weapon.", "punishment": "Up to 7 years imprisonment"},
        }
    },
    "Fraud": {
        "types": {
            "Credit Card Fraud": {"section": "IPC 420", "description": "Using someone else's credit card without permission.", "punishment": "Up to 7 years imprisonment"},
            "Insurance Fraud": {"section": "IPC 420", "description": "Deceiving an insurance company.", "punishment": "Up to 10 years imprisonment"},
        }
    }
}

# Home Route - List all crimes
@app.route('/')
def index():
    crimes = list(mongo.db.crimes.find())  
    return render_template('list_crimes.html', crimes=crimes)

# Add a Crime
@app.route('/add', methods=['GET', 'POST'])
def add_crime():
    if request.method == 'POST':
        crime_category = request.form.get('crime_category')
        crime_type = request.form.get('crime_type')
        location = request.form.get('location')

        # Get crime details from dictionary
        crime_info = crime_data[crime_category]["types"].get(crime_type, {"section": "Unknown", "description": "No details available", "punishment": "Not defined"})

        mongo.db.crimes.insert_one({
            'crime_category': crime_category,
            'crime_type': crime_type,
            'location': location,
            'section': crime_info["section"],
            'description': crime_info["description"],
            'punishment': crime_info["punishment"]
        })
        return redirect(url_for('index'))

    return render_template('add_crime.html', crime_data=crime_data)

# View Crime Details
@app.route('/crime/<crime_id>')
def view_crime(crime_id):
    try:
        crime = mongo.db.crimes.find_one({'_id': ObjectId(crime_id)})
        if crime:
            return render_template('view_crime.html', crime=crime)
        else:
            return "Crime Not Found", 404
    except:
        return "Invalid Crime ID", 400

# Edit a Crime
@app.route('/edit/<crime_id>', methods=['GET', 'POST'])
def edit_crime(crime_id):
    crime = mongo.db.crimes.find_one({'_id': ObjectId(crime_id)})

    if request.method == 'POST':
        crime_category = request.form.get('crime_category')
        crime_type = request.form.get('crime_type')
        location = request.form.get('location')

        # Get new crime details from dictionary
        crime_info = crime_data.get(crime_category, {}).get("types", {}).get(crime_type, {
            "section": "Unknown", 
            "description": "No details available", 
            "punishment": "Not defined"
        })

        # Update MongoDB document
        mongo.db.crimes.update_one(
            {'_id': ObjectId(crime_id)},
            {'$set': {
                'crime_category': crime_category,
                'crime_type': crime_type,
                'location': location,
                'section': crime_info["section"],
                'description': crime_info["description"],
                'punishment': crime_info["punishment"]
            }}
        )
        return redirect(url_for('index'))

    return render_template('edit_crime.html', crime=crime, crime_data=crime_data)

# Delete a Crime
@app.route('/delete/<crime_id>')
def delete_crime(crime_id):
    mongo.db.crimes.delete_one({'_id': ObjectId(crime_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
