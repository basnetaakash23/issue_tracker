import os
import flask
from flask import Flask, jsonify, request, abort, make_response, render_template, redirect, flash, session, url_for
from flask_pymongo import PyMongo, ObjectId # flask.ext.pymongo deprecated
from flask_cors import CORS, cross_origin
from flask_login import LoginManager , login_required , UserMixin , login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
# app = Flask(__name__, template_folder='../templates')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
# Allow CORS
CORS(app)

# Load Config File for DB
#app.config.from_pyfile('config.cfg')
app.config["MONGO_URI"]='mongodb://localhost:27017/python-mongo'
mongo = PyMongo(app)

# App Root
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

login = LoginManager(app)
login.login_view = 'login'

class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

@login.user_loader
def load_user(username):
    u = mongo.db.account.find_one({"username": username})
    if not u:
        return None
    return User(username=u['username'])

user = mongo.db.account
user.insert_one({'username':'aakash23','password':'iloveyou123'})


# @app.route('/login', methods = ["GET","POST"])
@app.route('/')
@app.route('/login', methods = ["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('get_users'))
    if(request.method == "POST"):
        user_name = request.form.get("username")
        pass_word = request.form.get("password")
        user = mongo.db.account
        q = user.find_one({'username':user_name})
        if(q and q["password"]== pass_word):
            user_obj = User(username = q['username'])
            login_user(user_obj)
            next_page = request.args.get('next')
            print("Next_Page",next_page)
            if not next_page:
                # return render_template('new_issue.html')
                print("Inside here")
                next_page = url_for('get_users')

            print("Loggin in\n")
            return redirect((next_page))
            return render_template('new_issue.html')

    print("Could not log in\n")

    return render_template('login.html')

@app.route('/new_issue.html/')
@login_required
def home():
    # return render_template('new_issue.html',header='All the users', sub_header='All the languages our users like',
    #                    users=get_all_users())
    return render_template('new_issue.html')

#this is called when a user tries to make any changes to existing data
@app.route('/new_issue.html/<id>')
@login_required
def post_updateddata(id):
    # return render_template('new_issue.html',header='All the users', sub_header='All the languages our users like',
    #                    users=get_all_users())
    if(id=="new_issue.html"):
        return redirect("http://127.0.0.1:5000/")

    user = mongo.db.users
    q = user.find_one({'_id': ObjectId(id)})
    return render_template('new_issue.html',user = q)

# List All Users. Its a home screen
@app.route('/index.html', methods=['GET'])
@login_required
def get_users():
    return render_template('index.html',header='All the users', sub_header='All the languages our users like',
                       users=get_all_users())
    # return jsonify(get_all_users())

def get_all_users():
    user = mongo.db.users
    l = user.count_documents({})
    print(l)
    #user = mongo.db.users
    #user.insert_one(users_info)
    output = []
    for q in user.find():
        output.append({'_id': str(q['_id']), 'issue': q['issue'], 'count': q['count'],'subject':q['subject'],'description':q['description'],'lob':q['lob'],'status':q['status']})

    return output

#posts the new data
@app.route('/new_issue.html/post_userdata/',methods=['POST'])
def post_userdata():
    user = mongo.db.users
    issue = request.form.get('issue')
    count = int(request.form.get('count'))
    subject = request.form.get('subject')
    description = request.form.get('description')
    lob = request.form.get('lob')
    status = request.form.get('status')

    if (len(issue)>0):
        inserted_id = user.insert_one({'issue': issue, 'count': count,'subject':subject,'description':description,'lob':lob,'status':status})
        output = {'message': 'new user created'}
    else:
        output = {'error': 'required fields error'}

    # return render_template('index.html',header='All the users', sub_header='All the languages our users like',
    #                    users=get_all_users())
    return redirect("http://127.0.0.1:5000/index.html")

#posts the updated data after an edit
@app.route('/new_issue.html/post_userdata/<id>',methods=['POST'])
def post_updatedata(id):
    user = mongo.db.users
    issue = request.form.get('issue')
    count = int(request.form.get('count'))
    subject = request.form.get('subject')
    description = request.form.get('description')
    lob = request.form.get('lob')
    status = request.form.get('status')

    if (len(issue)>0):
        inserted_id = user.update_one({'_id':ObjectId(id)},{"$set": {'count': count,'subject':subject,'description':description,'lob':lob,'status':status}},upsert=False)
        output = {'message': 'Data updated'}
       
    else:
        output = {'error': 'required fields error'}

    return redirect("http://127.0.0.1:5000/index.html")



#It will show the updated data. fetches the id from the html form and then sends the id to html page in the url
@app.route('/new_issue/<id>', methods=['GET','POST'])
def new_data(id):
    user = mongo.db.users
      
    q = user.find_one({'_id': ObjectId(id)})
    # return post_data()
    return redirect("http://127.0.0.1:5000/new_issue.html/"+str(q['_id']))
    return  render_template("new_issue.html",user = q)

# # Delete a user
@app.route('/delete_issue/<user_id>', methods=['POST','DELETE'])
def delete_user(user_id):
    user = mongo.db.users
    q = user.find_one({'_id': ObjectId(user_id)})
    if q:
        user.remove(q["_id"])
        output = {'message' : 'user deleted'}
    else:
        output = {'error' : 'user not found'}

    return redirect("http://127.0.0.1:5000/index.html")

@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/users', methods=['DELETE'])
def delete_users():
    x = mongo.db.users.remove({ })
    # x = user.delete_many({})
    return jsonify(x,"documents deleted")

# Error Handler 404
@app.errorhandler(404)
def not_found(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'Not found'}), 404)

# Error Handler 405
@app.errorhandler(405)
def not_found(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'Method is not allowed'}), 405)

# Error Handler 500
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'Internal Error'}), 500)

# Exception
@app.errorhandler(Exception)
def unhandled_exception(error):
    app.logger.error('Unhandled Exception: %s', (error))
    return make_response(jsonify({'error': 'Unhandled Exception'}), 500)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)
