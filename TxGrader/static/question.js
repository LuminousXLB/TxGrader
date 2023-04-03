const { createApp } = Vue;

var app = createApp({
  data() {
    return {
      isLoading: true,
      meta: {
        course_id: null,
        assignment_id: null,
        quiz_id: null,
        question_id: null,
        question_group_id: null,
      },
      rawData: {},
      selected: 0,
      selPoints: -1,
      selComment: "",
      messages: [],
      messageTimers: [],
      question: {},
      sortKeys: ["user_id", "attempt"],
    };
  },
  computed: {
    tableData() {
      let res = [];

      for (const stu of Object.values(this.rawData)) {
        const name = stu.user.name;
        const user_id = stu.user.id;

        for (const history of stu.submission_history) {
          if (stu.attempt != history.attempt) {
            continue;
          }
          const quiz_submission_id = history.id;
          const attempt = history.attempt;

          if (!history.submission_data) {
            continue;
          }
          const submission_data = history.submission_data.find(
            (ans) => ans.question_id == this.meta.question_id
          );

          let obj = {
            name,
            user_id,
            attempt,
            quiz_submission_id,
            question_id: submission_data.question_id,
            score: submission_data.points,
            comment: submission_data.more_comments,
            text: submission_data.text,
          };
          if (stu.attempt === attempt) {
            obj.speedgrader = `https://canvas.nus.edu.sg/courses/${this.meta.course_id}/gradebook/speed_grader?assignment_id=${this.meta.assignment_id}&student_id=${user_id}`;
          }
          res.push(obj);
        }
      }

      res.sort((a, b) => {
        for (const key of this.sortKeys) {
          if (a[key] == b[key]) {
            continue;
          } else {
            return a[key] - b[key];
          }
        }
        return 0;
      });

      return res;
    },
  },
  watch: {
    tableData: function (val) {
      this.selPoints = val[this.selected].score;
      this.selComment = val[this.selected].comment;
    },
    selected: function (val) {
      const elem = document.getElementById(`table-row-${val}`);
      if (elem) {
        this.selPoints = this.tableData[val].score;
        this.selComment = this.tableData[val].comment;
        elem.scrollIntoViewIfNeeded(false);
      }
    },
    messages: {
      handler: function (val) {
        if (this.messageTimers.length < val.length) {
          this.messageTimers.push(
            setTimeout(() => {
              this.messages.shift();
              this.messageTimers.shift();
            }, 3000)
          );
        }

        if (this.messageTimers.length > val.length) {
          clearTimeout(this.messageTimers.shift());
        }

        if (val.length > 3) {
          this.messages.shift();
        }
      },
      deep: true,
    },
  },
  methods: {
    SubmitForm(e) {
      const quiz_submission_id =
        this.tableData[this.selected].quiz_submission_id;

      const attempt = this.tableData[this.selected].attempt;
      const question_id = this.tableData[this.selected].question_id;
      const score = this.selPoints;
      const comment = this.selComment;

      axios
        .post(
          "/api/update_scores_and_comments",
          { attempt, questions: [{ question_id, score, comment }] },
          {
            params: {
              course_id: this.meta.course_id,
              quiz_id: this.meta.quiz_id,
              quiz_submission_id,
            },
          }
        )
        .then((res) => {
          const user_id = res.data.quiz_submissions[0].user_id;

          axios
            .get("/api/get_single_submission", {
              params: {
                course_id: this.meta.course_id,
                assignment_id: this.meta.assignment_id,
                user_id,
                include: ["submission_history", "user"],
              },
            })
            .then((res) => {
              this.rawData[user_id] = res.data;
              this.messages.push(
                `Complete updating ${res.data.user.name}'s score or comment.`
              );
            });
        });
    },
    selectFirst() {
      this.selected = 0;
    },
    selectLast() {
      this.selected = this.tableData.length - 1;
    },
    selectPrev() {
      this.selected = Math.max(0, this.selected - 1);
    },
    selectNext() {
      this.selected = Math.min(this.tableData.length - 1, this.selected + 1);
    },
  },
  created() {
    param = new URLSearchParams(window.location.search);
    this.meta.course_id = param.get("course_id");
    this.meta.assignment_id = param.get("assignment_id");
    this.meta.quiz_id = param.get("quiz_id");
    if (param.has("question_group_id")) {
      this.meta.question_group_id = param.get("question_group_id");
    } else {
      this.meta.question_id = param.get("question_id");
    }

    axios
      .get("/api/get_single_quiz_question", {
        params: {
          course_id: this.meta.course_id,
          quiz_id: this.meta.quiz_id,
          id: this.meta.question_id,
        },
      })
      .then((res) => {
        this.question = res.data;
      });
  },
  mounted() {
    axios
      .get("/api/list_assignment_submissions/" + this.meta.question_id, {
        params: {
          course_id: this.meta.course_id,
          assignment_id: this.meta.assignment_id,
          include: ["user", "submission_history"],
        },
      })
      .then((res) => {
        this.messages.push("Complete loading submission history.");
        for (let stu of res.data) {
          this.rawData[stu.user.id] = stu;
        }
        this.isLoading = false;
      });
  },
}).mount("#app");

document.addEventListener("keyup", (e) => {
  if (e.key === "Enter") {
    if (e.ctrlKey || (e.target.tagName === "TEXTAREA" && e.shiftKey)) {
      app.SubmitForm();
    }

    if (e.shiftKey) {
      app.selectNext();
    }
  }

  if (e.key === "Escape") {
    app.messages = [];
  }

  if (e.target.tagName === "TEXTAREA") {
    return;
  }

  switch (e.key) {
    case "h":
      app.selectFirst();
      break;
    case "j":
      app.selectNext();
      break;
    case "k":
      app.selectPrev();
      break;
    case "l":
      app.selectLast();
      break;
  }
});
