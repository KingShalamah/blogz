from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:chosen12@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

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

    # I will hash the user's password for security purposes.
    password = db.Column(db.String(20))

    # Bind the user to the blogs they write.
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password, blogs):
        self.username = username
        self.password = password
        self.blogs = blogs

"""
@app.route('/', methods=['POST', 'GET'])
def index():
    blog_id = request.args.get('id')

    if request.method == 'GET' and not blog_id:
        return redirect('/blog')

    if request.method == 'GET' and int(blog_id) > 0:
        blogs = Blog.query.all()
        blog = Blog.query.get(blog_id)
        return render_template('single_blog.html',blogs=blogs,blog=blog)
"""

@app.route('/blog', methods=['GET'])
def show_blogs():
    blogs = Blog.query.all()
    return render_template('blog.html',blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def create_blog_post():
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
        location = '/?id={}'
        location = location.format(value)
        return redirect(location)

    if request.method == 'POST' and activate == False:
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        return render_template('create_post.html', title_hold=post_title, body_hold=post_body,  title_alert=post_title_status, body_alert=post_body_status)
    
    elif request.method == 'GET':
        return render_template('create_post.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    blog_id = request.args.get('id')

    if request.method == 'GET' and not blog_id:
        return redirect('/blog')

    if request.method == 'GET' and int(blog_id) > 0:
        blogs = Blog.query.all()
        blog = Blog.query.get(blog_id)
        return render_template('single_blog.html',blogs=blogs,blog=blog)


@app.route('/login', methods=['POST', 'GET'])
def login():
    blog_id = request.args.get('id')

    if request.method == 'GET' and not blog_id:
        return redirect('/blog')

    if request.method == 'GET' and int(blog_id) > 0:
        blogs = Blog.query.all()
        blog = Blog.query.get(blog_id)
        return render_template('single_blog.html',blogs=blogs,blog=blog)


@app.route('/index', methods=['POST', 'GET'])
def index():
    blog_id = request.args.get('id')

    if request.method == 'GET' and not blog_id:
        return redirect('/blog')

    if request.method == 'GET' and int(blog_id) > 0:
        blogs = Blog.query.all()
        blog = Blog.query.get(blog_id)
        return render_template('single_blog.html',blogs=blogs,blog=blog)


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        # Delete the current username from the session.

        # Redirect the logged out user to the blog page.
        return redirect('/blog')

if __name__ == '__main__':

    app.run()