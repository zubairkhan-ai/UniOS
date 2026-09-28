import { useEffect, useMemo, useState } from "react";
import "./Labs.css";

const API_URL = "http://127.0.0.1:8000";

function Labs() {
  const [labs, setLabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showAddForm, setShowAddForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    course: "",
    title: "",
    due_date: "",
    description: "",
  });

  // ============================================================
  // LOAD LABS
  // ============================================================

  const loadLabs = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/labs`);

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      setLabs(data.labs || []);
    } catch (err) {
      console.error("Labs error:", err);

      setError(
        "Could not load labs. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLabs();
  }, []);

  // ============================================================
  // DATE
  // ============================================================

  const today = new Date().toISOString().split("T")[0];

  // ============================================================
  // FILTER LABS
  // ============================================================

  const pendingLabs = useMemo(() => {
    return labs.filter(
      (lab) => lab.status === "pending"
    );
  }, [labs]);

  const completedLabs = useMemo(() => {
    return labs.filter(
      (lab) => lab.status === "completed"
    );
  }, [labs]);

  const overdueLabs = useMemo(() => {
    return pendingLabs.filter(
      (lab) => lab.due_date < today
    );
  }, [pendingLabs, today]);

  const upcomingLabs = useMemo(() => {
    return pendingLabs.filter(
      (lab) => lab.due_date >= today
    );
  }, [pendingLabs, today]);

  // ============================================================
  // ADD LAB
  // ============================================================

  const handleAddLab = async (e) => {
    e.preventDefault();

    if (
      !form.course.trim() ||
      !form.title.trim() ||
      !form.due_date
    ) {
      alert("Please fill Course, Title and Due Date.");
      return;
    }

    setSaving(true);

    try {
      const response = await fetch(
        `${API_URL}/labs`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            course: form.course.trim(),
            title: form.title.trim(),
            due_date: form.due_date,
            description: form.description.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(
          data.error || "Failed to add lab"
        );
      }

      setForm({
        course: "",
        title: "",
        due_date: "",
        description: "",
      });

      setShowAddForm(false);

      await loadLabs();
    } catch (err) {
      console.error("Add lab error:", err);

      alert(
        err.message ||
          "Could not add lab."
      );
    } finally {
      setSaving(false);
    }
  };

  // ============================================================
  // COMPLETE LAB
  // ============================================================

  const handleComplete = async (id) => {
    try {
      const response = await fetch(
        `${API_URL}/labs/${id}/complete`,
        {
          method: "PATCH",
        }
      );

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(
          data.error || "Failed to complete lab"
        );
      }

      await loadLabs();
    } catch (err) {
      console.error(
        "Complete lab error:",
        err
      );

      alert(
        err.message ||
          "Could not complete lab."
      );
    }
  };

  // ============================================================
  // DELETE LAB
  // ============================================================

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this lab?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/labs/${id}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(
          data.error || "Failed to delete lab"
        );
      }

      await loadLabs();
    } catch (err) {
      console.error(
        "Delete lab error:",
        err
      );

      alert(
        err.message ||
          "Could not delete lab."
      );
    }
  };

  // ============================================================
  // FORMAT DATE
  // ============================================================

  const formatDate = (dateString) => {
    if (!dateString) {
      return "No date";
    }

    const date = new Date(
      `${dateString}T00:00:00`
    );

    return date.toLocaleDateString(
      "en-US",
      {
        year: "numeric",
        month: "short",
        day: "numeric",
      }
    );
  };

  // ============================================================
  // LAB CARD
  // ============================================================

  const LabCard = ({ lab, completed = false }) => {
    const isOverdue =
      !completed &&
      lab.due_date < today;

    return (
      <div
        className={`lab-card ${
          isOverdue
            ? "lab-card-overdue"
            : ""
        }`}
      >
        <div className="lab-icon">
          🧪
        </div>

        <div className="lab-main">
          <div className="lab-title-row">
            <h3>
              {lab.title}
            </h3>

            {isOverdue && (
              <span className="overdue-tag">
                Overdue
              </span>
            )}

            {completed && (
              <span className="completed-tag">
                Completed
              </span>
            )}
          </div>

          <p className="lab-course">
            {lab.course}
          </p>

          {lab.description && (
            <p className="lab-description">
              {lab.description}
            </p>
          )}
        </div>

        <div className="lab-right">
          <div className="lab-date">
            <span>Due</span>
            <strong>
              {formatDate(
                lab.due_date
              )}
            </strong>
          </div>

          {!completed && (
            <div className="lab-actions">
              <button
                className="complete-btn"
                onClick={() =>
                  handleComplete(
                    lab.id
                  )
                }
              >
                ✓ Complete
              </button>

              <button
                className="delete-btn"
                onClick={() =>
                  handleDelete(
                    lab.id
                  )
                }
              >
                Delete
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="labs-page">

      {/* PAGE HEADER */}

      <div className="labs-header">
        <div>
          <h1>My Labs</h1>

          <p>
            Track your upcoming, overdue,
            and completed labs.
          </p>
        </div>

        <div className="labs-header-actions">

          <button
                className="refresh-btn"
                onClick={loadLabs}
                disabled={loading}
            >
                <span className="refresh-icon">↻</span>

                <span>
                    {loading ? "Loading..." : "Refresh"}
                </span>
          </button>
          <button
            className="add-lab-btn"
            onClick={() =>
              setShowAddForm(
                (prev) => !prev
              )
            }
          >
            + Add Lab
          </button>

        </div>
      </div>

      {/* ERROR */}

      {error && (
        <div className="labs-error">
          ⚠️ {error}
        </div>
      )}

      {/* ADD LAB FORM */}

      {showAddForm && (
        <div className="add-lab-panel">

          <div className="add-lab-header">
            <div>
              <h2>
                Add New Lab
              </h2>

              <p>
                Add a lab to your university
                schedule.
              </p>
            </div>

            <button
              className="close-form-btn"
              onClick={() =>
                setShowAddForm(false)
              }
            >
              ×
            </button>
          </div>

          <form
            className="lab-form"
            onSubmit={handleAddLab}
          >

            <div className="form-grid">

              <div className="form-group">
                <label>
                  Course
                </label>

                <input
                  type="text"
                  placeholder="e.g. CN"
                  value={form.course}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      course:
                        e.target.value,
                    })
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  Lab Title
                </label>

                <input
                  type="text"
                  placeholder="e.g. Computer Networks Lab 4"
                  value={form.title}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      title:
                        e.target.value,
                    })
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  Due Date
                </label>

                <input
                  type="date"
                  value={form.due_date}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      due_date:
                        e.target.value,
                    })
                  }
                />
              </div>

              <div className="form-group form-description">
                <label>
                  Description
                </label>

                <input
                  type="text"
                  placeholder="Optional description"
                  value={form.description}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      description:
                        e.target.value,
                    })
                  }
                />
              </div>

            </div>

            <div className="form-actions">

              <button
                type="button"
                className="cancel-btn"
                onClick={() =>
                  setShowAddForm(false)
                }
              >
                Cancel
              </button>

              <button
                type="submit"
                className="save-lab-btn"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : "Save Lab"}
              </button>

            </div>

          </form>
        </div>
      )}

      {/* STATS */}

      <div className="lab-stats">

        <div className="stat-card">
          <div className="stat-icon">
            🧪
          </div>

          <div>
            <span>Total Labs</span>
            <strong>
              {labs.length}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            ⏳
          </div>

          <div>
            <span>Pending</span>
            <strong>
              {pendingLabs.length}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            ⚠️
          </div>

          <div>
            <span>Overdue</span>
            <strong>
              {overdueLabs.length}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            ✅
          </div>

          <div>
            <span>Completed</span>
            <strong>
              {completedLabs.length}
            </strong>
          </div>
        </div>

      </div>

      {/* TWO COLUMNS */}

      <div className="labs-columns">

        {/* UPCOMING */}

        <section className="labs-section">

          <div className="section-header">

            <div>
              <h2>
                🧪 Upcoming Labs
              </h2>

              <p>
                Labs you still need
                to complete.
              </p>
            </div>

            <span className="section-count">
              {upcomingLabs.length}
            </span>

          </div>

          <div className="section-list">

            {loading ? (
              <div className="empty-box">
                <div className="spinner"></div>
                <p>
                  Loading labs...
                </p>
              </div>
            ) : upcomingLabs.length ===
              0 ? (
              <div className="empty-box">
                <div className="empty-icon">
                  🎉
                </div>

                <h3>
                  No upcoming labs
                </h3>

                <p>
                  You're all caught up.
                </p>
              </div>
            ) : (
              upcomingLabs.map(
                (lab) => (
                  <LabCard
                    key={lab.id}
                    lab={lab}
                  />
                )
              )
            )}

          </div>
        </section>

        {/* OVERDUE */}

        <section className="labs-section">

          <div className="section-header">

            <div>
              <h2>
                ⚠️ Overdue Labs
              </h2>

              <p>
                These labs have passed
                their due date.
              </p>
            </div>

            <span className="section-count overdue-count">
              {overdueLabs.length}
            </span>

          </div>

          <div className="section-list">

            {overdueLabs.length ===
            0 ? (
              <div className="empty-box">
                <div className="empty-icon">
                  🎉
                </div>

                <h3>
                  No overdue labs
                </h3>

                <p>
                  Nice work — you're
                  on track.
                </p>
              </div>
            ) : (
              overdueLabs.map(
                (lab) => (
                  <LabCard
                    key={lab.id}
                    lab={lab}
                  />
                )
              )
            )}

          </div>
        </section>

      </div>

      {/* COMPLETED */}

      <section className="completed-section">

        <div className="section-header">

          <div>
            <h2>
              ✅ Completed Labs
            </h2>

            <p>
              Your finished labs.
            </p>
          </div>

          <span className="section-count completed-count">
            {completedLabs.length}
          </span>

        </div>

        {completedLabs.length ===
        0 ? (
          <div className="empty-box completed-empty">
            <div className="empty-icon">
              📚
            </div>

            <h3>
              No completed labs
            </h3>

            <p>
              Completed labs will
              appear here.
            </p>
          </div>
        ) : (
          <div className="completed-list">
            {completedLabs.map(
              (lab) => (
                <LabCard
                  key={lab.id}
                  lab={lab}
                  completed
                />
              )
            )}
          </div>
        )}

      </section>

    </div>
  );
}

export default Labs;