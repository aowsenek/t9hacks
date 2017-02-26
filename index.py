from flask import Flask, request, redirect, url_for
from flask import render_template, make_response
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import urllib
import json

c = sqlite3.connect('database.db')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, lat TEXT, lng TEXT, gender TEXT, description TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS projects (owner TEXT, description TEXT, imglink TEXT)')
c.close()
#http://www.mapquestapi.com/geocoding/v1/address?key=snDZGmb07Jc3pnSyuKxpqhQo7l6ExlEr&location=Boulder,CO
def insert_user(username, password, location, gender, description):
        try:
            with sqlite3.connect("database.db") as con:
                fred = con.execute("SELECT username from users where username = (?)", (username, ))
                rows = fred.fetchall()

                print "Fetching location"
                f = urllib.urlopen("http://www.mapquestapi.com/geocoding/v1/address?key=snDZGmb07Jc3pnSyuKxpqhQo7l6ExlEr&location=%s" % location)
                js = json.loads(f.read())
                location = js['results'][0]['locations'][0]['displayLatLng']
                print "Location:", location['lat'], location['lng']

                if len(rows) != 0:
                    raise Exception("User already exists")
                con.execute("INSERT INTO users (username, password, lat, lng, gender, description) VALUES (?, ?, ?, ?, ?, ?)", (username, generate_password_hash(password), location['lat'], location['lng'], gender, description, ))
                con.commit()
        except Exception as e:
            print "Error: ", e
            con.rollback()
        finally:
            con.close()

def insert_project(owner, description, imglink):
        try:
            with sqlite3.connect("database.db") as con:
                fred = con.execute("SELECT username from users where username = (?)", (username, ))
                rows = fred.fetchall()

                print "Fetching location"
                f = urllib.urlopen("http://www.mapquestapi.com/geocoding/v1/address?key=snDZGmb07Jc3pnSyuKxpqhQo7l6ExlEr&location=%s" % location)
                js = json.loads(f.read())
                location = js['results'][0]['locations'][0]['displayLatLng']
                print "Location:", location['lat'], location['lng']

                if len(rows) != 0:
                    raise Exception("User already exists")
                con.execute("INSERT INTO users (username, password, lat, lng, gender, description) VALUES (?, ?)", (username, generate_password_hash(password), location['lat'], location['lng'], gender, description, ))
                con.commit()
        except Exception as e:
            print "Error: ", e
            con.rollback()
        finally:
            con.close()

# return render_template("result.html", msg = msg)
def verify_user(username, password):
    try:
        with sqlite3.connect("database.db") as con:
            fred = con.execute("SELECT password from users where username = (?)", (username, ))
            rows = fred.fetchall()
            if len(rows) == 0:
                hash = rows[0][0]
                return check_password_hash(hash, password)
    except Exception as e:
        print "Error: ", e
        con.rollback()
    finally:
        con.close()
    return False

UPLOAD_FOLDER = '/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/login", methods = ['POST', 'GET'])
def login():
    # if request.method == 'POST':
    valid = verify_user(request.form['username'], request.form['password'])
    print ("User logged in!" if valid else "Wrong password!")
    resp = make_response(render_template('profile.html'))
    resp.set_cookie('token', request.form['username'])
    return resp
    # return render_template('index.html')

@app.route("/signupform", methods = ['POST', 'GET'])
def signup():
    try:
        insert_user(request.form['username'], request.form['password'], request.form['location'], request.form['gender'].lower(), request.form['profile'])
        resp = make_response(render_template('profile.html', username = request.form['username'], gender = request.form['gender'], description = request.form['profile']))
        resp.set_cookie('token', request.form['username'])
        return resp
    except Exception as e:
        print "Error:", e

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/test")
def test():
    return render_template('test.html')

@app.route("/signup")
def signin():
    return render_template('signup.html')

@app.route("/createproject")
def signin():
    return render_template('index.html')

@app.route("/profile")
def profile():
    token = request.cookies.get('token')
    if not token:
        return render_template('signup.html')
    try:
        with sqlite3.connect("database.db") as con:
            fred = con.execute("SELECT username, gender, description from users where username = (?)", (token, ))
            rows = fred.fetchall()
            print len(rows)
            if len(rows) == 0:
                raise Exception("Invalid token")
            return render_template('profile.html', username=rows[0][0], gender=rows[0][1], description=rows[0][2])
    except Exception as e:
        print "Error: ", e
        con.rollback()
    finally:
        con.close()

    return render_template('profile.html')
if __name__ == "__main__":
    app.run()
