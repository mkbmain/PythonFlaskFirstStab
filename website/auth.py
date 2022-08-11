from flask import Blueprint, request, current_app
from .models import User, LoginAttempts
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import jwt
from website import Status
import json
import datetime
from website import ResponseOb

auth = Blueprint('auth', __name__)


@auth.route('/sign-up', methods=['POST'])
def sign_up():
    if request.content_type != 'application/json' or request.content_length < 1:
        return response('Body required and content type must be set to application/json', None,
                        Status.Status.BadRequest)
    lookup = {k.lower(): v for k, v in request.get_json().items()}
    email = lookup.get("email", "")
    first_name = lookup.get("firstname", "")
    password1 = lookup.get('password1', "")
    password2 = lookup.get('password2', "")

    user = User.query.filter_by(email=email).first()
    if user:
        return response('Email already exists.', None, Status.Status.BadRequest)
    if len(email) < 4:
        return response('Email must be greater than 3 characters.', None, Status.Status.BadRequest)
    if len(first_name) < 2:
        return response('First name must be greater than 1 character.', None, Status.Status.BadRequest)

    if password1 != password2:
        return response('Passwords don\'t match.', None, Status.Status.BadRequest)
    if len(password1) < 7:
        return response('Password must be at least 7 characters.', None, Status.Status.BadRequest)

    new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return response('Created', "Success", Status.Status.Ok)


@auth.route('/login', methods=['POST'])
def login():
    if request.content_type != 'application/json' or request.content_length < 1:
        return response('Body required and content type must be set to application/json', Status.Status.BadRequest)
    lookup = {k.lower(): v for k, v in request.get_json().items()}
    email = lookup.get("email", "")
    password = lookup.get('password', "")
    if len(email) < 4:
        return response('Email must be greater than 3 characters.', None, Status.Status.BadRequest)
    if len(password) < 7:
        return response('Password must be at least 7 characters.', None, Status.Status.BadRequest)

    user = User.query.filter_by(email=email).first()
    if user is None:
        return response('User not found or password wrong!', None, Status.Status.BadRequest)

    if not check_password_hash(user.password, password):
        db.session.add(LoginAttempts(user_id=user.id, success=False))
        db.session.commit()
        return response('User not found or password wrong!', None, Status.Status.BadRequest)

    token = jwt.encode({'public_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                       current_app.config['SECRET_KEY'])
    db.session.add(LoginAttempts(user_id=user.id, success=True))
    db.session.commit()
    return response("", token, Status.Status.Ok)


def response(message: str, data: str, status: Status):
    return json.dumps(ResponseOb.ResponseOb(message, data).__dict__), int(status.value)