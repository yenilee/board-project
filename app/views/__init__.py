from flask import jsonify
import sys

from app.views.user import UserView
from app.views.board import BoardView
from app.views.post import PostView
from app.views.comment import CommentView


def handle_bad_request(e):
    return jsonify(message='잘못된 요청입니다.'), 404

def page_not_found(e):
    return jsonify(message='페이지가 존재하지 않습니다.'), 404

def handle_unknown_exception(e):
    if 'JSONDecodeError' in str(sys.exc_info()):
        return jsonify(message='Json decoder 에러 - '+str(e)), 400

    if 'mongoengine' in str(sys.exc_info()):
        return jsonify(message='데이터베이스 에러 - '+str(e)), 500

    return jsonify(message='확인되지 않은 에러 - '+str(e)), 500

def json_decoder_error(e):
    if 'JSONDecodeError' in str(sys.exc_info()):
        return jsonify(message='Json decoder 오류 - '+str(e)), 400


def register_error_handlers(blueprint):
    blueprint.register_error_handler(400, handle_bad_request)
    blueprint.register_error_handler(404, page_not_found)
    blueprint.register_error_handler(Exception, handle_unknown_exception)


def register_api(app):
    UserView.register(app, route_base='/users', trailing_slash=False)
    BoardView.register(app, route_base='/boards', trailing_slash=False)
    PostView.register(app, route_base='/boards/<board_id>/posts', trailing_slash=False)
    CommentView.register(app, route_base='/boards/<board_id>/posts/<post_id>/comments', trailing_slash=False)

    register_error_handlers(app)
