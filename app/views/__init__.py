from flask import Blueprint

from app.views.user import UserView
from app.views.board import BoardView
from app.views.post import PostView

def register_api(app):
    UserView.register(app, route_base='/users', trailing_slash=False)
    BoardView.register(app, route_base='/boards', trailing_slash=False)
    PostView.register(app, route_base='/boards/<board_name>', trailing_slash=False)