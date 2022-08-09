from flask import Blueprint, request
from .models import User
from werkzeug.security import generate_password_hash
from . import db
from website import Status
import json
from website import ResponseOb

auth = Blueprint('auth', __name__)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            return response('Email already exists.', Status.Status.BadRequest)
        elif len(email) < 4:
            return response('Email must be greater than 3 characters.', Status.Status.BadRequest)
        elif len(first_name) < 2:
            return response('First name must be greater than 1 character.', Status.Status.BadRequest)

        elif password1 != password2:
            return response('Passwords don\'t match.', Status.Status.BadRequest)
        elif len(password1) < 7:
            return response('Password must be at least 7 characters.', Status.Status.BadRequest)
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            return response('Created', Status.Status.Ok)

    return


def response(message: str, status: Status):
    return json.dumps(ResponseOb.ResponseOb(message).__dict__), int(status.value)
