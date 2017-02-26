from flask import Flask, request
from flask import render_template
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

c = sqlite3.connect('database.db')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, lat TEXT, lon TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS projects (owner TEXT, description TEXT, imglink TEXT)')
c.close()

def insert_user(username, password):
        try:
            with sqlite3.connect("database.db") as con:
                fred = con.execute("SELECT username from users where username = (?)", (username, ))
                rows = fred.fetchall()
                if len(rows) != 0:
                    raise Exception("User already exists")
                con.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, generate_password_hash(password), ))
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

app = Flask(__name__)
#Bootstrap(app)

@app.route("/login", methods = ['POST', 'GET'])
def login():
    # if request.method == 'POST':
    valid = verify_user(request.form['username'], request.form['password'])
    print ("User logged in!" if valid else "Wrong password!")
    resp = make_response(render_template('readcookie.html'))
    resp.set_cookie('token', request.form['password'])
    return resp
    # return render_template('index.html')


@app.route("/signupform", methods = ['POST', 'GET'])
def signup():
    insert_user(request.form['username'], request.form['password'])
    return render_template('profile.html')

@app.route("/")
def hello():
    return render_template('index.html')
@app.route("/signup")
def signin():
    return render_template('signup.html')
@app.route("/profile")
def profile():
    return render_template('profile.html')
if __name__ == "__main__":
    app.run()
