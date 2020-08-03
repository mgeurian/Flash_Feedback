from flask import Flask, render_template, redirect, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, UserForm, FeedbackForm

from models import db, connect_db, User, Feedback
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///reg-auth"
app.config["SQLALCHEMY TRACK MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 
        email = form.email.data   
        first_name = form.first_name.data   
        last_name = form.last_name.data   

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another username')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f"/users/{new_user.username}")

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data 

        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')

        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)


@app.route('/users/<username>')
def show_user(username):

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for('home_page'))
        
    user = User.query.get(username)

    return render_template("secret.html", user=user)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
  """ remove a user and feedback from the database """

  if "username" not in session:
      flash("Please login first", "danger")
      return redirect(url_for('home_page'))
  
  user = User.query.get(username)
  if user.username == session['username']:
      db.session.delete(user)
      db.session.commit()
      session.pop('username')
      flash("The user and their feedback have been deleted!", "danger")
      return redirect("/login")


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect(url_for('home_page'))



@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for('home_page'))

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data   
        content = form.content.data   

        new_feedback = Feedback(title=title, content=content, username=username)

        db.session.add(new_feedback)
        db.session.commit()

        flash('New feedback has been added!', "success")
        return redirect(f"/users/{ username }")


    return render_template("feedback.html", username=username, form=form)


@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def update_feed(id):
    """ update feedback """

    feed = Feedback.query.get(id)

    if 'username' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('home_page'))

    form = FeedbackForm(obj=feed)
    
    if form.validate_on_submit():
        feed.title = form.title.data   
        feed.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{ feed.username }")

    return render_template("edit.html", form=form, feed=feed)

@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feed(id):
    """  delete feedback """

    if 'username' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('home_page'))

    feed = Feedback.query.get_or_404(id)
    if feed.username == session['username']:
        db.session.delete(feed)
        db.session.commit()
        flash("Feedback deleted!", "success")
        return redirect(f"/users/{ feed.username }")
    flash("You don't have permission to do that!", "danger")
    return redirect(url_for('home_page'),)









