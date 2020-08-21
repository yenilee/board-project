from flask import Blueprint

from app.views.user import UserView

def register_api(app):
    UserView.register(app, route_base='/users', trailing_slash=False)
