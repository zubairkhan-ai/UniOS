import { useEffect, useState } from "react";
import "./CourseDetails.css";

const API_URL = "http://127.0.0.1:8000";

function CourseDetails({ courseCode, onBack }) {
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadCourse = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_URL}/courses/${encodeURIComponent(courseCode)}`
        );

        if (!response.ok) {
          throw new Error("Failed to load course");
        }

        const data = await response.json();

        if (data.error) {
          throw new Error(data.error);
        }

        setCourse(data);

      } catch (err) {

        console.error(
          "Course details error:",
          err
        );

        setError(
          "Unable to load this course."
        );

      } finally {

        setLoading(false);

      }
    };

    if (courseCode) {
      loadCourse();
    }

  }, [courseCode]);


  // =========================================================
  // OPEN LECTURE
  // =========================================================

  const openLecture = (lecture) => {

    const fileUrl =
      `${API_URL}/lectures/file?path=${encodeURIComponent(
        lecture.path
      )}`;

    if (
      lecture.type === "pdf"
    ) {

      window.open(
        fileUrl,
        "_blank",
        "noopener,noreferrer"
      );

      return;
    }

    // PPT / PPTX / DOCX etc.
    // Browser will download the file.

    const link =
      document.createElement("a");

    link.href = fileUrl;

    link.target = "_blank";

    link.rel = "noopener noreferrer";

    link.click();

  };


  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {

    return (
      <div className="course-details-loading">

        <div className="course-details-spinner">
          ⏳
        </div>

        <p>
          Loading course...
        </p>

      </div>
    );

  }


  // =========================================================
  // ERROR
  // =========================================================

  if (error) {

    return (

      <div className="course-details-page">

        <button
          className="course-back-button"
          onClick={onBack}
        >
          ← Back to Courses
        </button>

        <div className="course-details-error">

          ⚠️ {error}

        </div>

      </div>

    );

  }


  if (!course) {
    return null;
  }


  // =========================================================
  // TOTAL LECTURES
  // =========================================================

  const totalLectures =
    course.weeks.reduce(
      (total, week) =>
        total + week.lectures.length,
      0
    );


  // =========================================================
  // RENDER
  // =========================================================

  return (

    <div className="course-details-page">


      {/* =====================================================
          BACK BUTTON
      ===================================================== */}

      <button
        className="course-back-button"
        onClick={onBack}
      >
        ← Back to Courses
      </button>


      {/* =====================================================
          COURSE HEADER
      ===================================================== */}

      <div className="course-details-header">

        <div className="course-details-icon">
          📚
        </div>

        <div className="course-details-title">

          <span className="course-details-code">
            {course.code}
          </span>

          <h1>
            {course.name}
          </h1>

          <p>
            Explore your course lectures and weekly material.
          </p>

        </div>

      </div>


      {/* =====================================================
          COURSE SUMMARY
      ===================================================== */}

      <div className="course-details-summary">

        <div className="course-detail-stat">

          <span className="course-detail-stat-icon">
            📁
          </span>

          <div>

            <strong>
              {course.weeks.length}
            </strong>

            <span>
              {course.weeks.length === 1
                ? "Week"
                : "Weeks"}
            </span>

          </div>

        </div>


        <div className="course-detail-stat">

          <span className="course-detail-stat-icon">
            📄
          </span>

          <div>

            <strong>
              {totalLectures}
            </strong>

            <span>
              {totalLectures === 1
                ? "Lecture"
                : "Lectures"}
            </span>

          </div>

        </div>


        <div className="course-detail-stat">

          <span className="course-detail-stat-icon">
            🎓
          </span>

          <div>

            <strong>
              3
            </strong>

            <span>
              Credits
            </span>

          </div>

        </div>

      </div>


      {/* =====================================================
          COURSE MATERIAL
      ===================================================== */}

      <div className="course-weeks-section">

        <div className="course-weeks-heading">

          <div>

            <h2>
              📚 Course Material
            </h2>

            <p>
              Lectures organized by week.
            </p>

          </div>

          <span>

            {course.weeks.length}{" "}

            {course.weeks.length === 1
              ? "Week"
              : "Weeks"}

          </span>

        </div>


        <div className="course-weeks-list">

          {course.weeks.length === 0 ? (

            <div className="course-no-material">

              📂 No lecture material found.

            </div>

          ) : (

            course.weeks.map(
              (week, index) => (

                <div
                  className="course-week-card"
                  key={week.name}
                >

                  {/* =================================================
                      WEEK HEADER
                  ================================================= */}

                  <div className="course-week-header">

                    <div className="course-week-number">

                      {index + 1}

                    </div>

                    <div>

                      <h3>
                        {week.name}
                      </h3>

                      <p>

                        {week.lectures.length}{" "}

                        {week.lectures.length === 1
                          ? "lecture"
                          : "lectures"}

                      </p>

                    </div>

                  </div>


                  {/* =================================================
                      LECTURES
                  ================================================= */}

                  <div className="course-lecture-list">

                    {week.lectures.length === 0 ? (

                      <div className="course-empty-lecture">

                        No lectures in this week.

                      </div>

                    ) : (

                      week.lectures.map(
                        (lecture, lectureIndex) => (

                          <div
                            className="course-lecture-item"
                            key={lecture.path}
                          >

                            {/* FILE ICON */}

                            <div className="lecture-file-icon">

                              {lecture.type === "pdf"
                                ? "📕"
                                : lecture.type === "pptx" ||
                                  lecture.type === "ppt"
                                ? "📊"
                                : "📄"}

                            </div>


                            {/* FILE INFORMATION */}

                            <div className="lecture-file-info">

                              <h4>
                                {lecture.name}
                              </h4>

                              <span>

                                Lecture{" "}
                                {lectureIndex + 1}

                                {" • "}

                                {lecture.type.toUpperCase()}

                              </span>

                            </div>


                            {/* OPEN BUTTON */}

                            <button
                              className="lecture-open-button"
                              onClick={() =>
                                openLecture(
                                  lecture
                                )
                              }
                            >

                              {lecture.type === "pdf"
                                ? "Open →"
                                : "Download →"}

                            </button>

                          </div>

                        )
                      )

                    )}

                  </div>

                </div>

              )

            )

          )}

        </div>

      </div>

    </div>

  );
}

export default CourseDetails;