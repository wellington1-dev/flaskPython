from flask import Flask, render_template, redirect, session, flash, request
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

app = Flask(__name__)
app.secret_key = "ThIsIsSeCrET"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['POST'])
def register():

    error = False
    # Let's add validtion rules

    if len(request.form['first_name']) < 1:
            flash("Name cannot be blank!", 'first_name')
    elif len(request.form['first_name']) <= 3:
        flash("Name must be 3+ characters", 'first_name')
        error = True

    if len(request.form['last_name']) < 1:
            flash("last_name cannot be blank!", 'last_name')
    elif len(request.form['first_name']) <= 3:
        flash("Name must be 3+ characters", 'last_name')
        error = True

    if len(request.form['email']) < 1:
        flash("Email cannot be blank!", 'email')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!", 'email')
        error = True
    
    if len(request.form['password']) < 1:
        flash("Password cannot be blank!", 'passoword')
    elif request.form['password'].isdigit() == False:
        flash("Password must be numeric", 'password')
    elif len(request.form['password']) < 4 or len(request.form['password'])>8:
        flash("password must be 4-8 digits", 'password')
        error = True
    
    if request.form['password'] != request.form["c_password"]:
        flash("Password must match")
        error = True

    if not request.form['first_name'].isalpha():
        flash("This name is not allowed")
        error = True
    if not request.form['first_name'].isalpha():
        flash("This name is not allowed")
        error = True

    if not EMAIL_REGEX.match(request.form['email']):
        flash("This email is not valid")
        error = True
        #email nao existente
        data = {
            "email" : request.form["email"]
        }
        query = "select * from users where email = %(email)s"
        mysql = connectToMySQL('mygames')
        matching_email_users = mysql.query_db(query,data)
        if len(matching_email_users) > 0:
            flash("Email - Information Incorrect")
            error = True;

    if error:
        return redirect("/")
    data = {
        #nome das strings que estarao dentro representando a query abaixo
        "first_name" : request.form["first_name"],
        "last_name" : request.form["last_name"],
        "email" : request.form["email"],
        "password" : bcrypt.generate_password_hash
        (request.form['password'])
    }
    query = "insert into users (first_name,last_name,email,password,created_at, updated_at) values(%(first_name)s,%(last_name)s,%(email)s,%(password)s,NOW(),NOW());"
    mysql = connectToMySQL('mygames')
    new_id = mysql.query_db(query,data)
    session['user_id'] = new_id
    return redirect("/dashboard")

@app.route('/login', methods=['POST'])
def login():
    print(request.form)

    email_query = 'SELECT * FROM users WHERE email = %(email)s;'
    email_data = {'email': request.form['email']}
    mysql = connectToMySQL('mygames')
    result = mysql.query_db(email_query, email_data)

    if len(result) == 0:
        flash('invalid login, try again.', 'login')
        return redirect('/')
    new_id = result[0]   
    if not bcrypt.check_password_hash(result[0]['password'], request.form['password']):
        flash('invalid login, try again.', 'login')
        return redirect('/')

    session['user_id'] = new_id['id']
    return redirect('/dashboard')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")
@app.route("/dashboard")
def dashboard():
    if not'user_id'in session:
        flash("You logoff")
        return redirect("/")

    data = {
        "id" : session['user_id']
    }

    user_query = 'SELECT * FROM users WHERE id = %(id)s;'
    mysql = connectToMySQL('mygames')
    user_info = mysql.query_db(user_query, data)

    query = 'SELECT games.id, name_game, description, users_id, first_name, last_name FROM games JOIN users ON games.users_id = users.id;'
    mysql = connectToMySQL('mygames')
    posted = mysql.query_db(query, data)

    
    query = 'SELECT * FROM likes;' 
    mysql = connectToMySQL('mygames')
    likes = mysql.query_db(query, data)

    
    return render_template("dashboard.html", user=user_info, posted=posted, likes = likes)

@app.route("/add_games", methods=["POST"])
def add_games():
    data = {
            "users_id" : session["user_id"],
            "name_game" : request.form["name_game"],
            "description" : request.form['description'],
            "age_recomended" : request.form['age_recomended']
    }
    query = 'INSERT INTO games(name_game, description, age_recomended, created_at, updated_at,users_id ) VALUES(%(name_game)s, %(description)s,%(age_recomended)s, NOW(),NOW(),%(users_id)s);'
    mysql = connectToMySQL('mygames')
    mysql.query_db(query, data)
    print(query)
    return redirect('/dashboard' )

@app.route("/like/<int:new_id>")
#  "This is a url parameter""
def like(new_id):
    data ={
        
        "user_id" : session['user_id'],
        "new_id" : new_id
    }
    query = 'INSERT INTO likes(games_id,users_id) VALUES(%(new_id)s,%(user_id)s);'
    mysql = connectToMySQL('mygames')
    mysql.query_db(query, data)
    return redirect('/dashboard')



if __name__ == "__main__":
    app.run(debug=True)