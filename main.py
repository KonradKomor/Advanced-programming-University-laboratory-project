# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from datetime import datetime
from flask import Flask, url_for, render_template, send_from_directory, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import SubmitField
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
import numpy as np
import cv2
import time
from sympy import *

app = Flask(__name__, template_folder='./swagger/templates')
app.secret_key = 'seed'
app.config['UPLOADED_PICS_DEST'] = 'pics'
app.config['JWT_SECRET_KEY'] = 'secret-secret'
jwt = JWTManager(app)
USERS = {
    "test1": 'Haslo1',
    "test2": 'Haslo2',
    "test3": 'Haslo3'
}
pics = UploadSet('pics', IMAGES)
configure_uploads(app, pics)

spec = APISpec(
    title='flask-api-swagger-doc',
    version='1.0.0',
    openapi_version='3.0.2',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)


@app.route('/docs/api/swagger.json')
def create_swagger_spec():
    return jsonify(spec.to_dict())


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


@app.route('/picture/invert', methods=['GET', 'POST'])
def uploadImage():
    form = UploadForm()
    if form.validate_on_submit():
        filename = pics.save(form.pic.data)
        name = 'pics/' + filename
        img = cv2.imread('pics//' + filename)
        inverted = np.invert(img)
        cv2.imwrite(name, inverted)

        time.sleep(5)
        file_url = url_for('get_file', filename=filename)
    else:
        file_url = None
    return render_template('image.html', form=form, file_url=file_url)


@app.route('/prime/<number>')
def isPrime(number):
    if simplify(number).is_prime == True:
        return "Liczba jest liczbą pierwszą"
    if simplify(number).is_prime == False:
        return "Liczba nie jest liczbą pierwszą"


@app.route('/register', methods=['POST'])
def register():
    """
        User registration method.
        ---
        post:
            description: Registrate user
            parameters:
              - name: username
                in: formData
                type: string
                required: true
              - name: password
                in: formData
                type: string
                required: true
            responses:
              200:
                description: User registration succesful.
              400:
                description: User registration failed.
        """
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    USERS.update({username: password})
    return 'Zarejestrowano'


@app.route('/login', methods=['POST'])
def login():
    """
        User authenticate method.
        ---
        post:
            description: Authenticate user with supplied credentials.
            parameters:
              - name: username
                in: formData
                type: string
                required: true
              - name: password
                in: formData
                type: string
                required: true
            responses:
              200:
                description: User successfully logged in.
              400:
                description: Brak hasła lub emaila.
              404:
                description: Brak takiego użytkownika
        """
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            return 'Wpisz email', 400
        if not password:
            return 'Wpisz haslo', 400

        userPassword = USERS[username]
        if not userPassword:
            return 'Brak takiego użytkownika', 404

        if userPassword == password:
            access_token = create_access_token(identity={"username": username})
            return {"access_token": access_token}, 200
        else:
            return 'błędne dane logowania!', 400
    except AttributeError:
        return 'Podaj hasło i email w formacie JSON!', 400


@app.route('/time', methods=['GET'])
@jwt_required()
def check():
    x=str(datetime.now())
    return x


with app.test_request_context():
    spec.path(view=login)
    spec.path(view=register)


@app.route('/docs/<path:path>')
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs')
    else:
        return send_from_directory('./swagger/static', secure_filename(path))
