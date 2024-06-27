from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.comment import Comment, comment_schema, comments_schema
from models.card import Card

comments_bp = Blueprint("comments", __name__, url_prefix="/<int:card_id>/comments")

# Don't need GET for comments as they are fetched when we GET cards
@comments_bp.route("/", methods=["POST"])
@jwt_required()
def create_comment(card_id):
    # get comment object from body of request
    body_data=request.get_json()
    # fetch the card with that particular id - card id
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card exists
    if card:
        # create intance of the Comment
        comment = Comment(
            message=body_data.get("message"),
            date=date.today(),
            card=card,
            user_id=get_jwt_identity()
        )
        # add and commit to the session
        db.session.add(comment)
        db.session.commit()
        # return the created commit
        return comment_schema.dump(comment), 201
    # else
    else:
        # return an error message
        return {"error": f"Card with id {card_id} not found"}, 404

@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(card_id, comment_id):
    # fetch the comment from the db with that id - comment id
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    # if the comment exists
    if comment:
        # delete the comment
        db.session.delete(comment)
        db.session.commit()
        return {"message": f"Comment '{comment.message}' deleted successfully"}
    # else
    else:
        # return an error
        return {"error": f"Comment with id {comment_id} not found"}, 404
    
@comments_bp.route("/<int:comment_id>", methods=["PUT", "PATCH"])
@jwt_required()
def edit_comment(card_id, comment_id):
    # get the values from the body of request
    body_data = request.get_json()
    # find the comment in the db with id - comment_id
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    # if comment exists
    if comment:
        # update
        comment.message=body_data.get("message") or comment.message
        # commit
        db.session.commit()
        # return message response
        return comment_schema.dump(comment)
    # else
    else:
        # return error message
        return {"error": f"Comment with {comment_id} not found"}, 404
