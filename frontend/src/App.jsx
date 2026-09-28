import { useEffect, useState } from "react";
import uniosLogo from "./assets/unios-logo-icon.png";
import "./App.css";
import "./CourseContext.css";
import "./Assignments.css";
import Quizzes from "./Quizzes";
import Labs from "./Labs";
import Deadlines from "./Deadlines";
import Courses from "./Courses";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {

  // =========================================================
  // AI CHAT STATE
  // =========================================================

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text:
        "Hey! 👋 I'm your AI University Assistant. Ask me about your lectures, assignments, quizzes, labs, or deadlines.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

// =========================================================
// AI COURSE CONTEXT
// =========================================================

  const [selectedCourse, setSelectedCourse] = useState("");
  const [availableCourses, setAvailableCourses] = useState([]);
  const [coursesLoading, setCoursesLoading] = useState(false);
  const [courseContextError, setCourseContextError] = useState("");
  // =========================================================
  // PAGE STATE
  // =========================================================

  const [activePage, setActivePage] = useState("assistant");


  // =========================================================
  // DASHBOARD STATE
  // =========================================================

  const [dashboardData, setDashboardData] = useState(null);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [dashboardError, setDashboardError] = useState("");


  // =========================================================
  // ASSIGNMENT STATE
  // =========================================================

  const [assignments, setAssignments] = useState([]);
  const [assignmentLoading, setAssignmentLoading] = useState(false);
  const [assignmentError, setAssignmentError] = useState("");

  const [showAddAssignment, setShowAddAssignment] = useState(false);

  const [newAssignment, setNewAssignment] = useState({
    course: "",
    title: "",
    due_date: "",
    description: "",
    task_type: "assignment",
  });


  // =========================================================
  // LOAD COURSE CONTEXT FROM YOUR ACTUAL UNIVERSITY DATA
  // =========================================================
  //
  // The /courses endpoint discovers the courses available in
  // data/lectures. This keeps the AI selector synchronized
  // with the same courses shown on the Courses page.
  //
  const loadCourseContext = async () => {
    try {
      setCoursesLoading(true);
      setCourseContextError("");

      const response = await fetch(`${API_BASE}/courses`);

      if (!response.ok) {
        throw new Error(`Courses server returned ${response.status}`);
      }

      const result = await response.json();

      // Support both:
      //   [ { code, name }, ... ]
      // and:
      //   { courses: [ { code, name }, ... ] }
      const rawCourses = Array.isArray(result)
        ? result
        : Array.isArray(result.courses)
        ? result.courses
        : [];

      const normalizedCourses = rawCourses
        .map((course) => {
          const code = String(
            course.code || course.course || ""
          ).trim();

          const name = String(
            course.name ||
            course.title ||
            course.course_name ||
            code
          ).trim();

          return {
            code,
            name,
          };
        })
        .filter((course) => course.code);

      // Remove duplicate course codes.
      const uniqueCourses = [];
      const seen = new Set();

      normalizedCourses.forEach((course) => {
        const key = course.code.toLowerCase();

        if (!seen.has(key)) {
          seen.add(key);
          uniqueCourses.push(course);
        }
      });

      setAvailableCourses(uniqueCourses);

      // If the previously selected course no longer exists,
      // return to All Courses.
      if (
        selectedCourse &&
        !uniqueCourses.some(
          (course) =>
            course.code.toLowerCase() ===
            selectedCourse.toLowerCase()
        )
      ) {
        setSelectedCourse("");
      }

    } catch (error) {
      console.error("Course context error:", error);

      setAvailableCourses([]);
      setSelectedCourse("");
      setCourseContextError(
        "Could not load your courses from the university data."
      );
    } finally {
      setCoursesLoading(false);
    }
  };

  // Load courses once when the AI Assistant starts.
  useEffect(() => {
    loadCourseContext();
  }, []);

  // =========================================================
  // SEND CHAT MESSAGE
  // =========================================================

  const sendMessage = async (message = input) => {

    const text = message.trim();

    if (!text || loading) {
      return;
    }

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: text,
      },
    ]);

    setInput("");
    setLoading(true);

    try {

      const response = await fetch(
        `${API_BASE}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
          message: text,
          course: selectedCourse || null,
        }),
        }
      );


      if (!response.ok) {
        throw new Error(
          `Server returned ${response.status}`
        );
      }


      const data = await response.json();


      // Add AI response
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",

          text:
            data.response ||
            "Sorry, I couldn't generate a response.",
        },
      ]);

    } catch (error) {

      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",

          text:
            "⚠️ I couldn't connect to the AI server. Make sure FastAPI is running.",
        },
      ]);

    } finally {

      setLoading(false);

    }
  };


  // =========================================================
  // CHAT FORM
  // =========================================================

  const handleSubmit = (e) => {

    e.preventDefault();

    sendMessage();

  };


  // =========================================================
  // LOAD DASHBOARD
  // =========================================================

  const loadDashboard = async () => {

    setDashboardLoading(true);
    setDashboardError("");

    try {

      const response = await fetch(
        `${API_BASE}/dashboard`
      );


      if (!response.ok) {

        throw new Error(
          `Dashboard server returned ${response.status}`
        );

      }


      const data = await response.json();

      setDashboardData(data);

    } catch (error) {

      console.error(
        "Dashboard error:",
        error
      );

      setDashboardError(
        "Could not load dashboard data. Make sure FastAPI is running."
      );

    } finally {

      setDashboardLoading(false);

    }
  };


  // =========================================================
  // OPEN DASHBOARD
  // =========================================================

  const openDashboard = () => {

    setActivePage("dashboard");

    loadDashboard();

  };


  // =========================================================
  // OPEN ASSISTANT
  // =========================================================

  const openAssistant = () => {

    setActivePage("assistant");

  };


  // =========================================================
  // LOAD ASSIGNMENTS
  // =========================================================

  const loadAssignments = async () => {

    setAssignmentLoading(true);
    setAssignmentError("");

    try {

      const response = await fetch(
        `${API_BASE}/assignments`
      );


      if (!response.ok) {

        throw new Error(
          `Assignments server returned ${response.status}`
        );

      }


      const data = await response.json();


      const taskList = Array.isArray(data)
        ? data
        : Array.isArray(data.assignments)
        ? data.assignments
        : [];


      setAssignments(taskList);

    } catch (error) {

      console.error(
        "Assignments error:",
        error
      );

      setAssignmentError(
        "Could not load assignments. Make sure FastAPI is running."
      );

    } finally {

      setAssignmentLoading(false);

    }
  };


  // =========================================================
  // OPEN ASSIGNMENTS
  // =========================================================

  const openAssignments = () => {

    setActivePage("assignments");

    loadAssignments();

  };


  // =========================================================
  // OPEN QUIZZES
  // =========================================================

  const openQuizzes = () => {

    setActivePage("quizzes");

  };


  // =========================================================
  // OPEN LABS
  // =========================================================

  const openLabs = () => {

    setActivePage("labs");

  };


  // =========================================================
  // OPEN DEADLINES
  // =========================================================

  const openDeadlines = () => {

    setActivePage("deadlines");

  };


  // =========================================================
  // OPEN COURSES
  // =========================================================

  const openCourses = () => {

    setActivePage("courses");

  };


  // =========================================================
  // COMING SOON PAGES
  // =========================================================

  const handleComingSoon = (page) => {

    console.log(`${page} page coming soon`);

  };


  // =========================================================
  // ASSIGNMENT FORM CHANGE
  // =========================================================

  const handleAssignmentChange = (e) => {

    const {
      name,
      value,
    } = e.target;


    setNewAssignment((prev) => ({
      ...prev,
      [name]: value,
    }));

  };


  // =========================================================
  // ADD ASSIGNMENT / QUIZ / LAB
  // =========================================================

  const addAssignment = async (e) => {

    e.preventDefault();


    if (
      !newAssignment.course.trim() ||
      !newAssignment.title.trim() ||
      !newAssignment.due_date
    ) {

      alert(
        "Please enter course, title and due date."
      );

      return;

    }


    try {

      const response = await fetch(
        `${API_BASE}/assignments`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(
            newAssignment
          ),
        }
      );


      if (!response.ok) {

        const errorData =
          await response
            .json()
            .catch(() => ({}));


        throw new Error(
          errorData.detail ||
          `Server returned ${response.status}`
        );

      }


      // Reset form
      setNewAssignment({
        course: "",
        title: "",
        due_date: "",
        description: "",
        task_type: "assignment",
      });


      setShowAddAssignment(false);


      // Refresh data
      await loadAssignments();
      await loadDashboard();


    } catch (error) {

      console.error(
        "Add assignment error:",
        error
      );

      alert(
        `Could not add task.\n\n${error.message}`
      );

    }

  };


  // =========================================================
  // COMPLETE ASSIGNMENT
  // =========================================================

  const completeAssignment = async (
    assignmentId
  ) => {

    try {

      const response = await fetch(
        `${API_BASE}/assignments/${assignmentId}/complete`,
        {
          method: "PATCH",
        }
      );


      if (!response.ok) {

        throw new Error(
          `Server returned ${response.status}`
        );

      }


      await loadAssignments();
      await loadDashboard();


    } catch (error) {

      console.error(
        "Complete assignment error:",
        error
      );

      alert(
        "Could not mark the assignment as completed."
      );

    }

  };


  // =========================================================
  // DELETE ASSIGNMENT
  // =========================================================

  const deleteAssignment = async (
    assignmentId
  ) => {

    if (
      !window.confirm(
        "Are you sure you want to delete this assignment?"
      )
    ) {

      return;

    }


    try {

      const response = await fetch(
        `${API_BASE}/assignments/${assignmentId}`,
        {
          method: "DELETE",
        }
      );


      if (!response.ok) {

        throw new Error(
          `Server returned ${response.status}`
        );

      }


      await loadAssignments();
      await loadDashboard();


    } catch (error) {

      console.error(
        "Delete assignment error:",
        error
      );

      alert(
        "Could not delete the assignment."
      );

    }

  };


  // =========================================================
  // ASSIGNMENT FILTERS
  // =========================================================

  const assignmentOnly =
    assignments.filter(
      (task) =>
        !task.task_type ||
        task.task_type.toLowerCase() ===
          "assignment"
    );


  const pendingAssignments =
    assignmentOnly.filter(
      (task) =>
        task.status === "pending"
    );


  const completedAssignments =
    assignmentOnly.filter(
      (task) =>
        task.status === "completed"
    );


  const today =
    new Date()
      .toISOString()
      .split("T")[0];


  const overdueAssignments =
    pendingAssignments.filter(
      (task) =>
        task.due_date &&
        task.due_date < today
    );


  // =========================================================
  // FORMAT TASK TYPE
  // =========================================================

  const formatTaskType = (type) => {

    if (!type) {
      return "Assignment";
    }

    return (
      type.charAt(0).toUpperCase() +
      type.slice(1)
    );

  };


  // =========================================================
  // RENDER
  // =========================================================

  return (

    <div className="app">


      {/* =====================================================
          SIDEBAR
      ===================================================== */}

      <aside className="sidebar">


        {/* LOGO */}

        <div className="logo-section">

          <div className="logo-icon">
            <img src={uniosLogo} alt="UniOS logo" />
          </div>

          <div className="logo-text">

            <h2>
              UniOS
            </h2>

            <span>
              AI University OS
            </span>

          </div>

        </div>


        {/* NAVIGATION */}

        <nav className="navigation">


          {/* AI ASSISTANT */}

          <button
            className={`nav-item ${
              activePage === "assistant"
                ? "active"
                : ""
            }`}
            onClick={openAssistant}
          >

            <span>
              💬
            </span>

            AI Assistant

          </button>


          {/* DASHBOARD */}

          <button
            className={`nav-item ${
              activePage === "dashboard"
                ? "active"
                : ""
            }`}
            onClick={openDashboard}
          >

            <span>
              🏠
            </span>

            Dashboard

          </button>


          {/* COURSES */}

          <button
            className={`nav-item ${
              activePage === "courses"
                ? "active"
                : ""
            }`}
            onClick={openCourses}
          >

            <span>
              📚
            </span>

            Courses

          </button>


          {/* ASSIGNMENTS */}

          <button
            className={`nav-item ${
              activePage === "assignments"
                ? "active"
                : ""
            }`}
            onClick={openAssignments}
          >

            <span>
              📝
            </span>

            Assignments

          </button>


          {/* LABS */}

          <button
            className={`nav-item ${
              activePage === "labs"
                ? "active"
                : ""
            }`}
            onClick={openLabs}
          >

            <span>
              🧪
            </span>

            Labs

          </button>


          {/* QUIZZES */}

          <button
            className={`nav-item ${
              activePage === "quizzes"
                ? "active"
                : ""
            }`}
            onClick={openQuizzes}
          >

            <span>
              ❓
            </span>

            Quizzes

          </button>


          {/* DEADLINES */}

          <button
            className={`nav-item ${
              activePage === "deadlines"
                ? "active"
                : ""
            }`}
            onClick={openDeadlines}
          >

            <span>
              📅
            </span>

            Deadlines

          </button>


        </nav>


        {/* SYSTEM STATUS */}

        <div className="sidebar-bottom">

          <div className="status-dot"></div>

          <div>

            <strong>
              AI System Online
            </strong>

            <span>
              FastAPI + LangGraph
            </span>

          </div>

        </div>


      </aside>


      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <main className="main">


        {/* ===================================================
            HEADER
        =================================================== */}

        <header className="topbar">

          <div>


            {/* ASSISTANT */}

            {activePage === "assistant" && (

              <>

                <h1>
                  AI Assistant
                </h1>

                <p>
                  Your intelligent university companion
                </p>

              </>

            )}


            {/* DASHBOARD */}

            {activePage === "dashboard" && (

              <>

                <h1>
                  Dashboard
                </h1>

                <p>
                  Your academic overview
                </p>

              </>

            )}


            {/* COURSES */}

            {activePage === "courses" && (

              <>

                <h1>
                  Courses
                </h1>

                <p>
                  Manage your courses and keep track of your academic work
                </p>

              </>

            )}


            {/* ASSIGNMENTS */}

            {activePage === "assignments" && (

              <>

                <h1>
                  Assignments
                </h1>

                <p>
                  Manage your academic assignments
                </p>

              </>

            )}


            {/* QUIZZES */}

            {activePage === "quizzes" && (

              <>

                <h1>
                  Quizzes
                </h1>

                <p>
                  Track your upcoming and completed quizzes
                </p>

              </>

            )}


            {/* LABS */}

            {activePage === "labs" && (

              <>

                <h1>
                  Labs
                </h1>

                <p>
                  Track your upcoming and completed labs
                </p>

              </>

            )}


            {/* DEADLINES */}

            {activePage === "deadlines" && (

              <>

                <h1>
                  Deadlines
                </h1>

                <p>
                  Track all your upcoming, overdue, and completed deadlines
                </p>

              </>

            )}


          </div>


          {/* ONLINE STATUS */}

          <div className="online-badge">

            <span></span>

            Online

          </div>

        </header>


        {/* ===================================================
            AI ASSISTANT PAGE
        =================================================== */}

        {activePage === "assistant" && (

          <>

            <section className="chat-area">


              <div className="messages">


                {/* MESSAGES */}

                {messages.map(
                  (message, index) => (

                    <div
                      key={index}
                      className={`message-row ${message.role}`}
                    >

                      <div className="avatar">

                        {
                          message.role ===
                          "assistant"
                            ? "🤖"
                            : "👤"
                        }

                      </div>


                      <div className="message-content">

                        <div className="message-name">

                          {
                            message.role ===
                            "assistant"
                              ? "UniOS AI"
                              : "You"
                          }

                        </div>


                        <div className="message-bubble">

                          {message.text}

                        </div>

                      </div>

                    </div>

                  )
                )}


                {/* TYPING */}

                {loading && (

                  <div className="message-row assistant">

                    <div className="avatar">
                      🤖
                    </div>

                    <div className="message-content">

                      <div className="message-name">
                        UniOS AI
                      </div>

                      <div className="message-bubble typing">

                        <span></span>
                        <span></span>
                        <span></span>

                      </div>

                    </div>

                  </div>

                )}

              </div>


              {/* QUICK ACTIONS */}

              {messages.length === 1 && (

                <div className="quick-actions">

                  <p>
                    Try asking
                  </p>


                  <div className="quick-grid">


                    <button
                      onClick={() =>
                        sendMessage(
                          "What is an operating system?"
                        )
                      }
                    >
                      📚 Explain a lecture topic
                    </button>


                    <button
                      onClick={() =>
                        sendMessage(
                          "What is my next deadline?"
                        )
                      }
                    >
                      📅 Check my next deadline
                    </button>


                    <button
                      onClick={() =>
                        sendMessage(
                          "Show my quizzes"
                        )
                      }
                    >
                      ❓ Show my quizzes
                    </button>


                    <button
                      onClick={() =>
                        sendMessage(
                          "I have 2 hours today"
                        )
                      }
                    >
                      🧠 Make a study plan
                    </button>


                  </div>

                </div>

              )}

            </section>


            {/* CHAT INPUT */}

            <div className="input-container">


              <form
                onSubmit={handleSubmit}
                className="chat-form"
              >

                <div className="assistant-course-context">
                  <div className="assistant-course-label">
                    <span className="assistant-course-icon">📚</span>
                    <span>Course Context</span>
                  </div>

                  <select
                    id="assistant-course"
                    value={selectedCourse}
                    onChange={(e) => setSelectedCourse(e.target.value)}
                    disabled={loading}
                    aria-label="Select course context"
                  >
                    <option value="">
                      {coursesLoading
                        ? "⏳ Loading your courses..."
                        : "🌐 All Courses"}
                    </option>

                    {availableCourses.map((course) => (
                      <option key={course.code} value={course.code}>
                        {course.code} — {course.name}
                      </option>
                    ))}
                  </select>
                </div>

                <input
                  type="text"
                  placeholder={
                    selectedCourse
                      ? `Ask anything about ${selectedCourse}...`
                      : "Ask anything about your university..."
                  }
                  value={input}
                  onChange={(e) =>
                    setInput(e.target.value)
                  }
                  disabled={loading}
                />


                <button
                  type="submit"
                  disabled={
                    loading ||
                    !input.trim()
                  }
                >

                  {
                    loading
                      ? "..."
                      : "➤"
                  }

                </button>

              </form>


              <p className="input-hint">
                {courseContextError
                  ? courseContextError
                  : selectedCourse
                  ? `UniOS is answering from ${selectedCourse} lecture material.`
                  : coursesLoading
                  ? "Loading your courses from the university data..."
                  : "UniOS can answer from your lectures and manage your academic tasks."}
              </p>


            </div>

          </>

        )}


        {/* ===================================================
            DASHBOARD PAGE
        =================================================== */}

        {activePage === "dashboard" && (

          <section className="dashboard-page">


            {/* DASHBOARD HEADER */}

            <div className="dashboard-header">

              <div>

                <h1>
                  Welcome back 👋
                </h1>

                <p>
                  Here's your academic overview.
                </p>

              </div>


              <button
                className="refresh-button"
                onClick={loadDashboard}
                disabled={dashboardLoading}
              >

                🔄{" "}

                {
                  dashboardLoading
                    ? "Loading..."
                    : "Refresh"
                }

              </button>

            </div>


            {/* ERROR */}

            {dashboardError && (

              <div className="dashboard-error">

                ⚠️ {dashboardError}

              </div>

            )}


            {/* LOADING */}

            {dashboardLoading && (

              <div className="dashboard-loading">

                Loading your university data...

              </div>

            )}


            {/* DASHBOARD DATA */}

            {dashboardData &&
              !dashboardLoading && (

                <>


                  {/* STAT CARDS */}

                  <div className="stats-grid">


                    {/* PENDING */}

                    <div className="stat-card">

                      <div className="stat-icon">
                        📋
                      </div>

                      <div>

                        <span>
                          Pending Tasks
                        </span>

                        <strong>
                          {
                            dashboardData
                              .summary
                              .pending
                          }
                        </strong>

                      </div>

                    </div>


                    {/* OVERDUE */}

                    <div className="stat-card overdue-card">

                      <div className="stat-icon">
                        ⚠️
                      </div>

                      <div>

                        <span>
                          Overdue
                        </span>

                        <strong>
                          {
                            dashboardData
                              .summary
                              .overdue
                          }
                        </strong>

                      </div>

                    </div>


                    {/* ASSIGNMENTS */}

                    <div className="stat-card">

                      <div className="stat-icon">
                        📝
                      </div>

                      <div>

                        <span>
                          Assignments
                        </span>

                        <strong>
                          {
                            dashboardData
                              .summary
                              .assignments
                          }
                        </strong>

                      </div>

                    </div>


                    {/* QUIZZES */}

                    <div className="stat-card">

                      <div className="stat-icon">
                        ❓
                      </div>

                      <div>

                        <span>
                          Quizzes
                        </span>

                        <strong>
                          {
                            dashboardData
                              .summary
                              .quizzes
                          }
                        </strong>

                      </div>

                    </div>


                  </div>


                  {/* TASK COLUMNS */}

                  <div className="dashboard-columns">


                    {/* OVERDUE */}

                    <div className="dashboard-card">

                      <div className="card-header">

                        <h2>
                          ⚠️ Overdue Tasks
                        </h2>

                        <span className="count-badge">

                          {
                            dashboardData
                              .overdue
                              .length
                          }

                        </span>

                      </div>


                      {
                        dashboardData
                          .overdue
                          .length === 0
                          ? (

                            <p className="empty-state">

                              🎉 No overdue tasks!

                            </p>

                          )
                          : (

                            <div className="task-list">

                              {
                                dashboardData
                                  .overdue
                                  .map(
                                    (task) => (

                                      <div
                                        className="task-item overdue"
                                        key={task.id}
                                      >

                                        <div className="task-info">

                                          <strong>
                                            {task.title}
                                          </strong>

                                          <span>
                                            {task.course}
                                            {" • "}
                                            {task.task_type}
                                          </span>

                                        </div>


                                        <small>
                                          Due {task.due_date}
                                        </small>

                                      </div>

                                    )
                                  )
                              }

                            </div>

                          )
                      }

                    </div>


                    {/* UPCOMING */}

                    <div className="dashboard-card">

                      <div className="card-header">

                        <h2>
                          📅 Upcoming
                        </h2>

                        <span className="count-badge">

                          {
                            dashboardData
                              .upcoming
                              .length
                          }

                        </span>

                      </div>


                      {
                        dashboardData
                          .upcoming
                          .length === 0
                          ? (

                            <p className="empty-state">

                              🎉 Nothing upcoming!

                            </p>

                          )
                          : (

                            <div className="task-list">

                              {
                                dashboardData
                                  .upcoming
                                  .map(
                                    (task) => (

                                      <div
                                        className="task-item"
                                        key={task.id}
                                      >

                                        <div className="task-info">

                                          <strong>
                                            {task.title}
                                          </strong>

                                          <span>
                                            {task.course}
                                            {" • "}
                                            {task.task_type}
                                          </span>

                                        </div>


                                        <small>
                                          {task.due_date}
                                        </small>

                                      </div>

                                    )
                                  )
                              }

                            </div>

                          )
                      }

                    </div>


                  </div>


                  {/* QUIZZES + LABS */}

                  <div className="dashboard-columns">


                    {/* QUIZZES */}

                    <div className="dashboard-card">

                      <div className="card-header">

                        <h2>
                          ❓ Upcoming Quizzes
                        </h2>

                        <span className="count-badge">

                          {
                            dashboardData
                              .quizzes
                              .length
                          }

                        </span>

                      </div>


                      {
                        dashboardData
                          .quizzes
                          .length === 0
                          ? (

                            <p className="empty-state">

                              No quizzes found.

                            </p>

                          )
                          : (

                            <div className="task-list">

                              {
                                dashboardData
                                  .quizzes
                                  .map(
                                    (quiz) => (

                                      <div
                                        className="task-item"
                                        key={quiz.id}
                                      >

                                        <div className="task-info">

                                          <strong>
                                            {quiz.title}
                                          </strong>

                                          <span>
                                            {quiz.course}
                                          </span>

                                        </div>

                                        <small>
                                          {quiz.due_date}
                                        </small>

                                      </div>

                                    )
                                  )
                              }

                            </div>

                          )
                      }

                    </div>


                    {/* LABS */}

                    <div className="dashboard-card">

                      <div className="card-header">

                        <h2>
                          🧪 Labs
                        </h2>

                        <span className="count-badge">

                          {
                            dashboardData
                              .labs
                              .length
                          }

                        </span>

                      </div>


                      {
                        dashboardData
                          .labs
                          .length === 0
                          ? (

                            <p className="empty-state">

                              No pending labs.

                            </p>

                          )
                          : (

                            <div className="task-list">

                              {
                                dashboardData
                                  .labs
                                  .map(
                                    (lab) => (

                                      <div
                                        className="task-item"
                                        key={lab.id}
                                      >

                                        <div className="task-info">

                                          <strong>
                                            {lab.title}
                                          </strong>

                                          <span>
                                            {lab.course}
                                          </span>

                                        </div>

                                        <small>
                                          {lab.due_date}
                                        </small>

                                      </div>

                                    )
                                  )
                              }

                            </div>

                          )
                      }

                    </div>


                  </div>


                </>

              )
            }


          </section>

        )}


        {/* ===================================================
            COURSES PAGE
        =================================================== */}

        {activePage === "courses" && (

          <Courses />

        )}


        {/* ===================================================
            ASSIGNMENTS PAGE
        =================================================== */}

        {activePage === "assignments" && (

          <section className="assignments-page">


            {/* HEADER */}

            <div className="assignments-header">

              <div>

                <h1>
                  My Assignments
                </h1>

                <p>
                  View and manage your pending and completed assignments.
                </p>

              </div>


              <div className="assignment-header-actions">

                <button
                  className="refresh-button"
                  onClick={loadAssignments}
                  disabled={assignmentLoading}
                >

                  🔄{" "}

                  {
                    assignmentLoading
                      ? "Loading..."
                      : "Refresh"
                  }

                </button>


                <button
                  className="add-assignment-button"
                  onClick={() =>
                    setShowAddAssignment(
                      (prev) => !prev
                    )
                  }
                >

                  ➕ Add Assignment

                </button>

              </div>

            </div>


            {/* STATS */}

            <div className="assignment-stats">

              <div className="assignment-stat-card">

                <span>
                  📚 Total
                </span>

                <strong>
                  {assignmentOnly.length}
                </strong>

              </div>


              <div className="assignment-stat-card">

                <span>
                  ⏳ Pending
                </span>

                <strong>
                  {pendingAssignments.length}
                </strong>

              </div>


              <div className="assignment-stat-card">

                <span>
                  ⚠️ Overdue
                </span>

                <strong>
                  {overdueAssignments.length}
                </strong>

              </div>


              <div className="assignment-stat-card">

                <span>
                  ✅ Completed
                </span>

                <strong>
                  {completedAssignments.length}
                </strong>

              </div>

            </div>


            {/* ADD FORM */}

            {showAddAssignment && (

              <form
                className="assignment-form-card"
                onSubmit={addAssignment}
              >

                <div className="assignment-form-grid">


                  <div className="form-group">

                    <label>
                      Course *
                    </label>

                    <input
                      name="course"
                      value={
                        newAssignment.course
                      }
                      onChange={
                        handleAssignmentChange
                      }
                      placeholder="e.g. CN"
                      required
                    />

                  </div>


                  <div className="form-group">

                    <label>
                      Title *
                    </label>

                    <input
                      name="title"
                      value={
                        newAssignment.title
                      }
                      onChange={
                        handleAssignmentChange
                      }
                      placeholder="e.g. Lab 4"
                      required
                    />

                  </div>


                  <div className="form-group">

                    <label>
                      Due Date *
                    </label>

                    <input
                      type="date"
                      name="due_date"
                      value={
                        newAssignment.due_date
                      }
                      onChange={
                        handleAssignmentChange
                      }
                      required
                    />

                  </div>


                  <div className="form-group">

                    <label>
                      Type
                    </label>

                    <select
                      name="task_type"
                      value={
                        newAssignment.task_type
                      }
                      onChange={
                        handleAssignmentChange
                      }
                    >

                      <option value="assignment">
                        Assignment
                      </option>

                      <option value="quiz">
                        Quiz
                      </option>

                      <option value="lab">
                        Lab
                      </option>

                    </select>

                  </div>


                </div>


                <div className="form-group">

                  <label>
                    Description
                  </label>

                  <textarea
                    name="description"
                    value={
                      newAssignment.description
                    }
                    onChange={
                      handleAssignmentChange
                    }
                    placeholder="Optional description..."
                    rows="3"
                  />

                </div>


                <div className="assignment-form-actions">

                  <button
                    type="button"
                    className="cancel-button"
                    onClick={() =>
                      setShowAddAssignment(false)
                    }
                  >
                    Cancel
                  </button>


                  <button
                    type="submit"
                    className="save-assignment-button"
                  >
                    💾 Save Task
                  </button>

                </div>

              </form>

            )}


            {/* ERROR */}

            {assignmentError && (

              <div className="dashboard-error">

                ⚠️ {assignmentError}

              </div>

            )}


            {/* LOADING */}

            {assignmentLoading && (

              <div className="dashboard-loading">

                Loading your assignments...

              </div>

            )}


            {/* LIST */}

            {!assignmentLoading && (

              <div className="assignment-list-card">


                <div className="card-header">

                  <h2>
                    📝 Assignment List
                  </h2>

                  <span className="count-badge">
                    {assignmentOnly.length}
                  </span>

                </div>


                {
                  assignmentOnly.length === 0
                    ? (

                      <div className="empty-state assignment-empty">

                        <div>
                          📚
                        </div>

                        <strong>
                          No assignments found.
                        </strong>

                        <span>
                          Add your first assignment using the button above.
                        </span>

                      </div>

                    )
                    : (

                      <div className="assignment-list">

                        {
                          assignmentOnly.map(
                            (assignment) => {

                              const isOverdue =
                                assignment.status ===
                                  "pending" &&
                                assignment.due_date <
                                  today;


                              const isCompleted =
                                assignment.status ===
                                "completed";


                              return (

                                <div
                                  key={
                                    assignment.id
                                  }
                                  className={`
                                    assignment-item
                                    ${
                                      isOverdue
                                        ? "assignment-overdue"
                                        : ""
                                    }
                                    ${
                                      isCompleted
                                        ? "assignment-completed"
                                        : ""
                                    }
                                  `}
                                >


                                  <div className="assignment-main">


                                    <div className="assignment-icon">

                                      {
                                        isCompleted
                                          ? "✅"
                                          : isOverdue
                                          ? "⚠️"
                                          : "📝"
                                      }

                                    </div>


                                    <div className="assignment-details">


                                      <div className="assignment-title-row">

                                        <h3>
                                          {
                                            assignment.title
                                          }
                                        </h3>


                                        <span
                                          className={`
                                            assignment-status
                                            ${
                                              isCompleted
                                                ? "completed"
                                                : isOverdue
                                                ? "overdue"
                                                : "pending"
                                            }
                                          `}
                                        >

                                          {
                                            isCompleted
                                              ? "Completed"
                                              : isOverdue
                                              ? "Overdue"
                                              : "Pending"
                                          }

                                        </span>

                                      </div>


                                      <div className="assignment-meta">

                                        <span>
                                          📚{" "}
                                          {
                                            assignment.course
                                          }
                                        </span>

                                        <span>
                                          📅{" "}
                                          {
                                            assignment.due_date
                                          }
                                        </span>

                                        <span>
                                          🏷️{" "}
                                          {
                                            formatTaskType(
                                              assignment.task_type
                                            )
                                          }
                                        </span>

                                      </div>


                                      {
                                        assignment.description && (

                                          <p>
                                            {
                                              assignment.description
                                            }
                                          </p>

                                        )
                                      }


                                    </div>


                                  </div>


                                  <div className="assignment-actions">


                                    {
                                      !isCompleted && (

                                        <button
                                          className="complete-button"
                                          onClick={() =>
                                            completeAssignment(
                                              assignment.id
                                            )
                                          }
                                        >

                                          ✅ Complete

                                        </button>

                                      )
                                    }


                                    <button
                                      className="delete-button"
                                      onClick={() =>
                                        deleteAssignment(
                                          assignment.id
                                        )
                                      }
                                    >

                                      🗑️ Delete

                                    </button>


                                  </div>


                                </div>

                              );

                            }
                          )
                        }

                      </div>

                    )
                }


              </div>

            )}


          </section>

        )}


        {/* ===================================================
            QUIZZES PAGE
        =================================================== */}

        {activePage === "quizzes" && (

          <Quizzes />

        )}


        {/* ===================================================
            LABS PAGE
        =================================================== */}

        {activePage === "labs" && (

          <Labs />

        )}


        {/* ===================================================
            DEADLINES PAGE
        =================================================== */}

        {activePage === "deadlines" && (

          <Deadlines />

        )}


      </main>


    </div>

  );

}


export default App;
