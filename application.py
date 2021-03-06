from flask import Flask, request, redirect, url_for, render_template, make_response
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3
import urllib
import json

c = sqlite3.connect('database.db')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, lat TEXT, lng TEXT, gender TEXT, description TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS projects (owner TEXT, name TEXT, category TEXT, description TEXT, lat TEXT, lng TEXT, imglink TEXT)')
c.close()

def insert_user(username, password, location, gender, description):
        try:
            with sqlite3.connect("database.db") as con:
                fred = con.execute("SELECT username from users where username = (?)", (username, ))
                rows = fred.fetchall()

                f = urllib.urlopen("http://www.mapquestapi.com/geocoding/v1/address?key=snDZGmb07Jc3pnSyuKxpqhQo7l6ExlEr&location=%s" % location)
                js = json.loads(f.read())
                location = js['results'][0]['locations'][0]['displayLatLng']

                if len(rows) != 0:
                    raise Exception("User already exists")
                con.execute("INSERT INTO users (username, password, lat, lng, gender, description) VALUES (?, ?, ?, ?, ?, ?)", (username, generate_password_hash(password), location['lat'], location['lng'], gender, description, ))
                con.commit()
                generateUserImage()
        except Exception as e:
            print "Error: ", e
            con.rollback()
        finally:
            con.close()

def generateUserImage():
    try:
        with sqlite3.connect("database.db") as con:
            fred = con.execute("SELECT lat, lng from users")
            todd = con.execute("SELECT lat, lng from projects")
            rows = fred.fetchall() + todd.fetchall()
            api = 'https://beta.mapquestapi.com/staticmap/v5/getmap?size=600,400@2x&key=snDZGmb07Jc3pnSyuKxpqhQo7l6ExlEr&locations='
            for i,row in enumerate(rows):
                api += "%s,%s%s" % (row[0], row[1], "||" if (i < len(rows) - 1) else "")
            urllib.urlretrieve(api, 'static/images/usermap.png')

    except Exception as e:
        print "Error: ", e
        con.rollback()
    finally:
        con.close()

def insert_project(owner, name, category, description, location, imglink):
    try:
        with sqlite3.connect("database.db") as con:
            f = urllib.urlopen("http://www.mapquestapi.com/geocoding/v1/address?key=snDZGmb07Jc3pnSyuKxpqhQo7l6ExlEr&location=%s" % location)
            js = json.loads(f.read())
            location = js['results'][0]['locations'][0]['displayLatLng']
            print "Location:", location
            con.execute("INSERT INTO projects (owner, name, category, description, lat, lng, imglink) VALUES (?, ?, ?, ?, ?, ?, ?)", (owner, name, category, description, location['lat'], location['lng'], imglink, ))
            con.commit()
    except Exception as e:
        print "Insert project error: ", e
        con.rollback()
    finally:
        con.close()

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

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
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


def get_thumbs():
    try:
        with sqlite3.connect("database.db") as con:
            fred = con.execute("SELECT username, gender, description from users").fetchall()
            todd = con.execute("SELECT owner, name, category, description, imglink from projects").fetchall()
            thumbs='''
            <article class="thumb">
                <a href="static/images/usermap.png" class="image"><img src="static/images/usermap.png" alt="" /></a>
                <h2>Users near you</h2>
                <p>There are %d users and %d projects near you!</p>
            </article>
            ''' % (len(fred), len(todd))

            for user in fred:
                thumbs += '''<article class="thumb">
                    <a href="../static/multiverseimages/thumbs/01.jpg" class="image"><img src="../static/multiverseimages/thumbs/01.jpg" alt="" /></a>
                    <h2>User: %s</h2>
                    <p>%s <br /> %s</p>
                </article>
                ''' % (user[0], user[1], user[2])
            for project in todd:
                thumbs += '''<article class="thumb">
                    <a href="%s" class="image"><img src="%s" alt="" /></a>
                    <h2>%s | %s</h2>
                    <p>%s
                    <br />
                    %s</p>
                </article>
                ''' % (project[4], project[4], project[1], project[2], project[0], project[3])
            return thumbs
    except Exception as e:
        print "Error: ", e
        con.rollback()
    finally:
        con.close()
    return ""

@app.route("/projects")
def projects():
    return render_template('multiverse.html', thumbs=get_thumbs())

@app.route("/")
def hello():
    return render_template('index.html')
@app.route("/test")
def test():
    return render_template('test.html')

@app.route("/signup")
def signin():
    return render_template('signup.html')

@app.route("/createproject", methods = ['POST', 'GET'])
def makeprojet():
    token = request.cookies.get('token')
    if not token:
        print "Bad token!"
        return render_template('multiverse.html', thumbs=get_thumbs())
    try:
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            print "Redirecting"
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imglink = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(imglink)
    except Exception as e:
        print "File upload error:", e
    insert_project(token, request.form['name'], request.form['category'], request.form['description'], request.form['location'], imglink)
    return render_template('multiverse.html', thumbs=get_thumbs())

@app.route("/profile")
def profile():
    token = request.cookies.get('token')
    if not token:
        return render_template('signup.html')
    try:
        with sqlite3.connect("database.db") as con:
            fred = con.execute("SELECT username, gender, description from users where username = (?)", (token, ))
            rows = fred.fetchall()
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
