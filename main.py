from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:chosen12@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "sec_187"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16))

    # Hash the user's password for security purposes.
    pw_hash = db.Column(db.String(120))

    # Optional email for account recovery and security.
    email = db.Column(db.String(50))

    # Bind the user to the blogs they write.
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password, email):
        self.username = username
        self.pw_hash = make_pw_hash(password)
        self.email = email

@app.before_request
def require_login():
    # These allowed routes are names of view functions, NOT the actual URL route.
    allowed_routes = ['signup','login','blog','index','single','author']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/logout')
def logout():
    # Delete the user's login session.
    del session['username']

    # Redirect the logged out user to the home page.
    return redirect('/blog')



@app.route('/newpost', methods=['POST', 'GET'])
def create_blog_post():
    if request.method == 'GET':
        login_name = session['username']
        return render_template('create_post.html',login_name=login_name)

    if request.method == 'POST':
        check_post_title = request.form['post_title']
        check_post_body = request.form['post_body']
        cpb = check_post_body.strip()

    post_title_status = ""
    post_body_status = ""
    activate = True

    if request.method == 'POST':
        if len(check_post_title) == 0:
            post_title_status = "The blog post title cannot be empty. "
            activate = False

        if len(cpb) == 0:
            post_body_status = "The blog post body cannot be empty. "
            activate = False

    if request.method == 'POST' and activate != False:
        # Get the title of the new blog post from the html form.
        post_title = request.form['post_title']

        # Get the body of the new blog post from the html form.
        post_body = request.form['post_body']

        # Identify the new post's owner by their username in the current login session.
        post_owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(post_title, post_body, post_owner)
        
        # Add the new post to the database session and commit.
        db.session.add(new_post)
        db.session.commit()

        # Redirect the user to their newly created blog post.
        value = new_post.id
        location = '/blog?id={}'
        location = location.format(value)
        return redirect(location)

    if request.method == 'POST' and activate == False:
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        return render_template('create_post.html', title_hold=post_title, body_hold=post_body,  title_alert=post_title_status, body_alert=post_body_status)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET' and 'username' not in session:
        return render_template('signup.html',login_name=False)

    if request.method == 'GET' and 'username' in session:
        login_name = session['username']
        return render_template('status.html',login_name=login_name)

    username = request.form['username']
    password = request.form['password']
    check_password = request.form['check_password']

    # Optional email for extra account security and recovery.
    email = request.form['email']

    username_status = ""
    password_status = ""
    verified_status = ""
    email_status = ""
    activate = True
    email_activate = True

    # Existing user statement
    existing_user = User.query.filter_by(username=username).first()

    # Existing email statement
    existing_email = User.query.filter_by(email=email).first()

    if len(username) < 3 or len(username) > 20 or username.isalnum() != True:
        username_status = "Username must be between 3 and 20 alphanumeric characters. No spaces allowed. "
        activate = False

    if existing_user:
        username_status = "That username is already taken. Please choose another."
        activate = False

    if len(password) < 3 or len(password) > 20 or password.isalnum() != True :
        password_status = "Password must be between 3 and 20 alphanumeric characters. No spaces allowed. "
        activate = False

    if len(check_password) < 3 or len(check_password) > 20 or check_password.isalnum() != True or check_password != password:
        verified_status = "Both passwords must match and meet the same requirements to verify."
        activate = False

    if len(email) < 3 or len(email) > 50 or email.find("@") < 0 or email.find(".") < 0 or email.find(" ") > -1 :
        email_status = "It is optional, but we recommend that you submit a valid email for your account."
        email_activate = False

        if len(email) > 0 and email_activate == False:
            email_status = "The email you supplied is not valid."
            activate = False

        if len(email) == 0:
            email_activate = True

    if existing_email and len(email) > 1:
        email_status = "That email is already in use. Please choose another."
        activate = False
    
    if activate == False:
        message = "Your registration could not be processed.<br />" + username_status + "<br />" + password_status + "<br />" + verified_status
        return render_template('signup.html', username_alert=username_status,password_alert=password_status,verifypw_alert=verified_status,email_alert=email_status,username=username,email=email)

    if activate != False and email_activate == False:
        return render_template('signup.html', username=username, email_status=email_status)

    if activate != False and email_activate != False:
        new_user = User(username, password, email)
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username
        return redirect('/newpost')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        login_name = session['username']
        return render_template('status.html', login_name=login_name)

    if request.method == 'GET' and 'username' not in session:
        return render_template('login.html', login_name=False)

    if request.method == 'POST' and 'username' not in session:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # If this username exists and the hashed password is correct, go ahead and log the user in.
        if request.method == 'POST' and user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')

        else:
            # If the username does not exist, show the username alert.
            if request.method == 'POST' and not user:
                username_status = "The username you entered does not exist."
                return render_template('login.html', username_alert=username_status)

            # If the username exists, but the password is incorrect, show the password alert.
            if request.method == 'POST' and user and user.password != password:
                password_status = "The password you entered is incorrect."
                return render_template('login.html', username_hold=username, password_alert=password_status)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    author_name = request.args.get('user')
    blog_id = request.args.get('id')

    if 'username' in session and not author_name and not blog_id:
        login_name = session['username']
        blogs = Blog.query.all()
        return render_template('articles.html',blogs=blogs,login_name=login_name,title='Welcome to MiniPress')

    if 'username' in session and blog_id and not author_name:
        # Working Properly
        login_name = session['username']
        blog = Blog.query.get(blog_id)
        return render_template('blog_single.html',blog=blog,login_name=login_name,title='Welcome to MiniPress')


    if 'username' in session and author_name and not blog_id:
        login_name = session['username']
        user = User.query.filter_by(username=author_name).first()
        blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('singleUser.html',user=user,blogs=blogs,login_name=login_name,title='Welcome to MiniPress')


    if 'username' not in session and blog_id and not author_name:
        # Working properly
        blog = Blog.query.get(blog_id)
        owner = blog.owner
        owner = owner.username
        return render_template('single_blog.html',owner=owner,blog=blog,login_name=False,title='Welcome to MiniPress')


    if 'username' not in session and author_name and not blog_id:
        # Working properly
        user = User.query.filter_by(username=author_name).first()
        blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('singleUser.html',user=user,blogs=blogs,login_name=False,title='Welcome to MiniPress')


    if 'username' not in session and not author_name and not blog_id:
        blogs = Blog.query.all()
        return render_template('blog.html',login_name=False,blogs=blogs)



@app.route('/index', methods=['POST', 'GET'])
def index():
    if 'username' in session:
        login_name = session['username']
        return render_template('home.html',login_name=login_name,title='Welcome to MiniPress')

    if 'username' not in session:
        return render_template('index.html',login_name=False,title='Welcome to MiniPress')


@app.route('/author', methods=['POST', 'GET'])
def author():
    authors = User.query.all()

    if 'username' in session:
        login_name = session['username']
        return render_template('author.html',authors=authors,login_name=login_name,title='Welcome to MiniPress')

    if 'username' not in session:
        return render_template('author.html',login_name=False,authors=authors,title='Welcome to MiniPress')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if 'username' in session:
        login_name = session['username']
        login_user = User.query.filter_by(username=login_name).first()
        login_email = login_user.email
        return render_template('status.html', login_name=login_name,login_email=login_email)


@app.route('/', methods=['POST', 'GET'])
def single():
    blog_id = request.args.get('id')
    author_name = request.args.get('user')

    if 'username' in session and request.method == 'GET' and not blog_id and not author_name:
        login_name = session['username']
        authors = User.query.all()
        return render_template('author.html',login_name=login_name,authors=authors)


    if 'username' in session and request.method == 'GET' and int(blog_id) > 0:
        login_name = session['username']
        # blogs = Blog.query.all()
        blog = Blog.query.get(blog_id)

        user = User.query.filter_by(username=author_name).first()
        blog_owner = user.id
        blogs = Blog.query.filter_by(owner_id=blog_owner).all()
        return render_template('single.html',user=user,blogs=blogs,blog=blog,login_name=login_name)


    if 'username' not in session and request.method == 'GET' and not blog_id and not author_name:
        authors = User.query.all()
        return render_template('author.html',login_name=False,authors=authors)

    if 'username' not in session and request.method == 'GET' and int(blog_id) > 0:
        # Awesome! I can finally use the owner_id class object!
        blogs = Blog.query.all()
        blog = Blog.query.get(blog_id)
        owner = blog.owner
        owner = owner.username
        return render_template('single_blog.html',owner=owner,login_name=False,blogs=blogs,blog=blog)


if __name__ == '__main__':

    app.run()