import os
import uuid
import requests
from io import BytesIO
from flask import Blueprint, render_template, flash, request, redirect, url_for, send_file,session
import cloudinary
import cloudinary.uploader
from sqlalchemy import func, or_

from app.models import Post
from app import db


# Clean Blueprint definition using default template routing
home = Blueprint('home', __name__)

@home.route('/', methods=['GET', 'POST'])
def index():
    selected_category = request.args.get('cat')
    srch = request.args.get('srch')

    query = Post.query.order_by(Post.click.desc())

    # 1. Apply search filter if present
    if srch and srch.strip():
        search_term = f"%{srch.strip()}%"
        query = query.filter(
            or_(
                Post.title.ilike(search_term),
                Post.category.ilike(search_term)
            )
        )

    # 2. Apply category filter if present (chains onto search query!)
    if selected_category and selected_category.strip():
        query = query.filter(Post.category == selected_category.strip())

    # 3. Execute the combined query ONCE
    posts = query.all()

    return render_template('home.html', posts=posts, srch=srch, selected_category=selected_category)

@home.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    
    elif request.method == 'POST':
        title = request.form.get('title')
        meme = request.files.get('meme')
        # Default to '💀BRUH' if category form field is empty
        category = request.form.get('category') or '💀BRUH'
        meme_url = None

        if meme and meme.filename != '':
            ext = os.path.splitext(meme.filename)[1]
            allowed_ext = ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.jfif']

            if ext.lower() in allowed_ext:
                cloudinary.config(
                    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "qpf3nomd"),
                    api_key=os.getenv("CLOUDINARY_API_KEY", "865614548478618"),
                    api_secret=os.getenv("CLOUDINARY_API_SECRET", "jyin_T9TRUI0E1HPv5qDbepmV10"),
                    secure=True
                )
                upload_result = cloudinary.uploader.upload(meme)
                meme_url = upload_result.get('secure_url')
            else:
                flash('Only Images!', 'danger')
                return redirect(url_for('home.upload'))
        
        token = str(uuid.uuid4())
        post = Post(title=title, meme=meme_url, delete_token=token, category=category)
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

    viewed = session.get('viewed_post', [])

    if post.click is None:
        post.click = 0

    if post_id not in viewed:
        post.click += 1
        db.session.commit()
        viewed.append(post_id)
        session['viewed_post'] = viewed

    return render_template('post.html', post=post)

@home.route('/about')
def about():
    return render_template('about.html')

@home.route('/meme-roulette')
def meme_roulette():
    post = Post.query.order_by(func.random()).first_or_404()
    return redirect(url_for('home.view_post', post_id=post.id))