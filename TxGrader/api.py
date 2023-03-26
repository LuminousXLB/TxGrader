from flask import Blueprint, jsonify, request

from .canvas import http

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/get_user_profile", methods=("GET",))
def get_user_profile():
    url = "/api/v1/users/{user_id}/profile".format(**request.args)
    return http.get(url).text


@bp.route("/list_courses", methods=("GET",))
def list_your_courses():
    url = "/api/v1/courses"
    iter = http.paginated(url, params={"enrollment_state": "active"})
    return list(iter)


@bp.route("/list_assignments", methods=("GET",))
def list_assignments_assignments():
    url = "/api/v1/courses/{course_id}/assignments".format(**request.args)
    iter = http.paginated(url)
    return list(iter)


@bp.route("/list_quiz_questions", methods=("GET",))
def list_questions_in_quiz_or_submission():
    url = "/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions".format(
        **request.args
    )
    resp = http.get(url, params={"per_page": 1})
    quiz_submission_id = resp.json()["quiz_submissions"][0]["id"]

    url = f"/api/v1/quiz_submissions/{quiz_submission_id}/questions"
    resp = http.get(url)
    return jsonify(resp.json()["quiz_submission_questions"]), resp.status_code


@bp.route("/get_single_quiz_question", methods=("GET",))
def get_single_quiz_question():
    url = "/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions/{id}".format(
        **request.args
    )
    resp = http.get(url)
    return resp.text, resp.status_code


@bp.route("/list_quiz_submission_questions", methods=("GET",))
def get_all_quiz_submission_questions():
    url = "/api/v1/quiz_submissions/{quiz_submission_id}/questions".format(
        **request.args
    )
    resp = http.get(url)
    return resp.text, resp.status_code


@bp.route("/list_assignment_submissions", methods=("GET",))
def list_assignment_submissions_courses():
    url = "/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions".format(
        **request.args
    )

    iter = http.paginated(
        url,
        params={
            "include[]": request.args.getlist("include[]"),
            "per_page": 50,
        },
    )

    return list(iter)


@bp.route("/list_assignment_submissions/<int:question_id>", methods=("GET",))
def list_assignment_submissions_courses_question(question_id):
    submissions = list_assignment_submissions_courses()
    return [
        {
            "user": submission["user"],
            "submission_history": [
                {
                    "id": history["id"],
                    "attempt": history["attempt"],
                    "submission_data": [
                        qn
                        for qn in history["submission_data"]
                        if qn["question_id"] == question_id
                    ],
                }
                for history in submission["submission_history"]
                if "submission_data" in history
            ],
        }
        for submission in submissions
    ]


@bp.route("/get_single_submission", methods=("GET",))
def get_single_submission_courses():
    url = "/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}".format(
        **request.args
    )
    resp = http.get(url, params={"include[]": request.args.getlist("include[]")})
    return resp.text, resp.status_code


@bp.route("/update_scores_and_comments", methods=("POST",))
def update_student_question_scores_and_comments():
    url = "/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{quiz_submission_id}".format(
        **request.args
    )

    attempt = request.json["attempt"]
    questions = request.json["questions"]

    resp = http.put(
        url,
        json={
            "quiz_submissions": [
                {
                    "attempt": attempt,
                    "questions": {
                        str(qn["question_id"]): {
                            "score": qn["score"],
                            "comment": qn.get("comment"),
                        }
                        for qn in questions
                    },
                }
            ]
        },
    )
    if not "quiz_submissions" in resp.json():
        return resp.text, 400
    else:
        return resp.text
