from app import app, db, login, admin
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Messages
from app.forms import LoginForm, PostForm, ContactForm, SearchForm
import datetime
from flask_admin import Admin,BaseView,expose
from flask_admin.menu import MenuLink
from flask_admin.contrib import sqla
from math import ceil

# Create AdminVire class 
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
        admin.add_views(adminView(User, db.session))
        views_already_created = True

@app.route('/')
def index():
    # Load the newest 3 post from database
    Posts = Post.query.order_by(Post.post_id.desc())[:3]
    return render_template('index.html', Posts=Posts, title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Generate the search form
    form=SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_item', item=form.item.data))
    return render_template('search.html', form=form, results=None, item=None, title='Search')

@app.route('/search/<item>', methods=['GET', 'POST'])
def search_item(item):
    # Generate the search form and populate with the 
    # previous search item
    form=SearchForm(item=item)
    if form.validate_on_submit():
        # If user searches again redirect to those results
        return redirect(url_for('search_item', item=form.item.data))

    # Grab all posts and create empty array
    Posts = Post.query.order_by(Post.post_id.desc())
    results=[]
    # Loop through every post and find if deisred term is anywhere in the post
    for post in Posts:
        text = post.title + ' ' + post.subtitle + ' ' + post.raw_body + ' ' + post.tags
        if item in text:
            # If so: append to results
            results.append(post)
    return render_template('search.html', form=form, results=results, item=item, title='Search')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    # Generate Contact Form
    form = ContactForm()
    if form.validate_on_submit():
        # Create message object with the neccesary details
        message = Messages(name=form.name.data, email=form.email.data, phone=form.phone.data, message=form.message.data)
        # 'Send' to me (add message to db)
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
        # Find how many posts exist
        count = db.session.query(Post.post_id).count()
        # Create post object and add to db
        post = Post(post_id=count, title=form.title.data, subtitle=form.subtitle.data, raw_body=form.raw_body.data, tags=form.tags.data, date=str(datetime.datetime.today().strftime("%B")) + ' ' + str(datetime.datetime.today().day) + ', ' + str(datetime.datetime.today().year))
        db.session.add(post)
        db.session.commit()
        flash('Posted!')
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form, title='Make a Post')

@app.route('/posts')
def posts():
    # Find what page is being requested
    page = request.args.get('page', 1, type=int)

    # If that page is either larger than what is avaliable or less than 1: return either the last possible page or the first page
    if page > ceil(db.session.query(Post.post_id).count() / 5): return redirect(url_for('posts', page=ceil(db.session.query(Post.post_id).count() / 5)))
    if page < 1: return redirect(url_for('posts', page=1))

    # Generate the posts for this page
    Posts = Post.query.order_by(Post.post_id.desc()).paginate(page,5,False).items
    
    # Determine whether there is a previous or next page
    has_prev = False if page == 1 else True
    has_next = False if ceil(db.session.query(Post.post_id).count() / 5) == page else True

    return render_template('post.html', Posts=Posts, page=page, has_next=has_next, has_prev=has_prev, title='Posts')

@app.route('/posts/<id>/<title>')
def view_post(id, title):
    # Find the requested post
    post = Post.query.filter_by(post_id=id).first()
    # Split the tags into a list
    tags = post.tags.split(',')
    return render_template('view_post.html', post=post, tags=tags, title=post.title, desc=post.subtitle)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already logged in
    if current_user.is_authenticated:
        return redirect('index')

    # Generate login form
    form = LoginForm()
    if form.validate_on_submit():
        # Theres only one user.. so just pull it up
        user = User.query.filter_by(username=form.username.data).first()
        # If the user is valid (I hope it is) and the password is right
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect Login')
            return redirect(url_for('login'))
        # Login and create the admin views
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