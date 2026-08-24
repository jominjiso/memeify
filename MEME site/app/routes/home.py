from flask import Blueprint,render_template,flash,request,redirect,url_for,current_app,send_from_directory
from flask_login import login_required,current_user,logout_user
import os,uuid
from app.models import Post
from app import db


home = Blueprint('home',__name__,template_folder='templates',static_folder='static',static_url_path='/app')

@home.route('/')
@login_required
def index():
    posts = Post.query.all()   
    return render_template('home.html',posts=posts)

@home.route('/upload',methods=['GET','POST'])
def upload():
        if request.method == 'GET':
            return render_template('upload.html')
        elif request.method == 'POST':
            title = request.form.get('title')
            meme = request.files.get('meme')

            meme_filename = None

            if meme and meme.filename != '':
                ext = os.path.splitext(meme.filename)[1]

                allowed_ext = ['.jpg','.jpeg','.png','.webp','.heic','.jfif']

                if ext.lower() in allowed_ext:
                    meme_filename = f'{uuid.uuid4().hex}{ext}'
                    save_path = os.path.join(current_app.root_path,'static','imgs','memes',meme_filename)
                    meme.save(save_path)
                else:
                    flash('Only Images!','danger')
                    return redirect(url_for('home.upload')) 
            post =  Post(title=title,meme=meme_filename,created_user=current_user.id)
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

     


     
        