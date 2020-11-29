from mongoengine.queryset.visitor import Q
from utils.time import get_time_after
from models.session import UserSessions
import traceback
from utils.misc import get_or_none
import uuid
from datetime import date, datetime

from app import app
from flask import request, jsonify
from models.user import Users
from bson import json_util
import json

from utils.mail import send_password_reset_mail, send_verification_mail
from flask import request
import re
from constants import fields
from functools import wraps
from flask import abort, request
from constants import fields


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if fields.SESSION_ID not in request.headers:
            abort(401)
        try:
            session_id = request.headers.get(fields.SESSION_ID)
            user_session: UserSessions = get_or_none(
                UserSessions.objects(Q(session_id=session_id) & Q(is_active=True) & Q(expiry_date__gte=datetime.now())))
            if not user_session:
                abort(401)
        except:
            print(traceback.format_exc())
            abort(401)

        return f(user_session.user_id.id, user_session.email, *args, **kws)

    return decorated_function


def is_strong(password):
    return re.match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$", password)


@app.route("/", methods=["GET"])
def root():
    return "This is the superstore backend api"


@app.route("/register", methods=["POST"])
def register_api():
    response = {
        fields.success: False,
        fields.message: "Something went wrong"
    }
    try:

        password = request.get_json().get(fields.password)
        email = request.get_json().get(fields.email)

        if email is None or password is None:
            response[fields.message] = "Email or password fields are empty"
            return jsonify(response)
        if not is_strong(password):
            response[
                fields.message] = "Password should contain at least one small letter, one capital letter, one number " \
                                  "and one special symbol! "
            return response
        existing_user = get_or_none(Users.objects(email=email))
        if existing_user is not None:
            response[fields.message] = "Email address is already taken"
            return response
        payload = request.get_json()
        payload = Users.create_user_data(payload)

        user: Users = Users(**payload).save()

        if user:
            response[fields.success] = True
            response[fields.message] = "Successfully registered the user"
            response[fields.user_id] = user.id
            send_verification_mail(email, user.verification_token)
            response = json.loads(json_util.dumps(response))
        else:
            return response
        return jsonify(response)
    except:
        print(traceback.format_exc())
        return response


@app.route("/login", methods=["POST"])
def login():
    response = {
        fields.success: False,
        fields.message: " "
    }
    email = request.json.get(fields.email)
    password = request.json.get(fields.password)
    if email and password:
        user = get_or_none(Users.objects(email=email))
        if user and Users.validate_login(user["password_hash"], password):
            num_sessions = UserSessions.objects.filter(Q(user_id=user.id)&Q(expiry_date__gte=datetime.now())&Q(is_active=True)).count()
            if num_sessions <= 2:
                new_session = UserSessions.create_new_session(user.id, email)
                if new_session:
                    response[fields.success] = True
                    response[fields.message] = "Successfully logged in"
                    response[fields.session_id] = new_session[fields.session_id]
                else:
                    print("unable to store user session for user: " + str(user))
                    response[fields.message] = "Unable to login"
            else:
                response[fields.message] = "Sessions limit reached"
        else:
            response[fields.message] = "Incorrect email or password"
    else:
        response[fields.message] = "Username or password not entered"
    return jsonify(response)


@app.route("/logout")
@authorize
def logout(user_id, email):
    response = {
        fields.success: False,
        fields.message: " "
    }

    if not request.headers.get(fields.SESSION_ID):
        response[fields.message] = "Some of the header fields are missing"
    else:
        session_id = request.headers.get(fields.SESSION_ID)
        n_sessions_updated = UserSessions.objects(session_id=session_id).update_one(set__is_active=False,
                                                                                    set__expireAt=get_time_after(
                                                                                        days=15))
        if n_sessions_updated >= 1:
            response[fields.success] = True
            response[fields.message] = "User Logged out"
        else:
            print("unable to delete user session")
            response[fields.message] = "Something went wrong"

    return jsonify(response)


@app.route("/resend_verification_mail")
@authorize
def resend_verification_mail(user_id, email):
    response = {}
    current_user = get_or_none(Users.objects(Q(id=user_id) & Q(email_verified=True)))
    if current_user:
        response[fields.success] = False
        response[fields.message] = "Email of the user is already verified"
    else:
        verification_token = str(uuid.uuid4())

        verification_token, verification_token_expiry = Users.create_token()

        num = Users.objects(id=user_id).update_one(set__verification_token=verification_token,
                                                   set__verification_token_expiry=verification_token_expiry)
        if num == 1:
            send_verification_mail(email, verification_token)
            response[fields.success] = True
            response[fields.message] = "Verification email sent successfully"
        else:
            response[fields.success] = False
            response[fields.message] = "Could not send verification mail, try again"

    return response


@app.route("/verify_email/<email>/<token>")
def verify_email(email, token):
    response = {
        fields.success: False,
        fields.message: "Password reset email expired"
    }
    # the next two statements need to be atomic I guess
    user_with_token = get_or_none(
        Users.objects(Q(verification_token=token) & Q(email=email) & Q(verification_token_expiry__gte=datetime.now())))

    if user_with_token:
        n_users_updated = Users.objects(email=email).update_one(set__email_verified=True)
        if n_users_updated == 1:
            response[fields.success] = True
            response[fields.message] = "Email address verified successfully"
    else:
        response[fields.success] = False
        response[fields.message] = "Could not verify the email address"
    return response


@app.route("/send_password_reset/")
def send_password_reset():
    email = request.get_json().get(fields.email)
    response = {}
    if not email:
        response[fields.success] = False
        response[fields.message] = "Email not passed"

    user = get_or_none(Users.objects(email=email))
    if user:
        token, token_expiry = Users.create_token()
        num = Users.objects(id=user.id).update_one(set__password_verification_token=token,
                                                   set__password_verification_token_expiry=token_expiry)

        if num == 1:
            send_password_reset_mail(email, token)
            response[fields.success] = True
            response[fields.message] = "Password reset instructions has been sent to your mail"
        else:
            response[fields.success] = False
            response[fields.message] = "Something went wrong, try again"
    else:
        response[fields.success] = False
        response[fields.message] = "No users associated with the given email address"
    return response


@app.route("/reset_password/<email>/<token>", methods=["GET", "POST"])
def hashcode(email, token):
    
    user_with_token = get_or_none(Users.objects(Q(password_verification_token=token) & Q(email=email) & Q(
        password_verification_token_expiry__gte=datetime.now())))

    if user_with_token:
        if request.method == "POST":
            passw = request.form["passw"]
            cpassw = request.form["cpassw"]
            if passw == cpassw:
                if not is_strong(passw):
                    return "Password should contain at least one small letter, one capital letter, one number and one " \
                           "special symbol! "
                new_password_hash = Users.generate_password_hash(passw)
                user_id = user_with_token.id
                
                num = Users.objects(id=user_id).update_one(set__password_hash=new_password_hash,
                                                           set__password_verification_token=datetime.now())

                if num == 1:
                    return "Password changed successfully"

            else:
                return """
                    Passwords do not match <br>
                    <form method="post">
                        <small>enter your new password</small> <br>
                        <input type=password name="passw" id="passw" placeholder=password> <br>
                        <input type=password name="cpassw" id="cpassw" placeholder="confirm password"> <br>
                        <input type="submit" value="Submit">
                    </form>
                """
        else:
            return """
                <form method="post">
                    <small>enter your new password</small> <br>
                    <input type=password name="passw" id="passw" placeholder=password> <br>
                    <input type=password name="cpassw" id="cpassw" placeholder="confirm password"> <br>
                    <input type="submit" value="Submit">
                </form>
            """
    else:
        return "Password recovery email expired!"
