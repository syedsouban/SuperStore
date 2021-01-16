from flask.templating import render_template_string
from werkzeug.utils import html
from routes.product import search_products
from utils.session import authorize_web, get_active_session_by_id
from app import app
from flask import session, redirect, url_for, render_template, request, Blueprint
from forms.forms import LoginForm, SigninForm
from routes.auth import handle_login
from utils._json import handle_mongoengine_response

bp = Blueprint('chat', __name__, url_prefix='/socket_io')

@bp.route('/login', methods=['GET', 'POST'])
def web_login():
    """Login form to enter a room."""
    form = SigninForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        login_response = handle_login(email,password).get_json()
        if login_response.get("success",False):
            session['id'] = login_response["session_id"]
            session['name'] = email
            return redirect(url_for('chat.list_products'))
        else:
            return redirect(url_for('chat.web_login'))
    elif request.method == 'GET':
        session_id = session.get("id")
        if session_id:
            user_session = get_active_session_by_id(session_id)
            if user_session:
                return redirect(url_for('chat.list_products'))
            else:
                return redirect(url_for('chat.web_login'))
    return render_template('login.html', form=form)

@bp.route('/list_products')
@authorize_web
def list_products():
    try:
        user_id = session['user_id']
        email = session['email']
        html_res = "<html>"
        products = handle_mongoengine_response(search_products().get_json())
        for product in products:
            pname = product['english_name']
            pid = product['_id']
            url = url_for("chat.chat")
            # session['product_id'] = pid
            html_res+='<a href="%s">'%url+pname+"</a><br>"
        html_res += "</html>"
        return html_res
    except:
        import traceback
        print(traceback.format_exc())
    return ""

# @bp.route('/', methods=['GET', 'POST'])
# def index():
#     """Login form to enter a room."""
#     form = LoginForm()
#     if form.validate_on_submit():
#         session['name'] = form.name.data
#         session['room'] = form.room.data
#         return redirect(url_for('chat.chat'))
#     elif request.method == 'GET':
#         form.name.data = session.get('name', '')
#         form.room.data = session.get('room', '')
#     return render_template('index.html', form=form)


@bp.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('chat.index'))
    return render_template('chat.html', name=name, room=room)
