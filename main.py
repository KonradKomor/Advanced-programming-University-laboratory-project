from flask import Flask, url_for, redirect, render_template,send_from_directory
from flask_uploads import UploadSet, IMAGES, configure_uploads
from authlib.integrations.flask_client import OAuth
from requests import *
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import os
app = Flask(__name__)
app.secret_key = 'seed'
app.config['UPLOADED_PICS_DEST'] = 'pics'

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='377006915377-gooljkgoj69ltjnrjgrhqpdavkhva0s8.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
)


@app.route('/main')
def helloWorld():
    email = dict(session).get('email', None)
    return f'Hello, {email}'


@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_url = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_url)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['email'] = user_info['email']
    return redirect('/main')


pics = UploadSet('pics', IMAGES)
configure_uploads(app, pics)


class UploadForm(FlaskForm):
    pic = FileField(
        validators=[
            FileAllowed(pics, 'test'),
            FileRequired("wypełnij")
        ]
    )
    submit = SubmitField('Wrzuć zdjęcie')


@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PICS_DEST'], filename)


@app.route('/image', methods=['GET', 'POST'])
def uploadImage():
    form = UploadForm()
    if form.validate_on_submit():
        filename = pics.save(form.pic.data)
        file_url = url_for('get_file', filename=filename)
    else:
        file_url = None
    return render_template('index.html', form=form, file_url=file_url)