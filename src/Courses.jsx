import { useEffect, useState } from "react";
import "./Courses.css";
import CourseDetails from "./CourseDetails";

const API_URL = "http://127.0.0.1:8000";

function Courses() {
  const [courses, setCourses] = useState([]);

  const [loading, setLoading] = useState(true);

  const [refreshing, setRefreshing] = useState(false);

  const [error, setError] = useState("");

  const [showAddCourse, setShowAddCourse] = useState(false);

  // =========================================================
  // SELECTED COURSE
  // Used for opening CourseDetails page
  // =========================================================

  const [selectedCourse, setSelectedCourse] = useState(null);

  const [newCourse, setNewCourse] = useState({
    code: "",
    name: "",
    instructor: "",
    credits: 3,
    color: "blue",
  });


  // =========================================================
  // LOAD MANUALLY ADDED COURSES
  // =========================================================

  const getManualCourses = () => {
    try {
      const savedCourses =
        localStorage.getItem("unios_manual_courses");

      if (!savedCourses) {
        return [];
      }

      const parsedCourses =
        JSON.parse(savedCourses);

      return Array.isArray(parsedCourses)
        ? parsedCourses
        : [];

    } catch (error) {

      console.error(
        "Manual courses error:",
        error
      );

      return [];
    }
  };


  // =========================================================
  // SAVE MANUALLY ADDED COURSES
  // =========================================================

  const saveManualCourses = (manualCourses) => {

    localStorage.setItem(
      "unios_manual_courses",
      JSON.stringify(manualCourses)
    );

  };


  // =========================================================
  // COURSE COLOR
  // =========================================================

  const getCourseColor = (code, index) => {

    const colors = [
      "blue",
      "purple",
      "green",
      "orange",
      "pink",
    ];

    const knownColors = {
      OS: "blue",
      DAA: "purple",
      OOP: "green",
      CN: "blue",
      RL: "purple",
      CV: "green",
      COAL: "orange",
      KRR: "pink",
    };

    return (
      knownColors[code] ||
      colors[index % colors.length]
    );

  };


  // =========================================================
  // COURSE ICON
  // =========================================================

  const getCourseIcon = (code) => {

    const icons = {
      OS: "💻",
      DAA: "🧮",
      OOP: "🤖",
      CN: "🌐",
      RL: "🤖",
      CV: "👁️",
      COAL: "💻",
      KRR: "🧠",
    };

    return icons[code] || "📚";

  };


  // =========================================================
  // LOAD COURSES FROM BACKEND
  // =========================================================

  const fetchCourses = async (
    isRefresh = false
  ) => {

    try {

      setError("");

      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }


      // =====================================================
      // GET ACTUAL COURSES FROM DATA/LECTURES
      // =====================================================

      const coursesResponse =
        await fetch(
          `${API_URL}/courses`
        );


      if (!coursesResponse.ok) {

        throw new Error(
          `Courses server returned ${coursesResponse.status}`
        );

      }


      const backendCourses =
        await coursesResponse.json();


      // =====================================================
      // GET ASSIGNMENTS / QUIZZES / LABS
      // =====================================================

      let allTasks = [];

      try {

        const dashboardResponse =
          await fetch(
            `${API_URL}/dashboard`
          );


        if (dashboardResponse.ok) {

          const dashboardData =
            await dashboardResponse.json();


          allTasks = [
            ...(dashboardData.upcoming || []),
            ...(dashboardData.overdue || []),
          ];

        }

      } catch (taskError) {

        console.warn(
          "Could not load task counts:",
          taskError
        );

      }


      // =====================================================
      // FORMAT BACKEND COURSES
      // =====================================================

      const formattedCourses =
        backendCourses.map(
          (course, index) => {

            const courseCode =
              String(
                course.code || ""
              ).trim();


            const courseTasks =
              allTasks.filter(
                (task) =>
                  String(
                    task.course || ""
                  )
                    .trim()
                    .toLowerCase() ===
                  courseCode.toLowerCase()
              );


            const assignments =
              courseTasks.filter(
                (task) =>
                  String(
                    task.task_type ||
                    "assignment"
                  ).toLowerCase() ===
                  "assignment"
              ).length;


            const quizzes =
              courseTasks.filter(
                (task) =>
                  String(
                    task.task_type || ""
                  ).toLowerCase() ===
                  "quiz"
              ).length;


            const labs =
              courseTasks.filter(
                (task) =>
                  String(
                    task.task_type || ""
                  ).toLowerCase() ===
                  "lab"
              ).length;


            return {

              ...course,

              code: courseCode,

              name:
                course.name ||
                courseCode,

              instructor:
                course.instructor ||
                "Course Instructor",

              credits:
                Number(course.credits) || 3,

              weeks:
                Number(course.weeks) || 0,

              lectures:
                Number(course.lectures) || 0,

              assignments,

              quizzes,

              labs,

              progress: 0,

              color:
                getCourseColor(
                  courseCode,
                  index
                ),

            };

          }
        );


      // =====================================================
      // MANUALLY ADDED COURSES
      // =====================================================

      const manualCourses =
        getManualCourses();


      // =====================================================
      // ADD MANUAL COURSES
      // WITHOUT DUPLICATING BACKEND COURSES
      // =====================================================

      const backendCodes =
        formattedCourses.map(
          (course) =>
            course.code.toLowerCase()
        );


      const uniqueManualCourses =
        manualCourses.filter(
          (course) =>
            !backendCodes.includes(
              String(
                course.code || ""
              ).toLowerCase()
            )
        );


      const finalCourses = [
        ...formattedCourses,
        ...uniqueManualCourses,
      ];


      setCourses(
        finalCourses
      );


    } catch (error) {

      console.error(
        "Courses error:",
        error
      );


      setError(
        "Could not load courses from the backend. Make sure FastAPI is running."
      );


      // Keep manually added courses visible
      const manualCourses =
        getManualCourses();

      setCourses(
        manualCourses
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

    fetchCourses();

  }, []);


  // =========================================================
  // ADD COURSE FORM CHANGE
  // =========================================================

  const handleCourseChange = (e) => {

    const {
      name,
      value,
    } = e.target;


    setNewCourse(
      (prev) => ({
        ...prev,
        [name]: value,
      })
    );

  };


  // =========================================================
  // ADD COURSE
  // =========================================================

  const addCourse = (e) => {

    e.preventDefault();


    const code =
      newCourse.code
        .trim()
        .toUpperCase();


    const name =
      newCourse.name.trim();


    const instructor =
      newCourse.instructor.trim();


    if (!code || !name) {

      alert(
        "Please enter course code and course name."
      );

      return;

    }


    // Check existing course

    const exists =
      courses.some(
        (course) =>
          String(
            course.code
          )
            .trim()
            .toLowerCase() ===
          code.toLowerCase()
      );


    if (exists) {

      alert(
        "A course with this code already exists."
      );

      return;

    }


    const manualCourses =
      getManualCourses();


    const course = {

      code,

      name,

      instructor:
        instructor ||
        "Course Instructor",

      credits:
        Number(
          newCourse.credits
        ) || 3,

      weeks: 0,

      lectures: 0,

      assignments: 0,

      quizzes: 0,

      labs: 0,

      progress: 0,

      color:
        newCourse.color ||
        "blue",

      manual: true,

    };


    const updatedManualCourses = [
      ...manualCourses,
      course,
    ];


    saveManualCourses(
      updatedManualCourses
    );


    setCourses(
      (prev) => [
        ...prev,
        course,
      ]
    );


    // Reset form

    setNewCourse({

      code: "",

      name: "",

      instructor: "",

      credits: 3,

      color: "blue",

    });


    setShowAddCourse(false);

  };


  // =========================================================
  // DELETE MANUALLY ADDED COURSE
  // =========================================================

  const deleteCourse = (
    courseCode
  ) => {

    const course =
      courses.find(
        (item) =>
          item.code === courseCode
      );


    if (!course) {
      return;
    }


    // Don't allow deleting
    // courses coming from lectures folder

    if (!course.manual) {

      alert(
        "This course comes from your lecture folder. Remove or rename its folder from data/lectures instead."
      );

      return;

    }


    const confirmed =
      window.confirm(
        `Are you sure you want to remove ${course.name}?`
      );


    if (!confirmed) {
      return;
    }


    const manualCourses =
      getManualCourses();


    const updatedManualCourses =
      manualCourses.filter(
        (item) =>
          item.code !==
          courseCode
      );


    saveManualCourses(
      updatedManualCourses
    );


    setCourses(
      (prev) =>
        prev.filter(
          (item) =>
            item.code !==
            courseCode
        )
    );

  };


  // =========================================================
  // TOTALS
  // =========================================================

  const totalCourses =
    courses.length;


  const totalCredits =
    courses.reduce(
      (total, course) =>
        total +
        Number(
          course.credits || 0
        ),
      0
    );


  const totalAssignments =
    courses.reduce(
      (total, course) =>
        total +
        Number(
          course.assignments || 0
        ),
      0
    );


  const totalQuizzes =
    courses.reduce(
      (total, course) =>
        total +
        Number(
          course.quizzes || 0
        ),
      0
    );


  const totalLabs =
    courses.reduce(
      (total, course) =>
        total +
        Number(
          course.labs || 0
        ),
      0
    );


  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {

    return (

      <div className="courses-loading">

        <div className="courses-loading-spinner">
          ⏳
        </div>

        <p>
          Loading your courses...
        </p>

      </div>

    );

  }


  // =========================================================
  // COURSE DETAILS PAGE
  // =========================================================

  if (selectedCourse) {

    return (
      <CourseDetails
        courseCode={selectedCourse}
        onBack={() => setSelectedCourse(null)}
      />
    );

  }


  // =========================================================
  // RENDER
  // =========================================================

  return (

    <div className="courses-page">


      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="courses-header">

        <div>

          <h1>
            Courses
          </h1>

          <p>
            Manage your courses and keep track of your academic work.
          </p>

        </div>


        <div className="courses-header-actions">

          <button
            className="courses-add-button"
            onClick={() =>
              setShowAddCourse(
                (prev) => !prev
              )
            }
          >
            ➕ Add Course
          </button>


          <button
            className="courses-refresh-button"
            onClick={() =>
              fetchCourses(true)
            }
            disabled={refreshing}
          >

            <span
              className={
                refreshing
                  ? "courses-refresh-icon spinning"
                  : "courses-refresh-icon"
              }
            >
              🔄
            </span>

            {refreshing
              ? "Refreshing..."
              : "Refresh"}

          </button>

        </div>

      </div>


      {/* =====================================================
          ADD COURSE FORM
      ===================================================== */}

      {showAddCourse && (

        <form
          className="add-course-card"
          onSubmit={addCourse}
        >

          <div className="add-course-title">

            <div>

              <h2>
                ➕ Add New Course
              </h2>

              <p>
                Add a course to your current semester.
              </p>

            </div>

          </div>


          <div className="add-course-grid">


            <div className="course-form-group">

              <label>
                Course Code *
              </label>

              <input
                type="text"
                name="code"
                value={
                  newCourse.code
                }
                onChange={
                  handleCourseChange
                }
                placeholder="e.g. AI"
                required
              />

            </div>


            <div className="course-form-group">

              <label>
                Course Name *
              </label>

              <input
                type="text"
                name="name"
                value={
                  newCourse.name
                }
                onChange={
                  handleCourseChange
                }
                placeholder="e.g. Artificial Intelligence"
                required
              />

            </div>


            <div className="course-form-group">

              <label>
                Instructor
              </label>

              <input
                type="text"
                name="instructor"
                value={
                  newCourse.instructor
                }
                onChange={
                  handleCourseChange
                }
                placeholder="e.g. Dr. Ahmad"
              />

            </div>


            <div className="course-form-group">

              <label>
                Credits
              </label>

              <select
                name="credits"
                value={
                  newCourse.credits
                }
                onChange={
                  handleCourseChange
                }
              >

                <option value="1">
                  1 Credit
                </option>

                <option value="2">
                  2 Credits
                </option>

                <option value="3">
                  3 Credits
                </option>

                <option value="4">
                  4 Credits
                </option>

                <option value="5">
                  5 Credits
                </option>

              </select>

            </div>


            <div className="course-form-group">

              <label>
                Course Color
              </label>

              <select
                name="color"
                value={
                  newCourse.color
                }
                onChange={
                  handleCourseChange
                }
              >

                <option value="blue">
                  Blue
                </option>

                <option value="purple">
                  Purple
                </option>

                <option value="green">
                  Green
                </option>

                <option value="orange">
                  Orange
                </option>

                <option value="pink">
                  Pink
                </option>

              </select>

            </div>

          </div>


          <div className="add-course-actions">

            <button
              type="button"
              className="course-cancel-button"
              onClick={() => {

                setShowAddCourse(false);

                setNewCourse({
                  code: "",
                  name: "",
                  instructor: "",
                  credits: 3,
                  color: "blue",
                });

              }}
            >
              Cancel
            </button>


            <button
              type="submit"
              className="course-save-button"
            >
              💾 Save Course
            </button>

          </div>

        </form>

      )}


      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <div className="courses-notice">

          <span>
            ⚠️
          </span>

          <p>
            {error}
          </p>

        </div>

      )}


      {/* =====================================================
          SUMMARY
      ===================================================== */}

      <div className="courses-summary">


        <div className="course-summary-card">

          <div className="course-summary-icon blue">
            📚
          </div>

          <div>

            <span>
              Total Courses
            </span>

            <strong>
              {totalCourses}
            </strong>

          </div>

        </div>


        <div className="course-summary-card">

          <div className="course-summary-icon purple">
            🎓
          </div>

          <div>

            <span>
              Total Credits
            </span>

            <strong>
              {totalCredits}
            </strong>

          </div>

        </div>


        <div className="course-summary-card">

          <div className="course-summary-icon orange">
            📝
          </div>

          <div>

            <span>
              Assignments
            </span>

            <strong>
              {totalAssignments}
            </strong>

          </div>

        </div>


        <div className="course-summary-card">

          <div className="course-summary-icon yellow">
            ❓
          </div>

          <div>

            <span>
              Quizzes
            </span>

            <strong>
              {totalQuizzes}
            </strong>

          </div>

        </div>


        <div className="course-summary-card">

          <div className="course-summary-icon green">
            🧪
          </div>

          <div>

            <span>
              Labs
            </span>

            <strong>
              {totalLabs}
            </strong>

          </div>

        </div>


      </div>


      {/* =====================================================
          MY COURSES
      ===================================================== */}

      <div className="courses-section-header">

        <div>

          <h2>
            📚 My Courses
          </h2>

          <p>
            Your current semester courses.
          </p>

        </div>


        <span className="course-count">
          {courses.length}
        </span>

      </div>


      {/* =====================================================
          COURSE GRID
      ===================================================== */}

      {courses.length === 0 ? (

        <div className="courses-empty">

          <div className="courses-empty-icon">
            📚
          </div>

          <h3>
            No courses found
          </h3>

          <p>
            Add a course or place lecture files inside data/lectures.
          </p>

          <button
            className="courses-empty-button"
            onClick={() =>
              setShowAddCourse(true)
            }
          >
            ➕ Add Course
          </button>

        </div>

      ) : (

        <div className="courses-grid">

          {courses.map(
            (course) => (

              <div
                className={`course-card ${
                  course.color || "blue"
                }`}
                key={course.code}
              >


                {/* COURSE TOP */}

                <div className="course-card-top">

                  <div
                    className={`course-icon ${
                      course.color || "blue"
                    }`}
                  >

                    {getCourseIcon(
                      course.code
                    )}

                  </div>


                  <span className="course-code">

                    {course.code}

                  </span>

                </div>


                {/* COURSE INFO */}

                <div className="course-info">

                  <h3>
                    {course.name}
                  </h3>


                  <p className="course-instructor">

                    👨‍🏫{" "}

                    {course.instructor ||
                      "Course Instructor"}

                  </p>


                  <span className="course-credits">

                    {course.credits}{" "}

                    {Number(
                      course.credits
                    ) === 1
                      ? "Credit"
                      : "Credits"}

                  </span>

                </div>


                {/* LECTURE INFORMATION */}

                <div className="course-lecture-info">

                  <div>

                    <span>
                      📖
                    </span>

                    <strong>
                      {course.weeks || 0}
                    </strong>

                    <small>
                      {Number(course.weeks) === 1
                        ? "Week"
                        : "Weeks"}
                    </small>

                  </div>


                  <div>

                    <span>
                      📄
                    </span>

                    <strong>
                      {course.lectures || 0}
                    </strong>

                    <small>
                      {Number(course.lectures) === 1
                        ? "Lecture"
                        : "Lectures"}
                    </small>

                  </div>

                </div>


                {/* PROGRESS */}

                <div className="course-progress">

                  <div className="course-progress-header">

                    <span>
                      Progress
                    </span>

                    <strong>
                      {course.progress || 0}%
                    </strong>

                  </div>


                  <div className="course-progress-bar">

                    <div
                      className="course-progress-fill"
                      style={{
                        width: `${
                          course.progress ||
                          0
                        }%`,
                      }}
                    ></div>

                  </div>

                </div>


                {/* TASK STATS */}

                <div className="course-task-stats">


                  <div>

                    <span>
                      📝
                    </span>

                    <strong>
                      {course.assignments || 0}
                    </strong>

                    <small>
                      Assignments
                    </small>

                  </div>


                  <div>

                    <span>
                      ❓
                    </span>

                    <strong>
                      {course.quizzes || 0}
                    </strong>

                    <small>
                      Quizzes
                    </small>

                  </div>


                  <div>

                    <span>
                      🧪
                    </span>

                    <strong>
                      {course.labs || 0}
                    </strong>

                    <small>
                      Labs
                    </small>

                  </div>


                </div>


                {/* ACTIONS */}

                <div className="course-card-actions">

                  <button
                    className="view-course-button"
                    onClick={() =>
                      setSelectedCourse(
                        course.code
                      )
                    }
                  >

                    View Course →

                  </button>


                  {course.manual && (

                    <button
                      className="delete-course-button"
                      onClick={() =>
                        deleteCourse(
                          course.code
                        )
                      }
                      title="Remove course"
                    >
                      🗑️
                    </button>

                  )}

                </div>


              </div>

            )
          )}

        </div>

      )}


    </div>

  );
}

export default Courses;