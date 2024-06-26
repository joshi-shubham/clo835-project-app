from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import boto3
from os import listdir
from os.path import isfile, join

def download_file(file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    print(file_name)
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )
    s3 = boto3.resource('s3')
    # os.makedirs("./downloads")
    output = f"static/{file_name}"
    print(f"the file path is ", output)
    app.logger.info("the file path is %s ", output)
    s3.Bucket(bucket).download_file(file_name, output)

    return output

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
IMAGE_FROM_ENV = os.environ.get('APP_IMAGE') or "lime"
DBPORT = int(os.environ.get("DBPORT"))
BUCKET = os.environ.get("BUCKET")
aws_access_key_id=os.environ.get("aws_access_key_id")
aws_secret_access_key=os.environ.get("aws_secret_access_key")
aws_session_token=os.environ.get("aws_session_token")

download_file(file_name=IMAGE_FROM_ENV, bucket=BUCKET)
imgPath = "/static/"+IMAGE_FROM_ENV
# Create a connection to the MySQL database
db_conn = connections.Connection(
    host= DBHOST,
    port=DBPORT,
    user= DBUSER,
    password= DBPWD, 
    db= DATABASE
    
)
output = {}
table = 'employee';

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}
download_file(file_name=IMAGE_FROM_ENV, bucket=BUCKET)

# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])


@app.route("/", methods=['GET', 'POST'])
def home():
    if os.path.exists(imgPath):
        print("Image exists at", imgPath)
    else:
        print("Image does not exist at", imgPath)
        download_file(file_name=IMAGE_FROM_ENV, bucket=BUCKET)
    return render_template('addemp.html', imagePath=imgPath)

@app.route("/about", methods=['GET','POST'])
def about():
    if os.path.exists(imgPath):
        print("Image exists at", imgPath)
    else:
        print("Image does not exist at", imgPath)
        download_file(file_name=IMAGE_FROM_ENV, bucket=BUCKET)
    return render_template('about.html', imagePath=imgPath)
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    if os.path.exists(imgPath):
        print("Image exists at", imgPath)
    else:
        print("Image does not exist at", imgPath)
        download_file(file_name=IMAGE_FROM_ENV, bucket=BUCKET)
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

  
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, imagePath=imgPath)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    if os.path.exists(imgPath):
        print("Image exists at", imgPath)
    else:
        print("Image does not exist at", imgPath)
        download_file(file_name=IMAGE_FROM_ENV, bucket=BUCKET)
    return render_template("getemp.html", imagePath=imgPath)


@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    if os.path.exists(imgPath):
        print("Image exists at", imgPath)
    else:
        print("Image does not exist at", imgPath)
        download_file(file_name=IMAGE_FROM_ENV, bucket=BUCKET)
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], imagePath=imgPath)

if __name__ == '__main__':
    
    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if IMAGE_FROM_ENV:
            print("A Image was set through environment variable -" + IMAGE_FROM_ENV + ". However, Image from command line argument takes precendence.")
    elif IMAGE_FROM_ENV:
        print("No Command line argument. Image from environment variable =" + IMAGE_FROM_ENV)
        COLOR = IMAGE_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    # if COLOR not in color_codes:
    #     print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
    #     exit(1)

    app.run(host='0.0.0.0',port=81,debug=True)
