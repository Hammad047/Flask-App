#This file contains the APIs that I created to solve the problem.

from app.tables import user_data, car_data
import urllib
import requests
import json
from app import app, db
from flask import request


#By using this you can signup and create an account which will be stored in "users" table 
@app.route('/user/signup', methods=['POST'])
def signup():
    if request.method == 'POST': 
        data = request.get_json() #getting data from POSTMAN
        username = data['username'] #get username
        name = data['name']  #get name
        email = data['email']  #get email
        password = data['password'] #get password
        adddata = user_data(username, name, email, password) #Passing to the user_data 
        adddata.create() #Here calling create functing to store the data in table.
    return 'Congratulation! You have signed-up succesfully.'


#By using this user can login by providing email and password which they entered during signup process.
@app.route('/user/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        data = request.get_json() #get data from postman
        email = data['email']  #get email
        password = data['password']  #get password
        userdata = db.session.query(user_data).filter_by(email=email, password=password).first() #This query will help us to search data from users table.  
        if not userdata: #if no record found
            return 'Warning! Invalid email or password'
    return f' Hi {userdata.user}' #if record found
    
#By using this user can create a dataset using the url given, this link is available in "contstants.py" file
@app.route('/dataset/createdataset', methods=['GET'])
def createdataset():
    where = urllib.parse.quote_plus("""
    {
        "Year": {
            "$lt": 2032
        }
    }
    """)
    url = 'https://parseapi.back4app.com/classes/Car_Model_List?limit=10'
    headers = {
    'X-Parse-Application-Id': 'hlhoNKjOvEhqzcVAJ1lxjicJLZNVv36GdbboZj3Z', 
    'X-Parse-Master-Key': 'SNMJJF0CZZhTPhLDIqGhTlUNV9r60M2Z5spyWfXW'
    }
    response = json.loads(
        requests.get(url, headers=headers).content.decode('utf-8'))
    list_models = []
    for data in response['results']:
        if data.get('Make') not in list_models:
            list_models.append(data.get('Make'))
            #Searching Based on "Make"
            url = 'https://parseapi.back4app.com/classes/Car_Model_List_{}?limit=10&order=Year&where=%s'.format(data.get("Make")) #Query to get 
            url = url % where
            print(url)
            records = json.loads(
                requests.get(url, headers=headers).content.decode('utf-8'))
            for record in records['results']: 
                obj = db.session.query(car_data).filter_by(object_id=record['objectId']).first()
                if not obj and record['Year'] >= 2012 and record['Year'] <= 2022: #If Year >= 2012 and <= 2022
                    #storing in cars table
                    adddata = car_data(record['objectId'], record['Year'], record['Make'], record['Model'], record['Category'], record['createdAt'], record['updatedAt'])
                    adddata.create()
    return "Car registration record has been created in database"

#By using this user can search the car registration report using "make" and "year"
@app.route('/search/<make>/<year>', methods=['GET'])
def search_my(make, year):
    db_data = db.session.query(car_data).filter_by(make=make,year=int(year)).first() #This query will help us to search data from cars table.  
    if not db_data: #if no record found
        return "Car not found"
    return db_data.display() #if record found

#By using this user can search the car registration report using "make" and "model"
@app.route('/searchby/<make>/<model>', methods=['GET'])
def search_mm(make, model):
    db_data = db.session.query(car_data).filter_by(make=make,model=model).first() #This query will help us to search data from cars table.  
    if not db_data: #if no record found
        return "Car not found" 
    return db_data.display() #if record found

