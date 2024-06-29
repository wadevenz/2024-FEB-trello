from flask_jwt_extended import get_jwt_identity

from init import db
from models.user import User

def authorise_as_admin():
    # get users id
    user_id = get_jwt_identity()
    # fetch user from db
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # check whether user is admin - returns T or F from is_admin
    return user.is_admin