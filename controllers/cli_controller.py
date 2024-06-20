from datetime import date

from flask import Blueprint

from init import db, bcrypt
from models.user import User
from models.card import Card

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def create_tables():
    db.create_all()
    print ("Tables created")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print ("Tables dropped")

@db_commands.cli.command("seed")
def seed_tables():
    # create a list of user instances
    users = [
        User(
            email="admin@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            is_admin=True
        ),
        User(
            name="User 1",
            email="user1@email.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8")
        )
    ]

    db.session.add_all(users)

    cards = [
        Card(
            title="Card 1",
            description="Card 1 description",
            date=date.today(),
            status="To Do",
            priority="High",
            user=users[0]
        ),
        Card(
            title="Card 2",
            description="Card 2 description",
            date=date.today(),
            status="Ongoing",
            priority="Low",
            user=users[0]
        ),
        Card(
            title="Card 3",
            description="Card 3 description",
            date=date.today(),
            status="Done",
            priority="Medium",
            user=users[1]
        )
    ]

    db.session.add_all(cards)

    db.session.commit()

    print ("Tables seeded")