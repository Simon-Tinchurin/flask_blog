from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, \
    login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from webforms import PostForm
from datetime import datetime
from configs import *

# https://codepen.io/ig_design/pen/omQXoQ
# https://support.sendwithus.com/jinja/jinja_time/
# https://www.free-css.com/free-css-templates/page244/tech-blog
# "https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{DB_PASSWORD}@localhost/users'
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    slug = db.Column(db.String(100))

    # num_of_views = db.Column(db.Integer)
    # tags = db.relationship('Tags', secondary=post_tag, backref='post')

    def __repr__(self):
        return f'Post {self.title}'


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50))
    posts_ids = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return f'Post {self.tag}'


@app.route("/brick")
def admin():
    posts = Posts.query.order_by(Posts.date_posted)
    number_of_posts = posts.count()
    return render_template("adminpage.html", posts=posts, number_of_posts=number_of_posts)


# add post page
@app.route("/add-post", methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     slug=form.slug.data)
        # clear the form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        # add post data to database
        db.session.add(post)
        db.session.commit()
        # return a message
        flash('Post submitted successfully!')
        return redirect(url_for('single_post', id=post.id))
    # redirect to the page
    return render_template('add_post.html', form=form)


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route('/delete_<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()

        flash('Post deleted')

        posts = Posts.query.order_by(Posts.date_posted)
        return redirect(render_template('posts.html', posts=posts))

    except Exception as ex:
        flash(f'Something is wrong! Error: {ex}')
        posts = Posts.query.order_by(Posts.date_posted)
        return redirect(render_template('posts.html', posts=posts))


@app.route('/edit_post_<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data
        # update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated")
        return redirect(url_for('single_post', id=post.id))
    form.title.data = post.title
    form.content.data = post.content
    form.slug.data = post.slug
    return render_template('edit_post.html', form=form)


@app.route('/posts.html')
def get_posts():
    # grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html', title="INTERNAL SERVER ERROR"), 500


# Custom 404 error page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title="PAGE NOT FOUND"), 404


# page for single post
@app.route("/post_<int:id>")
def single_post(id):
    post = Posts.query.get_or_404(id)
    return render_template("single_post.html", post=post)


@app.route("/useful_stuff")
def useful_stuff():
    return render_template('useful_stuff.html')


if __name__ == "__main__":
    app.run(debug=True)
