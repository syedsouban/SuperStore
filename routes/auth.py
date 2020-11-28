import uuid
from app import app
from utils.user import get_user_by_email, get_users_by_token_and_email, get_verified_users_by_id, update_email_verify_status, update_password_by_id, update_token
from flask import request, jsonify
from models.user import User
from bson import json_util
import json

from utils.mail import send_password_reset_mail, send_verification_mail
from flask import request
import re
from constants import fields
from functools import wraps
from flask import abort,request
from constants import fields

def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):
            if not fields.SESSION_ID in request.headers:
               abort(401)
            try:
                session_id = request.headers.get(fields.SESSION_ID)
                user_session = get_active_session_by_id(session_id)
                if not user_session:
                    abort(401)
            except:
                abort(401)

            return f(user_session[fields.user_id],user_session[fields.email], *args, **kws)
    return decorated_function


def is_strong(password):
    return re.match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$", password)

@app.route("/", methods=["GET"])
def root():
    return "This is the superstore backend api"

@app.route("/register", methods=["POST"])
def new_user():
    response = {
        fields.success: False,
        fields.message: " "
    }
    password = request.json.get(fields.password)
    email = request.json.get(fields.email)

    if email is None or password is None:
        response[fields.message] = "Email or password fields are empty"
        return jsonify(response)
    if not is_strong(password):
        response[fields.message] = "Password should contain at least one small letter, one capital letter, one number and one special symbol!"
        return response
    existing_user = get_user_by_email(email)
    if existing_user is not None:
        response[fields.message] = "Email address is already taken"
        return jsonify(response)
    
    user = User(email, password)
    if user.save():
        response[fields.success] = True
        response[fields.message] = "Successfully registered the user"
        response[fields.user_id] = user.id
        send_verification_mail(email, user.verification_token)
        response = json.loads(json_util.dumps(response))
    return jsonify(response)


@app.route("/login", methods=["POST"])
def login():
    response = {
        fields.success: False,
        fields.message: " "
    }
    email = request.json.get(fields.email)
    password = request.json.get(fields.password)
    if email and password:
        user = app.mongo.db.users.find_one({fields.email: email})
        if user and User.validate_login(user["password_hash"], password):
            num_sessions = get_active_sessions_by_user_id(user[fields._id])
            if num_sessions <= 2:
                new_session = create_new_session(user[fields._id], email)
                if new_session:
                    response[fields.success] = True
                    response[fields.message] = "Successfully logged in"
                    response[fields.session_id] = new_session[fields.session_id]
                else:
                    print("unable to store user session for user: "+str(user))
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
def logout(user_id,email):
    response = {
        fields.success: False,
        fields.message: " "
    }
    if not request.get(fields.SESSION_ID):
        response[fields.message] = "Some of the header fields are missing"
    else:
        session_id = request[fields.SESSION_ID]
        update_res = update_session_id(session_id)
        if update_res.get("nModified", 0) >= 1:
            response[fields.success] = True
            response[fields.message] = "User Logged out"
        else:
            print("unable to delete user session")
            response[fields.message] = "Something went wrong"

    return jsonify(response)

@app.route("/resend_verification_mail")
@authorize
def resend_verification_mail(user_id,email):
    response = {}
    current_user = get_verified_users_by_id(user_id)
    if current_user:
        response[fields.success] = False
        response[fields.message] = "Email of the user is already verified"
    else:
        verification_token = str(uuid.uuid4())
        verification_token,verification_token_expiry = User.create_token()
        
        update_res = update_token(fields.verification_token,user_id,verification_token,verification_token_expiry)
        if update_res.get("nModified",0) == 1:
            send_verification_mail(email,verification_token)
            response[fields.success] = True
            response[fields.message] = "Verification email sent successfully"
        else:
            response[fields.success] = False
            response[fields.message] = "Could not send verification mail, try again"
        
    return response

@app.route("/verify_email/<email>/<token>")
def verify_email(email, token):
    response = {
        fields.success : False,
        fields.message : "Password reset email expired"
    }
    user_with_token = get_users_by_token_and_email(fields.verification_token,token,email)
    if user_with_token:
        update_res = update_email_verify_status(email)
        if update_res.get("nModified") == 1:
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
    
    user = get_user_by_email(email)
    if user:
        token,token_expiry = User.create_token()
        update_res = update_token(fields.password_token,user[fields._id],token,token_expiry)
        
        if update_res.get("nModified") == 1:
            send_password_reset_mail(email,token)
            response[fields.success] = True
            response[fields.message] = "Password reset instructions has been sent to your mail"
        else:
            response[fields.success] = False
            response[fields.message] = "Something went wrong, try again"
    else:
        response[fields.success] = False
        response[fields.message] = "No users associated with the given email address"
    return response

@app.route("/reset_password/<email>/<token>",methods=["GET","POST"])
def hashcode(email,token):
    user_with_token = get_users_by_token_and_email(fields.password_token,token,email)
    
    if user_with_token:
        if request.method == "POST":
            passw = request.form["passw"]
            cpassw = request.form["cpassw"]
            if passw == cpassw:
                if not is_strong(passw):
                    return "Password should contain at least one small letter, one capital letter, one number and one special symbol!"
                new_password_hash = User.generate_password_hash(passw)
                user_id = user_with_token[fields._id]
                update_res = update_password_by_id(user_id,new_password_hash)
                if update_res.get("nModified",0) == 1:        
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
from utils.session import create_new_session, get_active_sessions_by_user_id, update_session_id,get_active_session_by_id