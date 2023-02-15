from flask import Blueprint, send_from_directory

bp = Blueprint("html", __name__, url_prefix="/")


@bp.route("/", methods=("GET",))
def index():
    return page_course()


@bp.route("/course", methods=("GET",))
def page_course():
    return send_from_directory("static", "course.html")


@bp.route("/question", methods=("GET",))
def page_question():
    return send_from_directory("static", "question.html")
