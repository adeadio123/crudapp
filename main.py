import os
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from a .env file into the environment
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Retrieve database configuration from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define the User model representing the 'users' table in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.BigInteger, nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "phone_number": self.phone_number,
            "location": self.location
        }

# Create tables, when the app starts
with app.app_context():
    db.create_all()

# Route to create a new user
@app.route('/create/users', methods=['POST'])
def create_user():
    data = request.get_json()   # Parse JSON data from the request
    required_fields = ['first_name', 'last_name', 'age', 'phone_number', 'location']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required fields.")
    try:
        # Create a new User instance with the provided data
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=int(data['age']),
            phone_number=int(data['phone_number']),
            location=data['location']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Route to retrieve all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

# Route to retrieve a specific user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({"error": "User not found"}), 404

# Route to update a specific user by ID
@app.route('/update/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if user:
        try:
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            user.phone_number = int(data.get("phone_number", user.phone_number))
            user.location = data.get("location", user.location)
            db.session.commit()
            return jsonify(user.to_dict())
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "User not found"}), 404

# Route to delete a specific user by ID
@app.route('/delete/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"})
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
