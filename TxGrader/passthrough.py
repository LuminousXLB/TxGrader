from io import BytesIO

from flask import Blueprint, request, send_file

from .canvas import http

bp = Blueprint("passthrough", __name__, url_prefix="/")


def _passthrough():
    url = request.url.replace(request.root_url, "")
    resp = http.get(url)
    return (
        send_file(
            BytesIO(resp.content), mimetype=resp.headers["Content-Type"], max_age=600
        ),
        resp.status_code,
    )


@bp.route("/dist/javascripts/translations/<string:filename>", methods=("GET",))
def translations(filename):
    return _passthrough()


@bp.route("/users/<int:user_id>/files/<int:file_id>", methods=("GET",))
def files(user_id, file_id):
    return _passthrough()


@bp.route("/users/<int:user_id>/files/<int:file_id>/preview", methods=("GET",))
def preview_file(user_id, file_id):
    return _passthrough()


@bp.route("/media_objects_iframe/<string:media_id>", methods=("GET",))
def media_objects_iframe(media_id):
    return _passthrough()
