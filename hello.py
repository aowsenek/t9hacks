from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

c = sqlite3.connect('database.db')
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS projects (name TEXT, addr TEXT, city TEXT, pin TEXT)')
c.close()

def insert_user(username, password):
        try:
            with sqlite3.connect("database.db") as con:
                fred = con.execute("SELECT username from users where username = (?)", (username, ))
                rows = fred.fetchall()
                if len(rows) != 0:
                    raise Exception("User already exists")
                    print("AAAAA")
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
            if len(rows) != 0:
                hash = rows[0][0]
                return check_password_hash(hash, password)
    except Exception as e:
        print "Error: ", e
        con.rollback()
    finally:
        con.close()
    return False

print insert_user("Fred", "password")
print insert_user("Bill", "swordfish")
print verify_user("Fred", "password")
print verify_user("Fred", "pass")
print verify_user("bill", "pass")
print verify_user("Bill", "swordfish")

# try:
#     with sqlite3.connect("database.db") as con:
#         fred = con.execute("SELECT * from users")
#         rows = fred.fetchall()
#         for row in rows:
#             for col in row:
#                 print col
# except Exception as e:
#     print "Error: ", e
#     con.rollback()
# finally:
#     con.close()

app = Flask(__name__)
#Bootstrap(app)

@app.route("/")
def hello():
    return render_template('index.html')
if __name__ == "__main__":
    app.run()

# @app.route('/addrec',methods = ['POST', 'GET'])
# def addrec():
#    if request.method == 'POST':
#       try:
#          nm = request.form['nm']
#          addr = request.form['add']
#          city = request.form['city']
#          pin = request.form['pin']
#
#          with sql.connect("database.db") as con:
#             cur = con.cursor()
#             cur.execute("INSERT INTO students (name,addr,city,pin)
#                VALUES (?,?,?,?)",(nm,addr,city,pin) )
#
#             con.commit()
#             msg = "Record successfully added"
#       except:
#          con.rollbac
#          k()
#          msg = "error in insert operation"
#
#       finally:
#          return render_template("result.html",msg = msg)
#          con.close()
