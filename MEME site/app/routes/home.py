from flask import Blueprint,render_template,flash,request,redirect,url_for,current_app,send_from_directory
from flask_login import login_required,current_user,logout_user
import os,uuid
from app.models import Post
from app import db
import cloudinary
import cloudinary.uploader


home = Blueprint('home',__name__,template_folder='templates',static_folder='static',static_url_path='/app')


@home.route('/')
@login_required
def index():
    posts = Post.query.all()   
    return render_template('home.html',posts=posts)

import os
import cloudinary
import cloudinary.uploader
from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import current_user
# Make sure to import your db and Post model at the top of your file

# Configure Cloudinary credentials
cloudinary.config(
    cloud_name = "qpf3nomd",
    api_key = "865614548478618",
    api_secret = "jyin_T9TRUI0E1HPv5qDbepmV10",
    secure = True
)

@home.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    
    elif request.method == 'POST':
        title = request.form.get('title')
        meme = request.files.get('meme')

        meme_url = None

        if meme and meme.filename != '':
            ext = os.path.splitext(meme.filename)[1]
            allowed_ext = ['.jpg','.jpeg','.png','.webp','.heic','.jfif']

            if ext.lower() in allowed_ext:
                # Upload the file directly to Cloudinary
                upload_result = cloudinary.uploader.upload(meme)
                
                # Get the permanent HTTPS URL from Cloudinary
                meme_url = upload_result.get('secure_url')
            else:
                flash('Only Images!', 'danger')
                return redirect(url_for('home.upload')) 
        
        # Save the full URL directly to the database instead of a filename
        post = Post(title=title, meme=meme_url, created_user=current_user.id)
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('home.index'))

@home.route('/del_post/<int:id>')
def del_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!',"success")
    return redirect(url_for('home.index'))

@home.route('/fav/<int:post_id>')
def fav(post_id):
    post = Post.query.get_or_404(post_id)

    if post in current_user.favorited_posts:
          current_user.favorited_posts.remove(post)
          flash("Removed from favorites!", "danger")
    else:
         current_user.favorited_posts.append(post)
         flash("added to favorites","success")
    db.session.commit()
    
    return redirect(url_for('home.index'))

@home.route('/favorites')
@login_required
def favorites():

    post = current_user.favorited_posts

    return render_template(
        'favs.html',
        post=post
    )

from flask import send_from_directory
import os

@home.route('/download/<int:post_id>')
@login_required
def download(post_id):

    post = Post.query.get_or_404(post_id)

    meme_folder = os.path.join(
        current_app.root_path,
        'static',
        'imgs',
        'memes'
    )

    extention = os.path.splitext(post.meme)[1]

    filename =f'{post.title}{extention}' 

    return send_from_directory(
        meme_folder,
        post.meme,
        as_attachment=True,
        download_name = filename
    )
@home.route('/post/<int:post_id>')
def view_post(post_id):

    post = Post.query.get_or_404(post_id)

    return render_template(
        'post.html',
        post=post
    )

     


     
        