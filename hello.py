from flask import Flask
from flask import render_template
#from flask_bootstrap import Bootstrap

app = Flask(__name__)
#Bootstrap(app)

webpage = '''
{% extends "bootstrap/base.html" %}
{% block title %}This is an example page{% endblock %}

{% block navbar %}
<div class="navbar navbar-fixed-top">
  <!-- ... -->
</div>
{% endblock %}

{% block content %}
  <h1>Hello, Bootstrap</h1>
{% endblock %}
'''

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
