from __future__ import print_function # In python 2.7
from datetime import datetime
import sys
import site
from unicodedata import name
from flask import Flask, redirect, render_template, request,flash, url_for
# from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user,current_user

app = Flask(__name__)
app.secret_key = 'super secret key'
# app.config["SQLALCHEMY_D"]
# app.config["SECRET_KEY"] = "key"


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "error"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///Database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db = SQLAlchemy(app)

class Users(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique = True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))
    task=db.relationship("Tasks")

class Tasks(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    date = db.Column(db.String(50))

db.create_all()

@app.route('/',methods = ["GET"])
def hello():
    return render_template('Home.html')

@app.route('/create',methods = ["GET","POST"])
def addUser():
    if request.method == "POST":
        uuname=request.form.get("username")
        uname = request.form.get("name")
        uemail = request.form.get("useremail")
        upass = request.form.get("userpass")
        user=Users.query.filter_by(email=uemail).first()
        if user:
            return render_template("register.html", msg = {"Message":"Username Already Exists!"})
        else:
            user=Users(username = uuname, name=uname,email=uemail,password=generate_password_hash(upass))
            db.session.add(user)
            db.session.commit()
            return render_template("login.html",flag=True,msg={"Message":"User Created Successfully!"})
    return render_template("register.html")

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method =="POST":
        email=request.form.get('username')
        password=request.form.get('userpass')
        user =Users.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for("add_task"))
            return render_template("login.html",msg={"Message":"Invalid Password"})
        return render_template("login.html",msg={"Message":"User Not found"})
    return render_template("login.html")


@app.route("/addtask",methods=["GET","POST"])
@login_required
def add_task():
    if request.method == "POST":
        description = request.form.get('description')
        date=request.form.get('date')
        task = Tasks(description=description,date=date,user_id=current_user.id)
        # here task obkect  is different from db model akka once check diff na??
        db.session.add(task)
        db.session.commit()
        return render_template("todo.html",msg={"Message":"Task Added!"})
        # flash("Movie added successfully!",category="success")
    return render_template("todo.html")

@app.route("/tasks")
def tasks():
    task = Tasks.query.all()
    print(task,file=sys.stderr)
    return render_template('alltask.html', task=task)
    # return render_template("alltask.html",task)



@app.route("/delete/<int:id>")
@login_required
def delete(id):
    to_delete = Tasks.query.get(id)
    if current_user.id == to_delete.user_id:
        db.session.delete(to_delete)
        db.session.commit()
        return redirect(url_for("tasks"))
    return redirect(url_for("tasks"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)