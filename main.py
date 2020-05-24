import os
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import numpy
from werkzeug.utils import secure_filename
import json


with open("config.json",'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = "mohit-secret"
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = "465",
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_password']
)
app.config['UPLOAD_FOLDER'] = params['upload_location']
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_server']

db = SQLAlchemy(app)





class Contact(db.Model):
    '''
    serialno , name , email , phone_number , message , date
    '''
    #serialno = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(80), primary_key = True)
    email = db.Column(db.String(20), nullable = False)
    phone_number = db.Column(db.String(12), nullable = False)
    message = db.Column(db.String(120), nullable = False)
    #date = db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    '''
    sno , title , slug , context , date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), primary_key = False)
    tag_line = db.Column(db.String(80), primary_key=False)
    slug = db.Column(db.String(20), nullable = False)
    context = db.Column(db.String(200), nullable = False)
    img_name = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=True)




post = Posts.query.filter_by(slug = "sky_info")

#--TOWARDS HOMEPAGE (INDEX.HTML)--#
@app.route('/')
def main_file():
    post = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params = params, post = post)




@app.route('/uploader',methods = ['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if (request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return"Uploaded Successfully!"



@app.route('/form.html',methods = ['GET','POST'])
def form_file():
    if 'user' in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by().all()
        return render_template('dashboard.html', params=params, post=post)
    if request.method == 'POST':
        user_name = request.form.get('inputEmail')
        user_password = request.form.get('inputPassword')
        if user_name == params['admin_user'] and user_password == params['admin_password']:
            session['user'] = user_name
            post = Posts.query.filter_by().all()
            return render_template('dashboard.html', params=params, post=post)
        else:
            return render_template('form.html', params=params)
    else:
        return render_template('form.html', params = params )



#--TOWARDS ABOUT.HTML--#
@app.route('/about.html')
def about_us():
    return render_template('about.html', params = params, post = post)



@app.route('/post.html')
def post_us():
    post = Posts.query.filter_by(slug = "first_post")
    return render_template('post.html', params = params, post=post)



#--TOWARDS POST.HTML--#
@app.route('/post.html/<string:post_slug>', methods = ['GET'])
def post_route(post_slug):
    if len(post_slug) != 0:
        post = Posts.query.filter_by(slug = post_slug).first()
        print(post_slug)
        print(post)
        return render_template('post.html', params = params, post = post)
    else:
        post = Posts.query.filter_by(slug = "first_post").first()
        print(post_slug)
        print(post)
        return render_template('post.html', params=params, post=post)


@app.route('/edit.html/<string:sno>', methods = ['GET','POST'])
def edit_route(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            context = request.form.get('context')
            img_name = request.form.get('img_name')
            if sno == '0':
                post = Posts(title=title, tag_line=tline, slug=slug, img_name=img_name,context = context, date=datetime.now())
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno = sno).first()
                post.title = title
                post.slug = slug
                post.context = context
                post.tag_line = tline
                db.session.commit()
                return redirect('/edit.html/'+sno)
    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html',params=params,post=post, sno = sno)




#--TOWARDS CONTACT.HTML--#
@app.route('/contact.html', methods = ['GET','POST'])
def contact():
    if (request.method == 'POST'):
        id = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone')
        message = request.form.get('message')

        #----------------CONTACT FORM ENTRY INTO THE DATABASE---------------#
        entry = Contact(id = id, email = email, phone_number = phone_number, message = message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + id,
                          sender = email,
                          recipients = [params['gmail_user']],
                          body = message + "\n" + phone_number)
    return render_template('contact.html', params=params, post = post)



@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/form.html')


@app.route('/delete/<string:sno>', methods = ['GET','POST'])
def delete(sno):
    if ('user' in session) and (session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno = sno).first()
        #print(post.sno)
        db.session.delete(post)
        db.session.commit()
        return redirect("/form.html")



#--TOWARDS INDEX.HTML--#
@app.route('/index.html')
def index():
    post = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, post = post)

app.run(debug=True)
