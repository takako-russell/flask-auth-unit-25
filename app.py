from flask import Flask, render_template,redirect,session,url_for
from models import connect_db,db,User,Feedback
from forms import RegisterForm,LoginForm,FeedbackForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask-feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "shhhhh"


connect_db(app)
app.app_context().push()
db.create_all()

@app.route("/")
def register():
    return redirect("/register")

@app.route("/register", methods=["GET"])
def show_and_register():
    # if "username" is in session:
    if session.get('username'):
        return redirect(url_for('user_profile'), username=session['username'])
    
    form = RegisterForm()
    return render_template("register.html", form=form)


@app.route("/register", methods=["POST"])
def do_register():
    form = RegisterForm()
    
    valid = form.validate_on_submit()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        user = User.register(username, password, first_name, last_name, email)
        db.session.commit()
        
        session["username"] = user.username
        return redirect("/secret")
    
    else:
       return render_template("register.html", form=form)
    
    

@app.route("/login", methods=["GET","POST"])
def login():
    
    if "username" in session:
       return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username,password)
        if user:
            session["username"] = user.username
            return redirect(f"/users/{user.username}")
        else:    
            return render_template("login.html",form=form)
    
    return render_template("login.html",form=form)
        
        
@app.route("/users/<username>")
def user_profile(username):
    if session['username'] == username:
        user = User.query.get(username)
        return render_template("user_profile.html",user=user)
    else:
        return redirect('/login')

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/login")

@app.route("/users/<username>/create", methods = ["GET","POST"])
def create_new_feedback(username):
    form = FeedbackForm()
    user = User.query.get(username)
    
    if form.validate_on_submit():

        title = form.title.data
        content = form.content.data
        username = username
        
        new_feedback = Feedback(title=title, content=content, username=username)
        
        db.session.add(new_feedback)
        db.session.commit()
        
        return redirect(f"/users/{username}")
    
    elif session['username'] == username:
        form = FeedbackForm()
        
        return render_template("feedback/new_feedback.html",form=form,user = user)
    
    
    return redirect("/login")

@app.route("/users/<username>/delete",methods=["POST"])
def delete_user(username):
   user = User.query.get(username)
   
   db.session.delete(user)
   db.session.commit()
   session.pop("username")
   
   return redirect("/login")

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
   
    feedback = Feedback.query.get(feedback_id)
    form = FeedbackForm(obj=feedback)

    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    
    elif feedback.username == session['username']:
        return render_template("feedback/update_feedback.html",form=form, username = feedback.username)


    return render_template("/login")


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    
    feedback = Feedback.query.get(feedback_id)
    
    if session["username"] == feedback.username: 

        db.session.delete(feedback)
        db.session.commit()
   

        return redirect(f"/users/{feedback.username}")
    
    return redirect("/login")

