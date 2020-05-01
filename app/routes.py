from app import app, db, login, admin
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Messages
from app.forms import LoginForm, PostForm, ContactForm, SearchForm
import datetime
from flask_admin import Admin,BaseView,expose
from flask_admin.menu import MenuLink
from flask_admin.contrib import sqla

#admin = Admin(app, name='ethanshealey')

class adminView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_authenticated 

# Global bool to prevent double-logins that cause a crash
views_already_created = False

# Function to create the admin views once an admin logs in
# NOTE: Make sure function only runs ONCE per session!
def create_admin_views():
    global views_already_created
    if views_already_created is False:
        admin.add_link(MenuLink(name='Public Website', category='', url=url_for('index')))
        admin.add_views(adminView(Post, db.session))
        admin.add_views(adminView(Messages, db.session))
        views_already_created = True

@app.route('/index')
@app.route('/')
def index():
    Posts = Post.query.order_by(Post.post_id.desc())
    print(Posts)
    return render_template('index.html', Posts=Posts, title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/search', methods=['GET', 'POST'])
def search():
    form=SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_item', item=form.item.data))
    return render_template('search.html', form=form, results=None, title='Search')

@app.route('/search/<item>', methods=['GET', 'POST'])
def search_item(item):
    form=SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_item', item=form.item.data))
    Posts = Post.query.order_by(Post.post_id.desc())
    results=[]
    for post in Posts:
        text = post.title + ' ' + post.subtitle + ' ' + post.raw_body + ' ' + post.tags
        if item in text:
            results.append(post)
    return render_template('search.html', form=form, results=results, title='Search')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        message = Messages(name=form.name.data, email=form.email.data, phone=form.phone.data, message=form.message.data)
        db.session.add(message)
        db.session.commit()
        flash('Message sent!')
        return redirect(url_for('index'))
    return render_template('contact.html', form=form, title='Contact')

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form=PostForm()
    if form.validate_on_submit():
        count = db.session.query(Post.post_id).count()
        post = Post(post_id=count, title=form.title.data, subtitle=form.subtitle.data, raw_body=form.raw_body.data, tags=form.tags.data, date=str(datetime.datetime.today().strftime("%B")) + ' ' + str(datetime.datetime.today().day) + ', ' + str(datetime.datetime.today().year))
        db.session.add(post)
        db.session.commit()
        flash('Posted!')
        return redirect(url_for('index'))
    return render_template('post.html', form=form, title='Make a Post')

@app.route('/posts/<id>/<title>')
def view_post(id, title):
    post = Post.query.filter_by(post_id=id).first()
    tags = post.tags.split(',')
    return render_template('view_post.html', post=post, tags=tags, title=post.title, desc=post.subtitle)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('index')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect Login')
            return redirect(url_for('login'))
        login_user(user)
        create_admin_views()
        return redirect(url_for('admin.index'))
    return render_template('login.html', form=form, title='Login')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404'), 404