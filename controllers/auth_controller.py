from datetime import timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from init import bcrypt, db
from models.user import User, user_schema, UserSchema
from utils import auth_as_admin_decorator

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register_user():
    try:
        # get data from the body of the request
        body_data = UserSchema().load(request.get_json())
        # create an instance of the User model
        user = User(
            name=body_data.get("name"),
            email=body_data.get("email"),
        )
        # hash the password
        password=body_data.get("password")

        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")

        # add and commit to the database
        db.session.add(user)
        db.session.commit()
        # respond back
        return user_schema.dump(user), 201

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The column {err.orig.diag.column_name} is required"}, 409  
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address already in use"}, 409
        
@auth_bp.route("/login", methods=["POST"])
def login_user():
    # get the data from the body of the request
    body_data = request.get_json()
    # find the user in DB with same email
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)
    # if user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # create JWT
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # respond back
        return {"email": user.email, "is_admin": user.is_admin, "token": token}
    
    # else
    else:
        # respond back with error
        return {"error": "Invalid email or password"}, 401
    
# /auth/users/
@auth_bp.route("/users", methods=["PUT", "PATCH"])
@jwt_required()
def update_user():
    # get fields from body of request
    body_data = UserSchema().load(request.get_json(), partial=True)
    password = body_data.get("password")
    # fetch the user from the database
    stmt = db.select(User).filter_by(id=get_jwt_identity())
    user = db.session.scalar(stmt)
    # if user exists
    if user:
        # update the fields
        user.name = body_data.get("name") or user.name
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        # commit to the db
        db.session.commit()
        # return a response
        return user_schema.dump(user)
    # else
    else:
        # return an error
        return {"error": f"{user} does not exist"}
    
# /auth/users/user_id
@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_decorator
def delete_user(user_id):
    # find the user with the id from the db
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # if user exists
    if user:
        # delete the user
        db.session.delete(user)
        db.session.commit()
        # return a message
        return {"message": f"User with id {user_id} deleted"}
    # else
    else:
        # return error saying user does not exist
        return {"error": f"User with id {user_id} not found"}
