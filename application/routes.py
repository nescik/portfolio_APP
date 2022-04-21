from application import app, db, mail
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin
import secrets
import os
from PIL import Image
from sqlalchemy.sql import func
from flask_mail import Message

from application.models import User, Photo, Comment, Rating, Tag
from application.forms import (RegisterForm, LoginForm, UpadeInfoForm, UpadeInfoForm2, AddCommentForm, RatingForm, 
                                AddPhotoForm, SearchTagForm, AddTagForm, RequestResetForm, ResetPasswordForm)

@app.route("/", methods = ['GET', 'POST'])
def main():
    """ db.create_all() """

    photos = Photo.query.order_by(Photo.data_posted.desc()).limit(10)
    users = User.query.order_by(User.join_data.desc()).limit(4)

    top = db.session.query(Photo, Rating, func.avg(Rating.rating).label('avg') ).join(Rating).filter(Photo.id == Rating.photo_id)\
        .group_by(Photo.id, Photo.name)\
            .order_by(func.avg(Rating.rating)\
                .desc()).limit(3)


    if current_user.is_authenticated and current_user.is_admin == False:
        user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    else:
        user_img = None

    return render_template("main.html", photos = photos, user_img = user_img, top = top, users = users)
    
@app.route("/more_photos", methods = ['GET', 'POST'])
def more_photos():

    count = request.form['newCount']

    photos = Photo.query.order_by(Photo.data_posted.desc()).limit(count)

    return render_template('more_photos.html', photos = photos)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    error = None

    if form.validate_on_submit():
        login = form.login.data
        email = form.email.data
        password = form.password.data
        hash_password = generate_password_hash(password, method="sha256")


        user_login_unique = (User.query.filter(User.login == form.login.data).count() == 0)
        user_email_unique = (User.query.filter(User.email == form.email.data).count() == 0)

        if not user_login_unique:
            error = 'Podany login już istnieje!'
        elif not user_email_unique:
            error = 'Podany email już istnieje!'
        
        if not error:
            new_user = User(login = login, password = hash_password, email = email, experience = '', age = '')
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
     
    return render_template("register.html", form = form, error = error)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc



@app.route("/login", methods = ['GET', 'POST'])
def login():

    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by( login=form.login.data ).first()

        if user:
            if user.is_active == True:
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)

                    next = request.args.get('next')
                    if next and is_safe_url(next):
                        return redirect(next)
                    else:
                        return redirect(url_for('main'))
                else:
                    error = "Podałeś złe hasło"
            else:
                error = "Twoje konto jest nieaktywne"
        else:
            error = "Podałeś zły login"
        

    return render_template("login.html", form = form, error = error)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main'))


@app.route("/user_dashboard")
@login_required
def user_dashboard():


    user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    return render_template("user_dashboard.html", user_img = user_img)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/pictures', picture_fn)
    
    output_size = (200,200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/user_profil", methods = ['GET', 'POST'])
@login_required
def user_profil():
    form = UpadeInfoForm()
    form2 = UpadeInfoForm2()

    form.tags.choices = [(c.id, c.name) for c in Tag.query.all()]
    
    if form.validate_on_submit():
        if form.picture.data:
            picture = save_picture(form.picture.data)
            current_user.picture = picture
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.email = form.email.data
        current_user.age = form.age.data
        current_user.experience = form.experience.data

        tags = Tag.query.all()
        accepted = []

        for tag in tags:
            if tag.id in form.tags.data:
                accepted.append(tag)
        
        current_user.tags = accepted
        db.session.commit()
        return redirect(url_for('user_profil'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.age.data = current_user.age
        form.experience.data = current_user.experience
    
    if form2.validate_on_submit():
        current_user.about = form2.about.data
        db.session.commit()

    user_tags = []
    for tag in current_user.tags:
        user_tags.append(tag.id)

    user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    return render_template("user_profil.html", form = form, form2 = form2, user_img = user_img, user_tags = user_tags)

def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_photo.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img/photos', picture_fn)
    
    output_size = (1600,1200)
    i = Image.open(form_photo)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/add_photo", methods = ['GET', 'POST'])
@login_required
def add_photo():
    form = AddPhotoForm()
    form.tags.choices = [(c.id, c.name) for c in Tag.query.all()]

    if form.validate_on_submit():
        photo = save_photo(form.photo.data)

        c_records = Tag.query.all()
        accepted = []

        for tag in c_records:
            if tag.id in form.tags.data:
                accepted.append(tag)

        new_photo = Photo(name = photo, user_id = current_user.id, tags = accepted)
        db.session.add(new_photo)
        db.session.commit()
        return redirect(url_for('add_photo'))
    
    user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    return render_template("add_photo.html", user_img = user_img, form = form)

@app.route("/photo/<int:photo_id>", methods = ['GET', 'POST'])
def photo(photo_id):
    form = AddCommentForm()
    form2 = RatingForm()

    photo = Photo.query.get_or_404(photo_id)

    if current_user.is_authenticated:

        if form.validate_on_submit():
            new_comment = Comment(content = form.comment.data, photo_id = photo_id, user_id = current_user.id)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('photo', photo_id = photo_id))

        if form2.validate_on_submit():
            new_rating = Rating(rating = form2.rating.data, photo_id = photo_id, user_id = current_user.id)
            db.session.add(new_rating)
            db.session.commit()
            return redirect(url_for('photo', photo_id = photo_id))

        user_rate = Rating.query.filter(Rating.user_id == current_user.id, Rating.photo_id == photo_id).first()
    
        if user_rate != None:
            user_rate = user_rate.rating

    else:
        user_rate = None
        url = "photo/" + str(photo_id)
        if form.is_submitted():
            return redirect(url_for('login', next = url))
        elif form2.is_submitted():
            return redirect(url_for('login', next = url))

    
    result = db.session.query(func.avg(Rating.rating)).filter(Rating.photo_id == photo_id)
    rate = result[0]
    rate = rate[0]
    if rate != None:
        rate = f"{rate:.2f}"

    return render_template("photo.html", photo = photo , title = photo.user.name, form = form, form2 = form2, rate = rate, user_rate = user_rate)

@app.route("/photos", methods = ['GET', 'POST'])
def photos():
    form = SearchTagForm()

    if current_user.is_authenticated and current_user.is_admin == False:
        user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    else:
        user_img = None

    
    form.tag.choices = [(c.id, c.name) for c in Tag.query.order_by('name')]
    if form.validate_on_submit():
        tag = Tag.query.filter(Tag.id == form.tag.data).first()
        name_tag = tag.name

        return redirect(url_for('photos_tag', user_img= user_img, form = form, name_tag = name_tag))
    elif request.method == 'GET':
        photos = Photo.query.all()

    return render_template("photos.html", user_img= user_img, photos = photos, form = form)


@app.route("/photos/tags/<name_tag>", methods = ['GET', 'POST'])
def photos_tag(name_tag):
    form = SearchTagForm()

    if current_user.is_authenticated and current_user.is_admin == False:
        user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    else:
        user_img = None

    form.tag.choices = [(c.id, c.name) for c in Tag.query.order_by('name')]
    if form.validate_on_submit():
        tag = Tag.query.filter(Tag.id == form.tag.data).first()
        name_tag = tag.name
        

        return redirect(url_for('photos_tag', user_img= user_img, form = form, name_tag = name_tag))
        
    photos = Photo.query.filter(Photo.tags.any(Tag.name == name_tag)).all()
    tag = Tag.query.filter(Tag.name == name_tag).first()    
    tag_id = tag.id

    return render_template("photos_tag.html", photos = photos, form = form, user_img = user_img, name_tag = name_tag, tag_id = tag_id)



@app.route("/rated_photos", methods = ['GET', 'POST'])
@login_required
def rated_photos():
    
    
    photos = db.session.query(Photo, Rating).join(Rating).filter(Rating.user_id == current_user.id).all()
        

    user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    return render_template("rated_photos.html", user_img = user_img, photos=photos)



@app.route("/artists", methods = ['GET', 'POST'])
def artists():

    if current_user.is_authenticated and current_user.is_admin == False:
        user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    else:
        user_img = None
    

    artists = User.query.filter(User.is_admin == False).all()

   
    return render_template('artists.html', user_img = user_img, artists = artists)

@app.route("/artist/<int:artist_id>", methods = ['GET', 'POST'])
def artist(artist_id):
    if current_user.is_authenticated and current_user.is_admin == False:
        user_img = url_for('static', filename='img/pictures/'+current_user.picture)
    else:
        user_img = None

    artist = User.query.get_or_404(artist_id)
    
    return render_template('artist.html', artist = artist, user_img = user_img)

@app.route("/admin_panel", methods = ['GET', 'POST'])
@login_required
def admin_panel():
    users = User.query.filter(User.is_admin == False).all()

    if current_user.is_authenticated and current_user.is_admin == True:
        return render_template("admin_panel.html", users = users)
    else:
        return "Nie jestes adminem!!!"

@app.route("/user_status_change/<int:user_id>", methods = ['GET', 'POST'])
@login_required
def user_status_change(user_id):

    user = User.query.get_or_404(user_id)
    if user:
        user.is_active = (user.is_active +1 ) % 2
        db.session.commit()
        return redirect(url_for('admin_panel')) 


@app.route("/delete_user/<int:user_id>", methods = ['GET', 'POST'])
@login_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin_panel'))   


@app.route("/admin_photos", methods = ['GET', 'POST'])
@login_required
def admin_photos():
    
    photos = Photo.query.all()
    c = Photo.query.count()

    if current_user.is_authenticated and current_user.is_admin == True:
        return render_template("admin_photos.html", photos = photos, c = c)
    else:
        return "Nie jestes adminem!!!"

    
@app.route("/delete_photo/<int:photo_id>", methods = ['GET', 'POST'])
@login_required
def delete_photo(photo_id):
    
    photo = Photo.query.get_or_404(photo_id)
    email = photo.user.email

    if request.method == 'POST':
        msg = request.form['reason']
        
        message = Message('Usunięto twoje zdjęcie', 
                    sender='e24546786@gmail.com', 
                    recipients=[email])

        message.body = f'''Twoje zdjęcie {photo.name} zostało usunięte z powodu:
{msg}

Administracja YOURPHOTO
'''
        mail.send(message)
        db.session.delete(photo)
        db.session.commit()
    
    return redirect(url_for('admin_photos'))

@app.route("/admin_tags", methods = ['GET', 'POST'])
@login_required
def admin_tags():
    form = AddTagForm()
    tags = Tag.query.all()

    if form.validate_on_submit():
        new_tag = Tag(name = form.name.data)
        db.session.add(new_tag)
        db.session.commit()
        return redirect(url_for('admin_tags'))

    if current_user.is_authenticated and current_user.is_admin == True:
        return render_template("admin_tags.html", tags = tags, form = form)
    else:
        return "Nie jestes adminem!!!"
    

@app.route("/delete_tag/<int:tag_id>", methods = ['GET', 'POST'])
@login_required
def delete_tag(tag_id):

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect(url_for('admin_tags'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Odzyskaj hasło', 
                    sender='e24546786@gmail.com', 
                    recipients=[user.email])

    msg.body = f'''Aby zresetować hasło, wejdz w poniższy link:
{url_for('reset_token', token = token,  _external=True)}
'''

    mail.send(msg)

@app.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by( email = form.email.data).first()
        if user is None:
            flash('Nie istnieje konto z podanym mailem.', 'danger')
        else:
            send_reset_email(user)
            flash('E-mail z instrukcja do zmiany hasła został wysłany')
            return redirect(url_for('login'))

    return render_template("reset_request.html", form=form)



@app.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):

    if current_user.is_authenticated:
        return redirect(url_for('main'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('Token nie istnieje lub wygasł', 'warning')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        password = form.password.data
        hash_password = generate_password_hash(password, method="sha256")
        user.password = hash_password
        db.session.commit()
        flash("Hasło zostało pomyślnie zmienione")
        return redirect(url_for('login'))

    return render_template("reset_token.html", form = form)
    