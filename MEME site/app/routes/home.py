import os
import uuid
import requests
from io import BytesIO
from flask import Blueprint, render_template, flash, request, redirect, url_for, send_file
import cloudinary
import cloudinary.uploader

from app.models import Post
from app import db

# Clean Blueprint definition using default template routing
home = Blueprint('home', __name__)

@home.route('/')
def index():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

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
            allowed_ext = ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.jfif']

            if ext.lower() in allowed_ext:
                cloudinary.config(
                    cloud_name="qpf3nomd",
                    api_key="865614548478618",
                    api_secret="jyin_T9TRUI0E1HPv5qDbepmV10",
                    secure=True
                )
                upload_result = cloudinary.uploader.upload(meme)
                meme_url = upload_result.get('secure_url')
            else:
                flash('Only Images!', 'danger')
                return redirect(url_for('home.upload'))
        
        token = str(uuid.uuid4())
        post = Post(title=title, meme=meme_url, delete_token=token)
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('home.index', created_id=post.id, token=token))

@home.route('/del_post/<int:id>', methods=['POST'])
def del_post(id):
    token = request.form.get('token')
    post = Post.query.get_or_404(id)
    
    if post.delete_token != token:
        flash('Unauthorized! You can only delete your own posts.', 'danger')
        return redirect(url_for('home.index'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('home.index'))

@home.route('/download/<int:post_id>')
def download(post_id):
    post = Post.query.get_or_404(post_id)
    
    response = requests.get(post.meme)
    if response.status_code == 200:
        image_stream = BytesIO(response.content)
        ext = os.path.splitext(post.meme.split('?')[0])[1] or '.jpg'
        filename = f"{post.title}{ext}"
        
        return send_file(
            image_stream,
            as_attachment=True,
            download_name=filename,
            mimetype=response.headers.get('Content-Type', 'image/jpeg')
        )
    
    flash("Failed to download image.", "danger")
    return redirect(url_for('home.index'))

@home.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@home.route('/about')
def about():
    return render_template('about.html')