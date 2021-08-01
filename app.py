import os
from flask import Flask, jsonify, request, abort, make_response, render_template, redirect
from flask_pymongo import PyMongo, ObjectId # flask.ext.pymongo deprecated
from flask_cors import CORS, cross_origin
from flask_login import LoginManager , login_required , UserMixin , login_user, current_user

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

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# class User(UserMixin):

#     def __init__(self, q):
#         self.id = q['_id']
#         self.name = q['username']
#         self.password = q['password']
        
#     def __repr__(self):
#         return "%d/%s/%s" % (self.id, self.name, self.password)

# user = mongo.db.account
# user.insert_one({'username':'aakash23','password':'iloveyou123'})

# Allowed files
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','json'])
users_info={
            'name':'Aakash',
            'language':'C'}

# @app.route('/fixtures', methods=['GET'])
# def add():
#     user = mongo.db.users
#     user.insert_one(users_info)
#     user.insert_one({'name': 'Anthony', 'language' : 'ruby'})
#     user.insert_one({'name': 'Kelly', 'language' : 'C'})
#     user.insert_one({'name': 'John', 'language' : 'Java'})
#     user.insert_one({'name': 'Cedric', 'language' : 'Javascript'})
#     return jsonify({'message':'users added'})

# @app.route('/', methods = ["GET","POST"])

# @app.route('/login', methods = ["GET","POST"])
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')
    # return render_template(str(APP_ROOT)+"/templates/login.html")
    # if(request.method=="POST"):
    #     user_name = request.form.get("username")
    #     password = request.form.get("password")
    #     user = mongo.db.account
    #     q = user.find_one({'username':user_name})
    #     if(q):
    #         if(password == q["password"]):
    #             id = q['_id']
    #             user = User(q)
    #             login_user(user)
    #             return redirect(request.args.get("next"))

    #         else:
    #             return abort(401)

    # else:
    # return render_template('login.html')


#It's the home page

# @login_required
@app.route('/new_issue.html/')
def home():
    # return render_template('new_issue.html',header='All the users', sub_header='All the languages our users like',
    #                    users=get_all_users())
    return render_template('new_issue.html')

#gets called when this page is called through mavbar
# @app.route('/new_issue.html')
# # @login_required
# def post_data():
#     # return render_template('new_issue.html',header='All the users', sub_header='All the languages our users like',
#     #                    users=get_all_users())
#     return render_template('new_issue.html')

#this is called when a user tries to make any changes to existing data
@app.route('/new_issue.html/<id>')
# @login_required
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
# @login_required
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
@app.route('/post_userdata/',methods=['POST'])
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
    return redirect("http://127.0.0.1:5000/")
    
# @app.route("/post_userdata/<id>", methods=['POST'])
# def post_formdata(id):
#     id = id
#     return post_updatedata(id)

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

    # return render_template('index.html',header='All the users', sub_header='All the languages our users like',
    #                    users=get_all_users())
    return redirect("http://127.0.0.1:5000/index.html")



#It will show the updated data. fetches the id from the html form and then sends the id to html page in the url
@app.route('/new_issue/<id>', methods=['GET','POST'])
def new_data(id):
    user = mongo.db.users
    # if(id=="index.html"):
    #     return redirect("http://127.0.0.1:5000/index.html")
    # elif(id=="new_issue.html"):
    #     return redirect("http://127.0.0.1:5000/")
        
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


# Route to Uploade Page
# @app.route("/upload-page")
# def main():
#     return render_template('upload-file.html')

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload File
# @app.route('/upload', methods=['POST'])
# def upload():
#     result = {'errors': [] }
#     # Set the target Folder
#     target = os.path.join(APP_ROOT, 'images/')
#     # Get sure the folder exists
#     if not os.path.isdir(target):
#         os.mkdir(target)
#     # Loop file to get the images names
#     for file in request.files.getlist("file"):
#         filename = file.filename
#         destination = "/".join([target, filename])
#         if file and allowed_file(file.filename):
#             file.save(destination)
#         else:
#             if not file.filename:
#                 file.filename = "empty"
#             result["errors"].append({file.filename:'not allowed'})

#     return jsonify(result)



# List user by name
# @app.route('/users/<user_id>', methods=['GET'])
# def get_one_user(user_id):
#     user = mongo.db.users
#     q = user.find_one({'_id': ObjectId(user_id)})
#     if q:
#         output = {'user': {'_id': str(q['_id']), 'name': q['name'], 'language': q['language']}}
#     else:
#         output = {'error' : 'user not found'}

#     return jsonify(output)

# Post user
# @app.route('/users', methods=['POST'])
# def post_user():
#     user = mongo.db.users
#     # name = request.form['name']
#     # language = request.form['language']
#     name = str(input("Enter user name"))
#     language = str(input("Enter the language of choice"))
#     if (len(name) > 1 and len(language) > 0):
#         q = user.find_one({'name':name})
#         if q:
#             user_found = {'_id': str(q['_id']),'name': q['name'], 'language': q['language']}
#             output = {'error': 'user exists !', 'user': user_found}
#         else:
#             inserted_id = user.insert_one({'name': name, 'language': language})
#             output = {'message': 'new user created'}
#     else:
#         output = {'error': 'required fields error'}

#     return jsonify(output)

# # Update a user
# @app.route('/users/<user_id>', methods=['PUT'])
# def update_user(user_id):
#     user = mongo.db.users
#     q = user.find_one({'_id': ObjectId(user_id)})
#     if q:
#         if request.form['name']:
#             q['name'] = request.form['name']
#         if request.form['language']:
#             q['language'] = request.form['language']

#         user.save(q);
#         output = {'message' : 'user updated'}
#     else:
#         output = {'error' : 'user not found'}

#     return jsonify(output)

# # Delete a user
# @app.route('/users/<user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = mongo.db.users
#     q = user.find_one({'_id': ObjectId(user_id)})
#     if q:
#         user.remove(q["_id"])
#         output = {'message' : 'user deleted'}
#     else:
#         output = {'error' : 'user not found'}

#     return jsonify(output)

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
    app.run(debug=True)
