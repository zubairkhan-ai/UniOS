import { useEffect, useState } from "react";
import "./Quizzes.css";

const API_BASE = "http://127.0.0.1:8000";

function Quizzes() {

  // =========================================================
  // STATE
  // =========================================================

  const [quizzes, setQuizzes] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const [actionLoading, setActionLoading] = useState(false);

  // Add Quiz form
  const [showAddForm, setShowAddForm] = useState(false);

  const [formData, setFormData] = useState({
    course: "",
    title: "",
    due_date: "",
    description: "",
  });


  // =========================================================
  // LOAD QUIZZES
  // =========================================================

  const loadQuizzes = async () => {

    setLoading(true);
    setError("");

    try {

      const response = await fetch(
        `${API_BASE}/quizzes`
      );

      if (!response.ok) {

        throw new Error(
          `Server returned ${response.status}`
        );

      }

      const data = await response.json();

      console.log(
        "Quiz API response:",
        data
      );


      // -----------------------------------------------------
      // NEW QUIZ API
      // -----------------------------------------------------

      if (Array.isArray(data.quizzes)) {

        setQuizzes(data.quizzes);

      }

      else {

        setQuizzes([]);

      }

    }

    catch (err) {

      console.error(
        "Quiz loading error:",
        err
      );

      setError(
        "Could not load quizzes. Make sure FastAPI is running."
      );

      setQuizzes([]);

    }

    finally {

      setLoading(false);

    }

  };


  // =========================================================
  // LOAD WHEN PAGE OPENS
  // =========================================================

  useEffect(() => {

    loadQuizzes();

  }, []);


  // =========================================================
  // TODAY
  // =========================================================

  const today = new Date()
    .toISOString()
    .split("T")[0];


  // =========================================================
  // FILTER QUIZZES
  // =========================================================

  const pendingQuizzes = quizzes.filter(
    (quiz) =>
      quiz.status === "pending"
  );


  const completedQuizzes = quizzes.filter(
    (quiz) =>
      quiz.status === "completed"
  );


  const overdueQuizzes = pendingQuizzes.filter(
    (quiz) =>
      quiz.due_date &&
      quiz.due_date < today
  );


  const upcomingQuizzes = pendingQuizzes.filter(
    (quiz) =>
      !quiz.due_date ||
      quiz.due_date >= today
  );


  // =========================================================
  // SORT
  // =========================================================

  const sortByDate = (a, b) => {

    if (!a.due_date) return 1;

    if (!b.due_date) return -1;

    return a.due_date.localeCompare(
      b.due_date
    );

  };


  const sortedUpcoming = [
    ...upcomingQuizzes
  ].sort(sortByDate);


  const sortedOverdue = [
    ...overdueQuizzes
  ].sort(sortByDate);


  const sortedCompleted = [
    ...completedQuizzes
  ].sort(sortByDate);


  // =========================================================
  // FORM INPUT
  // =========================================================

  const handleInputChange = (event) => {

    const {
      name,
      value
    } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value
    }));

  };


  // =========================================================
  // ADD QUIZ
  // =========================================================

  const handleAddQuiz = async (event) => {

    event.preventDefault();

    setError("");

    // Basic validation

    if (!formData.course.trim()) {

      setError("Please enter a course.");

      return;

    }


    if (!formData.title.trim()) {

      setError("Please enter a quiz title.");

      return;

    }


    if (!formData.due_date) {

      setError("Please select a due date.");

      return;

    }


    setActionLoading(true);

    try {

      const response = await fetch(
        `${API_BASE}/quizzes`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            course:
              formData.course.trim(),

            title:
              formData.title.trim(),

            due_date:
              formData.due_date,

            description:
              formData.description.trim()
          })
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.error ||
          `Server returned ${response.status}`
        );

      }


      console.log(
        "Quiz added:",
        data
      );


      // Close form

      setShowAddForm(false);


      // Clear form

      setFormData({
        course: "",
        title: "",
        due_date: "",
        description: "",
      });


      // Reload quizzes

      await loadQuizzes();

    }

    catch (err) {

      console.error(
        "Add quiz error:",
        err
      );

      setError(
        err.message ||
        "Could not add quiz."
      );

    }

    finally {

      setActionLoading(false);

    }

  };


  // =========================================================
  // COMPLETE QUIZ
  // =========================================================

  const handleCompleteQuiz = async (
    quizId
  ) => {

    const confirmed = window.confirm(
      "Mark this quiz as completed?"
    );


    if (!confirmed) {

      return;

    }


    setError("");
    setActionLoading(true);


    try {

      const response = await fetch(
        `${API_BASE}/quizzes/${quizId}/complete`,
        {
          method: "PATCH"
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.error ||
          `Server returned ${response.status}`
        );

      }


      console.log(
        "Quiz completed:",
        data
      );


      await loadQuizzes();

    }

    catch (err) {

      console.error(
        "Complete quiz error:",
        err
      );

      setError(
        err.message ||
        "Could not complete quiz."
      );

    }

    finally {

      setActionLoading(false);

    }

  };


  // =========================================================
  // DELETE QUIZ
  // =========================================================

  const handleDeleteQuiz = async (
    quizId
  ) => {

    const confirmed = window.confirm(
      "Are you sure you want to delete this quiz?"
    );


    if (!confirmed) {

      return;

    }


    setError("");
    setActionLoading(true);


    try {

      const response = await fetch(
        `${API_BASE}/quizzes/${quizId}`,
        {
          method: "DELETE"
        }
      );


      const data = await response.json();


      if (!response.ok) {

        throw new Error(
          data.error ||
          `Server returned ${response.status}`
        );

      }


      console.log(
        "Quiz deleted:",
        data
      );


      await loadQuizzes();

    }

    catch (err) {

      console.error(
        "Delete quiz error:",
        err
      );

      setError(
        err.message ||
        "Could not delete quiz."
      );

    }

    finally {

      setActionLoading(false);

    }

  };


  // =========================================================
  // QUIZ ITEM
  // =========================================================

  const renderQuizItem = (
    quiz,
    icon = "❓",
    extraClass = "",
    showActions = false
  ) => {

    return (

      <div
        className={`quiz-item ${extraClass}`}
        key={quiz.id}
      >

        {/* LEFT */}

        <div className="quiz-item-left">

          <div className="quiz-icon">

            {icon}

          </div>


          <div className="quiz-info">

            <strong>

              {quiz.title || "Quiz"}

            </strong>


            <span>

              {quiz.course || "Unknown Course"}

            </span>


            {quiz.description && (

              <small>

                {quiz.description}

              </small>

            )}

          </div>

        </div>


        {/* RIGHT */}

        <div className="quiz-item-right">

          <div className="quiz-date">

            {quiz.due_date ||
              "No due date"}

          </div>


          {showActions && (

            <div className="quiz-actions">

              <button
                className="quiz-complete-button"
                onClick={() =>
                  handleCompleteQuiz(
                    quiz.id
                  )
                }
                disabled={actionLoading}
              >

                ✓ Complete

              </button>


              <button
                className="quiz-delete-button"
                onClick={() =>
                  handleDeleteQuiz(
                    quiz.id
                  )
                }
                disabled={actionLoading}
              >

                🗑 Delete

              </button>

            </div>

          )}

        </div>

      </div>

    );

  };


  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {

    return (

      <section className="quizzes-page">

        <div className="quizzes-header">

          <div>

            <h1>
              My Quizzes
            </h1>

            <p>
              Track your upcoming,
              overdue, and completed quizzes.
            </p>

          </div>

        </div>


        <div className="quiz-loading">

          Loading your quizzes...

        </div>

      </section>

    );

  }


  // =========================================================
  // PAGE
  // =========================================================

  return (

    <section className="quizzes-page">


      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="quizzes-header">

        <div>

          <h1>
            My Quizzes
          </h1>

          <p>
            Track your upcoming,
            overdue, and completed quizzes.
          </p>

        </div>


        <div className="quiz-header-actions">

          <button
            className="refresh-button"
            onClick={loadQuizzes}
            disabled={loading || actionLoading}
          >

            🔄 Refresh

          </button>


          <button
            className="add-quiz-button"
            onClick={() =>
              setShowAddForm(
                !showAddForm
              )
            }
          >

            {showAddForm
              ? "✕ Cancel"
              : "＋ Add Quiz"}

          </button>

        </div>

      </div>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <div className="quiz-error">

          ⚠️ {error}

        </div>

      )}


      {/* =====================================================
          ADD QUIZ FORM
      ===================================================== */}

      {showAddForm && (

        <div className="add-quiz-card">

          <div className="add-quiz-header">

            <div>

              <h2>
                ➕ Add New Quiz
              </h2>

              <p>
                Add a quiz to your academic schedule.
              </p>

            </div>

          </div>


          <form
            className="add-quiz-form"
            onSubmit={handleAddQuiz}
          >

            {/* COURSE */}

            <div className="form-group">

              <label>
                Course
              </label>

              <input
                type="text"
                name="course"
                placeholder="e.g. CN"
                value={formData.course}
                onChange={handleInputChange}
              />

            </div>


            {/* TITLE */}

            <div className="form-group">

              <label>
                Quiz Title
              </label>

              <input
                type="text"
                name="title"
                placeholder="e.g. Mid Term Quiz"
                value={formData.title}
                onChange={handleInputChange}
              />

            </div>


            {/* DATE */}

            <div className="form-group">

              <label>
                Due Date
              </label>

              <input
                type="date"
                name="due_date"
                value={formData.due_date}
                onChange={handleInputChange}
              />

            </div>


            {/* DESCRIPTION */}

            <div className="form-group form-group-full">

              <label>
                Description
              </label>

              <textarea
                name="description"
                placeholder="Optional description..."
                value={formData.description}
                onChange={handleInputChange}
                rows="3"
              />

            </div>


            {/* SUBMIT */}

            <div className="form-actions">

              <button
                type="button"
                className="cancel-button"
                onClick={() =>
                  setShowAddForm(false)
                }
              >

                Cancel

              </button>


              <button
                type="submit"
                className="save-quiz-button"
                disabled={actionLoading}
              >

                {actionLoading
                  ? "Saving..."
                  : "＋ Add Quiz"}

              </button>

            </div>

          </form>

        </div>

      )}


      {/* =====================================================
          STAT CARDS
      ===================================================== */}

      <div className="quiz-stats">


        {/* TOTAL */}

        <div className="quiz-stat-card">

          <div className="quiz-stat-icon">
            ❓
          </div>

          <div>

            <span>
              Total Quizzes
            </span>

            <strong>
              {quizzes.length}
            </strong>

          </div>

        </div>


        {/* PENDING */}

        <div className="quiz-stat-card">

          <div className="quiz-stat-icon">
            ⏳
          </div>

          <div>

            <span>
              Pending
            </span>

            <strong>
              {pendingQuizzes.length}
            </strong>

          </div>

        </div>


        {/* OVERDUE */}

        <div className="quiz-stat-card">

          <div className="quiz-stat-icon">
            ⚠️
          </div>

          <div>

            <span>
              Overdue
            </span>

            <strong>
              {overdueQuizzes.length}
            </strong>

          </div>

        </div>


        {/* COMPLETED */}

        <div className="quiz-stat-card">

          <div className="quiz-stat-icon">
            ✅
          </div>

          <div>

            <span>
              Completed
            </span>

            <strong>
              {completedQuizzes.length}
            </strong>

          </div>

        </div>

      </div>


      {/* =====================================================
          UPCOMING + OVERDUE
      ===================================================== */}

      <div className="quiz-columns">


        {/* ===================================================
            UPCOMING
        =================================================== */}

        <div className="quiz-card">

          <div className="quiz-card-header">

            <div>

              <h2>
                📅 Upcoming Quizzes
              </h2>

              <p>
                Quizzes you still need to take.
              </p>

            </div>


            <span className="quiz-count">

              {sortedUpcoming.length}

            </span>

          </div>


          {sortedUpcoming.length === 0 ? (

            <div className="quiz-empty">

              <div className="empty-icon">
                🎉
              </div>

              <strong>
                No upcoming quizzes
              </strong>

              <span>
                You're all caught up.
              </span>

            </div>

          ) : (

            <div className="quiz-list">

              {sortedUpcoming.map(
                (quiz) =>

                  renderQuizItem(
                    quiz,
                    "❓",
                    "",
                    true
                  )
              )}

            </div>

          )}

        </div>


        {/* ===================================================
            OVERDUE
        =================================================== */}

        <div className="quiz-card">

          <div className="quiz-card-header">

            <div>

              <h2>
                ⚠️ Overdue Quizzes
              </h2>

              <p>
                These quizzes have passed their due date.
              </p>

            </div>


            <span className="quiz-count overdue-count">

              {sortedOverdue.length}

            </span>

          </div>


          {sortedOverdue.length === 0 ? (

            <div className="quiz-empty">

              <div className="empty-icon">
                🎉
              </div>

              <strong>
                No overdue quizzes
              </strong>

              <span>
                Nice work — you're on track.
              </span>

            </div>

          ) : (

            <div className="quiz-list">

              {sortedOverdue.map(
                (quiz) =>

                  renderQuizItem(
                    quiz,
                    "⚠️",
                    "quiz-overdue",
                    true
                  )
              )}

            </div>

          )}

        </div>

      </div>


      {/* =====================================================
          COMPLETED QUIZZES
      ===================================================== */}

      <div className="quiz-card completed-card">

        <div className="quiz-card-header">

          <div>

            <h2>
              ✅ Completed Quizzes
            </h2>

            <p>
              Your finished quizzes.
            </p>

          </div>


          <span className="quiz-count completed-count">

            {sortedCompleted.length}

          </span>

        </div>


        {sortedCompleted.length === 0 ? (

          <div className="quiz-empty">

            <div className="empty-icon">
              📚
            </div>

            <strong>
              No completed quizzes yet
            </strong>

            <span>
              Your completed quizzes will appear here.
            </span>

          </div>

        ) : (

          <div className="quiz-list">

            {sortedCompleted.map(
              (quiz) =>

                renderQuizItem(
                  quiz,
                  "✅",
                  "quiz-completed",
                  false
                )
            )}

          </div>

        )}

      </div>

    </section>

  );

}


export default Quizzes;