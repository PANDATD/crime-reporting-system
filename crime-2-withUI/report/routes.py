import os
import secrets
import smtplib
import imghdr
from email.message import EmailMessage
from PIL import Image
from flask import render_template, url_for, flash, redirect, request ,abort
from urllib.parse import urlparse
from report import app, db, bcrypt 
from report.forms import *
from report.models import User, Report 
from flask_login import login_user, current_user, logout_user, login_required  
from flask_mail import Message

flag = 0

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page' , 1 , type=int)
    reports = Report.query.order_by(Report.date_reported.desc()).paginate(page = page , per_page=5)
    return render_template('home.html', reports=reports)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, phone_no = form.phone_no.data , password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)





@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if current_user.id == 1:
                return redirect(url_for('admin'))
            next_page = request.args.get('next')
            if next_page:
                parsed_url = urlparse(next_page)
                if not parsed_url.netloc and not parsed_url.scheme:
                    return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if current_user.is_authenticated():
       return redirect(url_for('admin/user/index.html'))
    else:
        return redirect(url_for('login'))



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.phone_no = form.phone_no.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone_no.data = current_user.phone_no
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)




@app.route("/report/new", methods=['GET', 'POST'])
@login_required
def new_report():
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(title=form.title.data, content=form.content.data , author=current_user)
        db.session.add(report)
        db.session.commit()
        flash('Your report has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_report.html', title='New report',
                           form=form, legend='New report')


@app.route("/report/<int:report_id>")
def report(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('report.html', title=report.title, report=report)


@app.route("/report/<int:report_id>/update", methods=['GET', 'POST'])
@login_required
def update_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)
    form = ReportForm()
    if form.validate_on_submit():
        report.title = form.title.data
        report.content = form.content.data
        db.session.commit()
        flash('Your report has been updated!', 'success')
        return redirect(url_for('report', report_id=report.id))
    elif request.method == 'GET':
        form.title.data = report.title
        form.content.data = report.content
    return render_template('create_report.html', title='Update report',
                           form=form, legend='Update report')


@app.route("/report/<int:report_id>/delete", methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.author != current_user:
        abort(403)
    db.session.delete(report)
    db.session.commit()
    flash('Your report has been Deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_reports(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    reports = Report.query.filter_by(author=user)\
        .order_by(Report.date_reported.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_reports.html', reports=reports, user=user)



def send_reset_email(user):
    token = user.get_reset_token()
    # EMAIL_ADDRESS = os.environ['EMAIL']
    # EMAIL_PASSWORD = os.environ['E_PASSWORD']
    
    EMAIL_ADDRESS = 'crime.report.ghule.@gmail.com'
    EMAIL_PASSWORD = 'v658734657543276kreg'

    msg = EmailMessage()
    msg['Subject'] = 'Password Reset'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = [user.email]

    msg.set_content(f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}


If you did not make this request then simply ignore this email and no changes will be made.
''')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password. Check spam folder also.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', form=form)


#to e just copy from documentation
@app.errorhandler(404)
def error_404(e):
    return render_template('errors/404.html') , 404

@app.errorhandler(403)
def error_403(e):
    return render_template('errors/403.html') , 403

@app.errorhandler(500)
def error_500(e):
    return render_template('errors/500.html') , 500


