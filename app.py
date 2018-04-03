from flask import Flask, render_template, redirect, url_for, session,request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail,Message
from itsdangerous import URLSafeTimedSerializer,SignatureExpired,BadTimeSignature
import sqlite3 as sql


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config['SECRET_KEY'] = "thisisasecretkey"
app.secret_key = "yolosecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/codhek/Supply_Chain/dbms.db'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
mail=Mail(app)
db = SQLAlchemy(app)
Bootstrap(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='index'
s=URLSafeTimedSerializer(app.config['SECRET_KEY'])


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    email = db.Column(db.String(30))
    type = db.Column(db.String(20))
    password = db.Column(db.String(80))
    confirm_email=db.Column(db.Boolean)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.Integer)
    description = db.Column(db.String(100))
    quantity_avail = db.Column(db.String(100))
    cost_each = db.Column(db.String(100))
    min_quantity=db.Column(db.Integer)

class UpdateItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealer_id = db.Column(db.Integer)
    description = db.Column(db.String(100))
    quantity_avail = db.Column(db.String(100))
    cost_each = db.Column(db.String(100))
    min_quantity=db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    dealer_id = db.Column(db.Integer)
    quantity = db.Column(db.String(100))

class ClientDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    city = db.Column(db.String(100))
    address = db.Column(db.String(1000))
    pincode = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    state = db.Column(db.String(100))


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=90)])

class SignupFormClient(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=90)])

class SignupFormAdmin(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=90)])

class SignupFormDealer(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    username = StringField('Userame', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=90)])

class AddProductForm(FlaskForm):
    description = StringField('Name of your product', validators=[InputRequired(), Length(min=5, max=100)])
    quantity_avail = StringField('Quantity in Stock', validators=[InputRequired(), Length(min=1, max=100)])
    cost_each = StringField('Cost per product', validators=[InputRequired(), Length(min=1, max=100)])
    min_quantity=StringField('Minimum quantity',validators=[InputRequired(), Length(min=1, max=100)])

class SearchForm(FlaskForm):
    search = StringField('Search for a product', validators=[Length(min=0, max=1000)])

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=90)])
    confirm_password= PasswordField('Confirm Password', validators=[InputRequired(), Length(min=6, max=90)])

class ChangePasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=90)])
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=6, max=90)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[InputRequired(), Length(min=6, max=90)])

class QuantityForm(FlaskForm):
    quantity = StringField('Quantity', validators=[InputRequired(), Length(min=0, max=100)])

class ProfileForm(FlaskForm):
    city = StringField('City', validators=[InputRequired(), Length(min=0, max=100)])
    address = StringField('Address', validators=[InputRequired(), Length(min=0, max=100)])
    pincode = StringField('Pincode', validators=[InputRequired(), Length(min=0, max=100)])
    contact = StringField('Contact', validators=[InputRequired(), Length(min=0, max=100)])
    state = StringField('State', validators=[InputRequired(), Length(min=0, max=100)])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/client', methods=['GET', 'POST'])
def login_client():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data,type='client').first()
        if user:
            if check_password_hash(user.password, form.password.data):
                if user.confirm_email==1:
                    session['id'] = user.id
                    session['username'] = user.username
                    session['email'] = user.email
                    session['type'] = user.type
                    return redirect(url_for('dashboard_client'))
                else:
                    return render_template('login_client.html', form=form, message="** Please verify your email!")
        else:
            return render_template('login_client.html', form=form, message="** email or password for client doesn't seem right!")
    return render_template('login_client.html', form=form)

@app.route('/login/dealer', methods=['GET', 'POST'])
def login_dealer():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data,type='dealer').first()
        if user:
            if check_password_hash(user.password, form.password.data):
                if user.confirm_email==1:
                    session['id'] = user.id
                    session['username'] = user.username
                    session['email'] = user.email
                    session['type'] = user.type
                    return redirect(url_for('dashboard_dealer'))
                else:
                    return render_template('login_dealer.html', form=form, message="** Please verify your email!")
        else:
            return render_template('login_dealer.html', form=form, message="** email or password for dealer doesn't seem right!")
    return render_template('login_dealer.html', form=form)

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data,type='admin').first()
        if user:
            if check_password_hash(user.password, form.password.data):
                if user.confirm_email==1:
                    session['id'] = user.id
                    session['username'] = user.username
                    session['email'] = user.email
                    session['type'] = user.type
                    return redirect(url_for('dashboard_admin'))
                else:
                    return render_template('login_admin.html', form=form, message="** Please verify your email!")
        else:
            return render_template('login_admin.html', form=form, message="** email or password for admin doesn't seem right!")
    return render_template('login_admin.html', form=form)

###################################################

@app.route('/signup/client', methods=['GET', 'POST'])
def signup_client():
    form = SignupFormClient()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User.query.filter_by(email=form.email.data,type='client').first()
        if user:
            message = "** email already exits"
            return render_template('signup_client.html', message=message, form=form)
        else:
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, type="client",confirm_email=False)
            email=form.email.data
            token=s.dumps(email,salt='email-confirm')
            msg=Message('Confirm mail',sender='iit2016007@iiita.ac.in',recipients=[email])
            link=url_for('confirm_email',token=token,types='client',_external=True)
            msg.body='Your link is {}'.format(link)
            mail.send(msg)
            db.session.add(new_user)
            db.session.commit()
            message = "Please verify your email-id and then login"
            return render_template('signup_client.html', message=message, form=form)
            #return '<h1>email you entered is {}.the token is {}</h1>'.format(email,token)
            #return redirect(url_for('login_client'))
    return render_template('signup_client.html', form=form)

@app.route('/signup/admin', methods=['GET', 'POST'])
def signup_admin():
    form = SignupFormAdmin()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User.query.filter_by(email=form.email.data,type='admin').first()
        if user:
            message = "** email already exits"
            return render_template('signup_admin.html', message=message, form=form)
        else:
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, type="admin",confirm_email=False)
            email=form.email.data
            token=s.dumps(email,salt='email-confirm')
            msg=Message('Confirm mail',sender='iit2016007@iiita.ac.in',recipients=[email])
            link=url_for('confirm_email',token=token,types='admin',_external=True)
            msg.body='Your link is {}'.format(link)
            mail.send(msg)
            db.session.add(new_user)
            db.session.commit()
            message = "Please verify your email-id and then login"
            return render_template('signup_admin.html', message=message, form=form)
            # return '<h1>email you entered is {}.the token is {}</h1>'.format(email,token)

    return render_template('signup_admin.html', form=form)

@app.route('/signup/dealer', methods=['GET', 'POST'])
def signup_dealer():
    form = SignupFormDealer()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User.query.filter_by(email=form.email.data,type='dealer').first()
        if user:
            message = "** email already exits"
            return render_template('signup_dealer.html', message=message, form=form)
        else:
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, type="dealer",confirm_email=False)
            email=form.email.data
            token=s.dumps(email,salt='email-confirm')
            msg=Message('Confirm mail',sender='iit2016007@iiita.ac.in',recipients=[email])
            link=url_for('confirm_email',token=token,types='dealer',_external=True)
            msg.body='Your link is {}'.format(link)
            mail.send(msg)
            db.session.add(new_user)
            db.session.commit()
            message = "Please verify your email-id and then login"
            return render_template('signup_dealer.html', message=message, form=form)
            # return '<h1>email you entered is {}.the token is {}</h1>'.format(email,token)

    return render_template('signup_dealer.html', form=form)


@app.route('/confirm_email/<token>/<types>')
def confirm_email(token,types):
    try:
        email=s.loads(token,salt='email-confirm')
        user=User.query.filter_by(email=email,type=types).first()
        user.confirm_email=True
        db.session.commit()
    except SignatureExpired:
        #'The token is expired!'
        #message='expired'
        if types=='client':
            return redirect(url_for('signup_client'))
        if types=='dealer':
            return redirect(url_for('signup_dealer'))
        return redirect(url_for('signup_admin'))
    except BadTimeSignature:
        #'The token is expired!'
        #message='expired'
        if types=='client':
            return redirect(url_for('signup_client'))
        if types=='dealer':
            return redirect(url_for('signup_dealer'))
        return redirect(url_for('signup_admin'))
    if types == 'client':
        return redirect(url_for('login_client'))
    elif types == 'dealer':
        return redirect(url_for('login_dealer'))
    else:
        return redirect(url_for('login_admin'))
####################################################

@app.route('/dashboard/client', methods=['GET', 'POST'])
def dashboard_client():
    form = SearchForm()
    if 'username' in session:
        session_username = session['username']
        session_username = session_username[0].upper() + session_username[1:]
        products = Products.query.order_by(desc(Products.id))
        if form.validate_on_submit():
            searchVal = form.search.data
            products_on_search = Products.query.filter_by(description=searchVal)
            if products_on_search:
                message = "1"
                return render_template('dashboard_client.html',session_username=session_username, products=products_on_search, form=form, message=message)
            else:
                message = "0"
                return render_template('dashboard_client.html',session_username=session_username, products=products_on_search, form=form, message=message)
        else:
            message = "1"
            return render_template('dashboard_client.html',session_username=session_username, products=products, form=form, message=message)
    else:
        session_type = session['type']
        return render_template('not_logged_in.html',session_type=session_type)

@app.route('/dashboard/dealer', methods=['GET', 'POST'])
def dashboard_dealer():
    if 'username' in session:
        session_username = session['username']
        session_username = session_username[0].upper() + session_username[1:]
        orders = Order.query.filter_by(dealer_id=session['id'])
        # products = {}
        # clients = {}
        # for order in orders:
        #     product = Products.query.filter_by(id=order.product_id)
        #     products[order.product_id] = product
        #     client = ClientDetails.query.filter_by(client_id=order.client_id)
        #     clients[order.client_id] = client
            # return orders[order]
        return render_template('dashboard_dealer.html',session_username=session_username, orders=orders)
    else:
        session_type = session['type']
        return render_template('not_logged_in.html',session_type=session_type)

@app.route('/dashboard/admin', methods=['GET', 'POST'])
def dashboard_admin():
    if 'username' in session:
        session_username = session['username']
        session_username = session_username[0].upper() + session_username[1:]
        return render_template('dashboard_admin.html',session_username=session_username)
    else:
        session_type = session['type']
        return render_template('not_logged_in.html',session_type=session_type)

######################################################

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddProductForm()
    session_username = session['username']
    if form.validate_on_submit():
        dealer_id = session['id']
        new_product = Products(description=form.description.data, dealer_id=dealer_id, cost_each=form.cost_each.data, quantity_avail=form.quantity_avail.data,min_quantity=form.min_quantity.data)
        db.session.add(new_product)
        db.session.commit()
        return render_template('add_product.html', message="Product added successfully!", session_username=session_username, form=form)
    return render_template('add_product.html', session_username=session_username, form=form)


##################################################

@app.route('/forgot_password/client', methods=['GET', 'POST'])
def forgot_password_client():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        #hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User.query.filter_by(email=form.email.data,type='client').first()
        if user:
            email=form.email.data
            token=s.dumps(email,salt='forgot-password')
            msg=Message('forgot password',sender='iit2016007@iiita.ac.in',recipients=[email])
            link=url_for('password_reset',token=token,types='client',_external=True)
            msg.body='Your link is {}'.format(link)
            mail.send(msg)
            message = "** tu toh cool ban gaya!"
            return render_template('forgot_password_client.html', message=message, form=form)

        else:
            message = "** email does not exist!"
            return render_template('forgot_password_client.html', message=message, form=form)

    return render_template('forgot_password_client.html', form=form)

@app.route('/forgot_password/dealer', methods=['GET', 'POST'])
def forgot_password_dealer():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        #hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User.query.filter_by(email=form.email.data,type='dealer').first()
        if user:
            email=form.email.data
            token=s.dumps(email,salt='forgot-password')
            msg=Message('forgot password',sender='iit2016007@iiita.ac.in',recipients=[email])
            link=url_for('password_reset',token=token,types='dealer',_external=True)
            msg.body='Your link is {}'.format(link)
            mail.send(msg)
            message = "** tu toh cool ban gaya!"
            return render_template('forgot_password_dealer.html', message=message, form=form)

        else:
            message = "** email does not exit!"
            return render_template('forgot_password_dealer.html', message=message, form=form)

    return render_template('forgot_password_dealer.html', form=form)
@app.route('/forgot_password/admin', methods=['GET', 'POST'])
def forgot_password_admin():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        #hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User.query.filter_by(email=form.email.data,type='admin').first()
        if user:
            email=form.email.data
            token=s.dumps(email,salt='forgot-password')
            msg=Message('forgot password',sender='iit2016007@iiita.ac.in',recipients=[email])
            link=url_for('password_reset',token=token,types='admin',_external=True)
            msg.body='Your link is {}'.format(link)
            mail.send(msg)
            message = "** tu toh cool ban gaya!"
            return render_template('forgot_password_admin.html', message=message, form=form)

        else:
            message = "** email does not exit!"
            return render_template('forgot_password_admin.html', message=message, form=form)

    return render_template('forgot_password_admin.html', form=form)


##################################################
@app.route('/password_reset/<token>/<types>', methods=['GET', 'POST'])
def password_reset(token,types):
    form=PasswordResetForm()
    if form.validate_on_submit():
        try:
            email=s.loads(token,salt='forgot-password',max_age=3600)
            password=form.password.data
            confirm_password=form.confirm_password.data
            user=User.query.filter_by(email=email,type=types).first()
            #user.confirm_email=True
            #db.session.commit()
            #return '<h1>password if {}.confirm password is {}</h1>'.format(password,confirm_password)
            if user and password==confirm_password:
                hashed_password=generate_password_hash(form.password.data, method='sha256')
                user.password=hashed_password
                db.session.commit()
                return '<h1>done!</h1>'

            else:
                message='the password fields dont match!'
                return render_template('password_reset.html', message=message,form=form,token=token,types=types)


        except SignatureExpired:
            #'The token is expired!'
            #message='expired'
            if types=='client':
                return redirect(url_for('forgot_password_client'))
            if types=='dealer':
                return redirect(url_for('forgot_password_dealer'))
            return redirect(url_for('forgot_password_admin'))
        except BadTimeSignature:
        #'The token is expired!'
        #message='expired'
            if types=='client':
                return redirect(url_for('forgot_password_client'))
            if types=='dealer':
                return redirect(url_for('forgot_password_dealer'))
            return redirect(url_for('forgot_password_admin'))
        return '<h1>ok!</h1>'
    return render_template('password_reset.html', form=form,token=token,types=types)




##################################################
@app.route('/change_password/<types>',methods=['GET', 'POST'])
def change_password(types):
    form=ChangePasswordForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        new_password=form.new_password.data
        confirm_new_password=form.confirm_new_password.data
        user=User.query.filter_by(email=email,type=types).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                if new_password==confirm_new_password:
                    hashed_password=generate_password_hash(new_password, method='sha256')
                    user.password=hashed_password
                    db.session.commit()
                    return '<h1>done!</h1>'
                else:
                    message='**new password and confirm new password fields dont match!!'
                    return render_template('change_password.html',message=message,form=form,types=types)

            else:
                message='**wrong email or password!'
                return render_template('change_password.html',message=message,form=form,types=types)
        else:
            message='no such user exists!'
        return render_template('change_password.html',message=message,form=form,types=types)
    #return '<h1>the types is {}!</h1>'.format(types)
    return render_template('change_password.html',form=form,types=types)

##################################################
@app.route('/print_inventory')
#@login_required
def print_inventory():

    con = sql.connect("dbms.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from products")

    rows = cur.fetchall();
    return render_template("print_items.html",rows = rows)

#####################################################

@app.route('/dashboard/order/<int:product_id>', methods=['GET', 'POST'])
def order(product_id):
    form = QuantityForm()
    product = Products.query.filter_by(id=product_id).one()
    return render_template('product.html', form=form, product=product, session_username=session['username'])

@app.route('/order_confirmed/<int:product_id>', methods=['GET', 'POST'])
def confirmed_order(product_id):
    form = QuantityForm()
    profileForm = ProfileForm()
    product = Products.query.filter_by(id=product_id).one()
    if form.validate_on_submit():
        client_id = session['id']
        dealer_id = product.dealer_id
        quantity_ordered = form.quantity.data
        client_found = ClientDetails.query.filter_by(client_id=client_id).first()
        if client_found:
            if int(quantity_ordered) < int(product.quantity_avail):
                new_order = Order(client_id=client_id, product_id=product_id, dealer_id=dealer_id, quantity=quantity_ordered)
                db.session.add(new_order)
                db.session.commit()
                new_quantity = int(product.quantity_avail) - int(quantity_ordered)
                product.quantity_avail = str(new_quantity)
                db.session.commit()
                order_id = new_order.id
                #if int(product.quantity_avail) < int(product.min_quantity):
                message = "Order placed Successfully!"
                return render_template('thankyou_for_ordering.html', message=message, session_username=session['username'], order_id=order_id)
            else:
                message = "Select quantity less than " + quantity_ordered
                return render_template('product.html', form=form, message=message, product=product, session_username=session['username'])
        else:
            transaction = "incomplete"
            if int(quantity_ordered) < int(product.quantity_avail):
                new_order = Order(product_id=product_id, dealer_id=dealer_id, quantity=quantity_ordered)
                db.session.add(new_order)
                db.session.commit()
                message = "Order placed Successfully!"
                return render_template('thankyou_for_ordering.html', message=message, session_username=session['username'], order_id=order_id)
            else:
                message = "Select quantity less than " + quantity_ordered
                return render_template('product.html', form=form, message=message, product=product, session_username=session['username'])
            return render_template('profile.html',form=profileForm, session_username=session['username'], transaction=transaction)
    return render_template('product.html', form=form, product=product, session_username=session['username'])


@app.route('/dashboard/notifications')
def notifications():
    products = Products.query.filter_by(dealer_id=session['id'])
    return render_template('notifications_dealer.html', products=products, session_username=session['username'])

@app.route('/history')
def history():
    my_orders = Order.query.filter_by(client_id=session['id'])
    list_of_products = []
    for each_order in my_orders:
        product_data = Products.query.filter_by(id=each_order.product_id)
        list_of_products.append(product_data)

    return render_template('history_client.html', session_username=session['username'], my_orders=my_orders, list_of_products=list_of_products)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = ProfileForm()
    transaction = "complete"
    if form.validate_on_submit():
        save_profile = ClientDetails(city=form.city.data, client_id=session['id'], address=form.address.data, pincode=form.pincode.data, state=form.state.data, contact=form.contact.data)
        db.session.add(save_profile)
        db.session.commit()
        return render_template('profile.html', form=form, session_username=session['username'], transaction=transaction)
    return render_template('profile.html', form=form, session_username=session['username'], transaction=transaction)

@app.route('/save', methods=['GET', 'POST'])
def save():
    form = ProfileForm()
    if form.validate_on_submit():
        save_profile = ClientDetails(city=form.city.data, client_id=session['id'], address=form.address.data, pincode=form.pincode.data, state=form.state.data, contact=form.contact.data)
        db.session.add(save_profile)
        db.session.commit()
        return redirect(url_for('dashboard_client'))


##################################################
# @app.route('/update_item')
# def update_item():
#     form=
##################################################
@app.route('/logout')
# @login_required
def logout():
    if 'type' in session:
        if session['type'] == 'client':
            session.pop('username', None)
            return redirect(url_for('index'))
        elif session['type'] == 'dealer':
            session.pop('username', None)
            return redirect(url_for('index'))
        elif session['type'] == 'admin':
            session.pop('username', None)
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)