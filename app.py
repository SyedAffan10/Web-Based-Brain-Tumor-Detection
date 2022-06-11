from __future__ import division, print_function
import numpy as np
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from flask import Flask, request, render_template, session, url_for
from werkzeug.utils import redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'mynameisaffanhussain'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'affan2244'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# Load your trained model
model = load_model(filepath='model/VGG_model.h5')

def model_predict(image_path, model):
  
  test_image = image.load_img(image_path, target_size = (224, 224))
  test_image = image.img_to_array(test_image)
  test_image = preprocess_input(test_image)
  test_image = np.expand_dims(test_image, axis=0)

  result = model.predict(test_image)
  print(result)

  if result[0][0] == 1:
    prediction = "Brain Tumor detected"
  else:
    prediction = "No Brain Tumor"
    
  return prediction


def preview():
  return render_template("preview.html")


@app.route('/predict', methods=['GET', 'POST'])
def upload():
  if request.method == 'POST':
    file = request.files['file']
    file_path = './images/'+file.filename
    file.save(file_path)

    prediction = model_predict(file_path, model)
    return prediction
  return None


@app.route('/', methods=['GET'])
def index():
  return render_template("index.html")


@app.route('/abstract', methods=['GET'])
def abstract():
  return render_template("abstract.html")
  

@app.route('/login', methods=['GET', 'POST'])
def login():
  msg = ''
  # Check if "username" and "password" POST requests exist (user submitted form)
  if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    # Create variables for easy access
    username = request.form['username']
    password = request.form['password']

    # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
    # Fetch one record and return result
    account = cursor.fetchone()

    # If account exists in accounts table in out database
    if account:
      # Create session data, we can access this data in other routes
      session['loggedin'] = True
      session['id'] = account['id']
      session['username'] = account['username']
      # Redirect to home page
      return render_template("preview.html")
      
    else:
      # Account doesnt exist or username/password incorrect
      msg = 'Incorrect username/password!'
  # Show the login form with message (if any)
  return render_template('login.html', msg=msg)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  # Output message if something goes wrong...
  msg = ''
  # Check if "username", "password" and "email" POST requests exist (user submitted form)
  if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
    # Create variables for easy access
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
    account = cursor.fetchone()

    # If account exists show error and validation checks
    if account:
      msg = 'Account already exists!'
    elif not re.match(r'^[a-z-0-9_.+-]+@[a-z-0-9-]+\.[a-z-0-9-.]+', email):
      msg = 'Invalid email address!'
    elif not re.match(r'[A-Za-z0-9]+', username):
      msg = 'Username must contain only characters and numbers!'
    elif not username or not password or not email:
      msg = 'Please fill out the form!'
    else:
      # Account doesnt exists and the form data is valid, now insert new account into accounts table
      cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
      mysql.connection.commit()
      msg = 'You have successfully registered!'
      return render_template('login.html', msg=msg)
  elif request.method == 'POST':
    # Form is empty... (no POST data)
    msg = 'Please fill out the form!'
  # Show registration form with message (if any)
  return render_template('signup.html', msg=msg)


@app.route('/logout', methods=['GET'])
def logout():
  # Remove session data, this will log the user out
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  # Redirect to login page
  return redirect(url_for('login'))

@app.route('/contact', methods=['GET'])
def contact():
  return render_template("contact.html")

@app.route('/patient', methods=['GET'])
def patient():
  return render_template("patient.html")

if __name__ == '__main__':
    app.run(debug=True)