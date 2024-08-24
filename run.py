from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user, logout_user
from ml import predict

app = Flask(__name__)
app.config['SECRET_KEY'] = '417dea5bf1f74a58129b5692f2488fbf'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

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

@login_manager.user_loader
def load_user(use_id):
    return database.get(int(use_id))

@app.route('/', methods=['POST'])
def home():
    if request.is_json:
        data = request.get_json()

        input = data.get('input', None)
        input = str(input)

        if input is None:
            return jsonify({'error': 'No input data provided'}),400
        else:
            output = predict(input)

        return jsonify({"result": output})

    else:
        return jsonify({"error": "Request must be JSON"}),400


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