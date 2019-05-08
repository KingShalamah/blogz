from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogger:chosen12@localhost:8889/blogger'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():
    blog_id = request.args.get('id')

    if request.method == 'GET' and not blog_id:
        return redirect('/blog')

    if request.method == 'GET' and int(blog_id) > 0:
        blogs = Blog.query.all()
        blog = Blog.query.get(blog_id)
        return render_template('single_blog.html',blogs=blogs,blog=blog)

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
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        new_post = Blog(post_title, post_body)

        db.session.add(new_post)
        db.session.commit()
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

if __name__ == '__main__':

    app.run()