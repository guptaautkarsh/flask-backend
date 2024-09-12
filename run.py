from crypt import methods
import os
import secrets
from datetime import datetime

from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from flask_cors import CORS

from MLmodel.project_convex.model import predict

# from ml import predict
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id_of_user, username, email, password):
        self.id = id_of_user
        self.username = username
        self.email = email
        self.password = password


user_id = 0
database = {
    # 1: User(1,"Utkarsh Gupta", "ut@gmail.com", "84wvkm")
}

pdf_id = 0
pdf_db = {
    # 1: {'id':1, 'pdf_name': 'xyz.pdf', 'date_posted': '02-09-2024', 'user_id':1}
}

@login_manager.user_loader
def load_user(use_id):
    return database.get(int(use_id))


@app.route('/question', methods=['POST'])
def question():
    if request.is_json:
        data = request.get_json()

        user_query = data.get('question', None)

        if user_query is None:
            return jsonify({'error': 'No question provided'}),400
        else:
            user_query = str(user_query)
            ans = predict(user_query)
            ans = str(ans)

        return jsonify({"answer":ans})

    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/registration', methods=['POST'])
def registration():
    if request.is_json:
        data = request.get_json()

        global user_id
        username = data.get('username')
        for i in range(1,user_id+1):
            if database[i].username == username:
                return jsonify({'error' : 'username already exist'})

        email = data.get('email')
        for i in range(1, user_id+1):
            if database[i].email == email:
                return jsonify({'error': 'Email already exist'})

        user_id =+ 1
        hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
        user = User(user_id, username, email, hashed_password)
        database[user_id] = user
        return jsonify({'message' : 'Successfully Registered'})

    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json()

        email = data.get('email')
        for i in range(1,user_id+1):
            if database[i].email == email:
                password = data.get('password')
                if bcrypt.check_password_hash(database[i].password, password):
                    login_user(database[i])
                    return jsonify({"message": "Login successful"})
                else:
                    return jsonify("error : Invalid Password")

            if i==user_id:
                return jsonify("error : Email is not registered")

    else:
        return jsonify({"error": "Request must be JSON"}), 400

def save_pdf(pdf):
    random_hex = secrets.token_hex(8) #just to make file name unique
    f_name, f_ext = os.path.splitext(pdf.filename) #.filename to extract filename from the uploaded pic
    pdf_fn = random_hex + f_ext
    # now we need to get full path where this pdf will be stored
    save_pdf_path = os.path.join(app.root_path, 'pdf_files', pdf_fn)
    pdf.save(save_pdf_path) #save pdf to that path
    return pdf_fn #returning pdf name so we can use it to change in database

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if not current_user.is_authenticated:
        return jsonify({'error' : 'user is not logged in!'})

    if 'pdf_file' not in request.files:
        return jsonify({'error': "pdf file not found"})

    pdf_array = request.files.getlist('pdf_file')

    for pdf in pdf_array:
        pdf_name = save_pdf(pdf)
        global pdf_id
        pdf_id += 1
        pdf_db[pdf_id] = { }
        pdf_db[pdf_id]['id'] = pdf_id
        pdf_db[pdf_id]['pdf_name'] = pdf_name
        pdf_db[pdf_id]['date_posted'] = datetime.now().strftime('%d-%m-%Y')
        pdf_db[pdf_id]['user_id'] = current_user.id

    return jsonify({'message': 'All PDF uploaded successfully'})


def save_pdf_to_documents(pdf):
    pdf_fn = pdf.filename
    save_pdf_path = os.path.join(app.root_path, 'MLmodel/project_convex/documents', pdf_fn)
    pdf.save(save_pdf_path) #save pdf to that path

def clear_documents():
    # delete all the existing files
    folder_path = os.path.join(app.root_path, 'MLmodel/project_convex/documents')
    if not os.listdir(folder_path):
        return

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)


@app.route('/selected', methods=['POST'])
def select_pdf():
    if not current_user.is_authenticated:
        return jsonify({'error' : 'user is not logged in!'})

    if 'selected_pdf_files' not in request.files:
        return jsonify({'error': "pdf file not found"})

    selected_pdf_array = request.files.getlist('selected_pdf_files')

    clear_documents()
    for pdf in selected_pdf_array:
        save_pdf_to_documents(pdf)

    return jsonify({'message': 'All PDF selected successfully'})


@app.route('/download/<int:file_id>')
def get_pdf(file_id):
    if file_id in pdf_db:
        name = pdf_db[file_id]['pdf_name']
        path = os.path.join(app.root_path, 'pdf_files', name)

        return send_file(path_or_file=path,as_attachment=False,
                         download_name= str(name),mimetype='application/pdf')

    return jsonify({"error" : 'file not found'})


@app.route('/history')
def history():
    if not current_user.is_authenticated:
        return jsonify({'error' : 'user is not logged in!'})

    json_obj = [ ]

    for pdf_no in pdf_db.values():
        json_obj.append(pdf_no)

    return jsonify({'history' : json_obj})



@app.route('/logout')
@login_required
def logout():
    logout_user_name = current_user.username
    logout_user()
    return jsonify({'message': '{} is logged out'.format(logout_user_name)})


@app.route('/account')
@login_required
def account():
    return jsonify({"message" : "{} is currently logged in".format(current_user.username)})

if __name__ == '__main__':
    app.run(debug=True)
