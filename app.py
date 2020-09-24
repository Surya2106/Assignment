from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import re

app = Flask(__name__)
app.secret_key = "delhivery"
app.permanent_session_lifetime = timedelta(minutes=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:surya@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class feedbackInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(80), nullable=False)
    company = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text())

    def __int__(self, customer, company, rating, comments):
        self.customer = customer
        self.company = company
        self.rating = rating
        self.comments = comments


class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route("/welcome", methods=['GET', 'POST'])
def welcome():
    return render_template("welcome.html")


@app.route("/review", methods=["GET", "POST"])
def review():
    if "uname" in session:  # any user can fill feedback form only when user logins
        if request.method == "POST":
            print("entered post review")
            customer = request.form['customer']
            comments = request.form['comments']
            company = request.form['company']
            rating = request.form['rating']

            # print(customer, comments, company, rating)
            feedback = feedbackInfo(customer=customer, company=company, rating=rating, comments=comments)
            db.session.add(feedback)
            db.session.commit()

            return redirect(url_for("welcome"))
        return render_template("review.html")
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form['uname']
        passw = request.form['passw']

        signIn = user.query.filter_by(username=uname, password=passw).first()

        if signIn is not None:
            session["uname"] = uname
            session.permanent = True
            return redirect(url_for("review", customer=uname))

        return "invalid login credentials";

    else:
        if "uname" in session:
            return redirect(url_for("review"))
        return render_template("login.html")


def checkPassword(password):

    charRegex = re.compile(r'(\w{8,})')
    lowerRegex = re.compile(r'[a-z]+')
    upperRegex = re.compile(r'[A-Z]+')
    digitRegex = re.compile(r'[0-9]+')

    if not charRegex.findall(password):
        return "password length must be at least 8 characters"

    elif not lowerRegex.findall(password):
        return "password must contain at least one lower case character"

    elif not upperRegex.findall(password):
        return "password must contain at least one upper case character"

    elif not digitRegex.findall(password):
        return "password must contain at least one digit"

    return "True"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        checkUser = user.query.filter_by(username=uname).first()
        checkMail = user.query.filter_by(email=mail).first()

        if checkUser is not None:
            return "user already exists"
        if checkMail is not None:
            return "email already exists"

        verdict = checkPassword(passw)

        if not verdict == "True":
            return verdict

        signUp = user(username=uname, email=mail, password=passw)
        db.session.add(signUp)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("registration.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
