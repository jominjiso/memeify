import os
import requests
from io import BytesIO
from flask import (
    Blueprint,
    render_template,
    flash,
    request,
    redirect,
    url_for,
    current_app,
    send_file
)
from flask_login import login_required, current_user, logout_user
import cloudinary
import cloudinary.uploader

from app.models import Post
from app import db

home = Blueprint('home', __name__, template_folder='templates', static_folder='static', static_url_path='/app')

# Configure Cloudinary credentials (spaces removed)
cloudinary.config(
    cloud_name="qpf3nomd",
    api_key="865614548478618",
    api_secret="jyin_T9TRUI0E1HPv5qDbepmV10",
    secure=True
)

@home.route('/')
@login_required
def index():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@home.route('/upload', methods=['GET', 'POST'])
@login_required
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
                upload_result = cloudinary.uploader.upload(meme)
                meme_url = upload_result.get('secure_url')
            else:
                flash('Only Images!', 'danger')
                return redirect(url_for('home.upload'))
        
        post = Post(title=title, meme=meme_url, created_user=current_user.id)
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('home.index'))

@home.route('/del_post/<int:id>')
@login_required
def del_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', "success")
    return redirect(url_for('home.index'))

@home.route('/fav/<int:post_id>')
@login_required
def fav(post_id):
    post = Post.query.get_or_404(post_id)

    if post in current_user.favorited_posts:
        current_user.favorited_posts.remove(post)
        flash("Removed from favorites!", "danger")
    else:
        current_user.favorited_posts.append(post)
        flash("Added to favorites!", "success")
    
    db.session.commit()
    return redirect(url_for('home.index'))

@home.route('/favorites')
@login_required
def favorites():
    post = current_user.favorited_posts
    return render_template('favs.html', post=post)

@home.route('/download/<int:post_id>')
@login_required
def download(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Fetch image bytes directly from Cloudinary URL
    response = requests.get(post.meme)
    if response.status_code == 200:
        image_stream = BytesIO(response.content)
        
        # Determine extension from Cloudinary URL or fall back to .jpg
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