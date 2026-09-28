import { useEffect, useState } from "react";
import "./Deadlines.css";

const API_URL = "http://127.0.0.1:8000";

function Deadlines() {
  const [data, setData] = useState({
    overdue: [],
    upcoming: [],
    summary: {
      pending: 0,
      overdue: 0,
      assignments: 0,
      quizzes: 0,
      labs: 0,
    },
  });

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  // =========================================================
  // FETCH DEADLINES
  // =========================================================

  const fetchDeadlines = async (isRefresh = false) => {
    try {
      setError("");

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      const response = await fetch(`${API_URL}/dashboard`);

      if (!response.ok) {
        throw new Error("Failed to load deadlines");
      }

      const result = await response.json();

      setData({
        overdue: Array.isArray(result.overdue)
          ? result.overdue
          : [],

        upcoming: Array.isArray(result.upcoming)
          ? result.upcoming
          : [],

        summary: {
          pending: result.summary?.pending ?? 0,
          overdue: result.summary?.overdue ?? 0,
          assignments: result.summary?.assignments ?? 0,
          quizzes: result.summary?.quizzes ?? 0,
          labs: result.summary?.labs ?? 0,
        },
      });
    } catch (err) {
      console.error("Deadline error:", err);

      setError(
        "Unable to load deadlines. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    fetchDeadlines();
  }, []);

  // =========================================================
  // FORMAT DATE
  // =========================================================

  const formatDate = (dateString) => {
    if (!dateString) {
      return "No date";
    }

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return "No date";
    }

    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  // =========================================================
  // DAYS LEFT
  // =========================================================

  const getDaysLeft = (dateString) => {
    if (!dateString) {
      return "";
    }

    const today = new Date();
    const due = new Date(dateString);

    today.setHours(0, 0, 0, 0);
    due.setHours(0, 0, 0, 0);

    const difference = Math.round(
      (due - today) / (1000 * 60 * 60 * 24)
    );

    if (difference < 0) {
      const days = Math.abs(difference);

      return `${days} day${days !== 1 ? "s" : ""} overdue`;
    }

    if (difference === 0) {
      return "Due today";
    }

    if (difference === 1) {
      return "Due tomorrow";
    }

    return `${difference} days left`;
  };

  // =========================================================
  // TASK TYPE
  // =========================================================

  const getType = (taskType) => {
    return (taskType || "assignment").toLowerCase();
  };

  const getTypeIcon = (taskType) => {
    const type = getType(taskType);

    if (type === "quiz") {
      return "❓";
    }

    if (type === "lab") {
      return "🧪";
    }

    return "📝";
  };

  const getTypeLabel = (taskType) => {
    const type = getType(taskType);

    if (type === "quiz") {
      return "Quiz";
    }

    if (type === "lab") {
      return "Lab";
    }

    return "Assignment";
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="deadlines-page">

        <div className="deadline-loading">
          <div className="loading-spinner"></div>

          <h3>Loading deadlines...</h3>

          <p>
            Getting your university tasks
          </p>
        </div>

      </div>
    );
  }

  // =========================================================
  // MAIN UI
  // =========================================================

  return (
    <div className="deadlines-page">

      {/* =====================================================
          MAIN CONTENT HEADER
      ===================================================== */}

      <div className="deadline-page-title">

        <div>
          <h1>Deadlines</h1>

          <p>
            Keep track of everything you need to complete.
          </p>
        </div>

        <button
          type="button"
          className={`refresh-button ${
            refreshing ? "refreshing" : ""
          }`}
          onClick={() => fetchDeadlines(true)}
          disabled={refreshing}
        >
          <span
            className={`refresh-icon ${
              refreshing ? "spinning" : ""
            }`}
          >
            🔄
          </span>

          <span>
            {refreshing ? "Refreshing..." : "Refresh"}
          </span>
        </button>

      </div>


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (
        <div className="deadline-error">
          <span>⚠️</span>

          <div>
            <strong>Could not load deadlines</strong>
            <p>{error}</p>
          </div>

          <button
            type="button"
            onClick={() => fetchDeadlines(true)}
          >
            Try again
          </button>
        </div>
      )}


      {/* =====================================================
          SUMMARY CARDS
      ===================================================== */}

      <div className="deadline-stats">

        {/* TOTAL PENDING */}
        <div className="deadline-stat-card">

          <div className="stat-icon pending-icon">
            📋
          </div>

          <div className="stat-content">
            <span>Total Pending</span>

            <strong>
              {data.summary.pending}
            </strong>
          </div>

        </div>


        {/* OVERDUE */}
        <div className="deadline-stat-card">

          <div className="stat-icon overdue-icon">
            ⚠️
          </div>

          <div className="stat-content">
            <span>Overdue</span>

            <strong>
              {data.summary.overdue}
            </strong>
          </div>

        </div>


        {/* ASSIGNMENTS */}
        <div className="deadline-stat-card">

          <div className="stat-icon assignment-icon">
            📝
          </div>

          <div className="stat-content">
            <span>Assignments</span>

            <strong>
              {data.summary.assignments}
            </strong>
          </div>

        </div>


        {/* QUIZZES */}
        <div className="deadline-stat-card">

          <div className="stat-icon quiz-icon">
            ❓
          </div>

          <div className="stat-content">
            <span>Quizzes</span>

            <strong>
              {data.summary.quizzes}
            </strong>
          </div>

        </div>


        {/* LABS */}
        <div className="deadline-stat-card">

          <div className="stat-icon lab-icon">
            🧪
          </div>

          <div className="stat-content">
            <span>Labs</span>

            <strong>
              {data.summary.labs}
            </strong>
          </div>

        </div>

      </div>


      {/* =====================================================
          TWO COLUMN AREA
      ===================================================== */}

      <div className="deadline-columns">

        {/* ===================================================
            UPCOMING
        =================================================== */}

        <section className="deadline-section">

          <div className="section-title">

            <div className="section-heading">

              <h2>
                <span>📅</span>
                Upcoming Deadlines
              </h2>

              <p>
                Things you need to complete soon.
              </p>

            </div>

            <span className="section-count">
              {data.upcoming.length}
            </span>

          </div>


          {/* EMPTY */}
          {data.upcoming.length === 0 ? (

            <div className="empty-deadline">

              <div className="empty-icon">
                🎉
              </div>

              <h3>
                No upcoming deadlines
              </h3>

              <p>
                You're all caught up.
              </p>

            </div>

          ) : (

            <div className="deadline-list">

              {data.upcoming.map((task) => {

                const type = getType(task.task_type);

                return (
                  <div
                    className={`deadline-card ${type}-card`}
                    key={task.id}
                  >

                    {/* ICON */}
                    <div className={`deadline-icon ${type}`}>
                      {getTypeIcon(task.task_type)}
                    </div>


                    {/* INFO */}
                    <div className="deadline-info">

                      <h3>
                        {task.title || "Untitled Task"}
                      </h3>

                      <div className="deadline-course">
                        {task.course || "Unknown Course"}
                      </div>

                      {task.description && (
                        <p>
                          {task.description}
                        </p>
                      )}

                    </div>


                    {/* DATE */}
                    <div className="deadline-date">

                      <span>
                        Due
                      </span>

                      <strong>
                        {formatDate(task.due_date)}
                      </strong>

                      <small
                        className={
                          getDaysLeft(task.due_date) ===
                          "Due today"
                            ? "today-text"
                            : ""
                        }
                      >
                        {getDaysLeft(task.due_date)}
                      </small>

                    </div>


                    {/* TYPE */}
                    <div className={`deadline-type ${type}`}>
                      {getTypeLabel(task.task_type)}
                    </div>

                  </div>
                );
              })}

            </div>

          )}

        </section>


        {/* ===================================================
            OVERDUE
        =================================================== */}

        <section className="deadline-section overdue-section">

          <div className="section-title">

            <div className="section-heading">

              <h2>
                <span>⚠️</span>
                Overdue
              </h2>

              <p>
                These deadlines have already passed.
              </p>

            </div>

            <span className="section-count overdue-count">
              {data.overdue.length}
            </span>

          </div>


          {/* EMPTY */}
          {data.overdue.length === 0 ? (

            <div className="empty-deadline overdue-empty">

              <div className="empty-icon">
                🎉
              </div>

              <h3>
                No overdue tasks
              </h3>

              <p>
                Nice work — you're on track.
              </p>

            </div>

          ) : (

            <div className="deadline-list">

              {data.overdue.map((task) => {

                const type = getType(task.task_type);

                return (
                  <div
                    className={`deadline-card overdue-card ${type}-card`}
                    key={task.id}
                  >

                    {/* ICON */}
                    <div className={`deadline-icon ${type}`}>
                      {getTypeIcon(task.task_type)}
                    </div>


                    {/* INFO */}
                    <div className="deadline-info">

                      <h3>
                        {task.title || "Untitled Task"}
                      </h3>

                      <div className="deadline-course">
                        {task.course || "Unknown Course"}
                      </div>

                      {task.description && (
                        <p>
                          {task.description}
                        </p>
                      )}

                    </div>


                    {/* DATE */}
                    <div className="deadline-date">

                      <span>
                        Due
                      </span>

                      <strong>
                        {formatDate(task.due_date)}
                      </strong>

                      <small className="overdue-text">
                        {getDaysLeft(task.due_date)}
                      </small>

                    </div>


                    {/* TYPE */}
                    <div className={`deadline-type ${type}`}>
                      {getTypeLabel(task.task_type)}
                    </div>

                  </div>
                );
              })}

            </div>

          )}

        </section>

      </div>

    </div>
  );
}

export default Deadlines;