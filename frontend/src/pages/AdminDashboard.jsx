import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import "./AdminDashboard.css";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";
const DJANGO_ADMIN_URL = "http://127.0.0.1:8000/admin/";

function AdminDashboard() {
  const navigate = useNavigate();
  const accessToken = localStorage.getItem("access_token");

  const [healthData, setHealthData] = useState(null);
  const [fraudLogs, setFraudLogs] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const openAdmin = () => {
    window.open(DJANGO_ADMIN_URL, "_blank");
  };

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }
    loadAdminData();
  }, [accessToken, navigate]);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      setError("");

      const headers = {
        Authorization: `Bearer ${accessToken}`,
      };

      const [healthRes, fraudRes, auditRes] = await Promise.all([
        fetch(`${DJANGO_BASE_URL}/api/system/health/`, { headers }),
        fetch(`${DJANGO_BASE_URL}/api/transactions/fraud-logs/`, { headers }),
        fetch(`${DJANGO_BASE_URL}/api/audit-logs/`, { headers }),
      ]);

      if (healthRes.status === 401 || fraudRes.status === 401) {
        localStorage.clear();
        navigate("/login");
        return;
      }

      if (healthRes.ok) {
        const hData = await healthRes.json();
        setHealthData(hData);
      }

      if (fraudRes.ok) {
        const fData = await fraudRes.json();
        setFraudLogs(fData.fraud_logs || []);
      }

      if (auditRes.ok) {
        const aData = await auditRes.json();
        setAuditLogs(aData.audit_logs || []);
      }
    } catch (err) {
      setError(err.message || "Failed to load administrative monitoring data.");
    } finally {
      setLoading(false);
    }
  };

  const handleReviewFraud = async (logId, newStatus) => {
    try {
      setActionMessage("");
      const res = await fetch(
        `${DJANGO_BASE_URL}/api/transactions/fraud-logs/${logId}/review/`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to update fraud log status.");
      }

      setActionMessage(`Fraud alert #${logId} marked as ${newStatus}.`);
      loadAdminData();
    } catch (err) {
      setError(err.message || "Error updating fraud status.");
    }
  };

  const handleExport = async (type) => {
    try {
      let endpoint = "";
      let filename = "";

      if (type === "analytics_pdf") {
        endpoint = `${DJANGO_BASE_URL}/api/transactions/analytics/export/pdf/?all=true`;
        filename = "analytics_summary.pdf";
      } else if (type === "analytics_csv") {
        endpoint = `${DJANGO_BASE_URL}/api/transactions/analytics/export/csv/?all=true`;
        filename = "analytics_summary.csv";
      } else if (type === "transactions_csv") {
        endpoint = `${DJANGO_BASE_URL}/api/transactions/export/csv/?all=true`;
        filename = "transactions_export.csv";
      }

      const res = await fetch(endpoint, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (!res.ok) throw new Error("Export download failed.");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "Unable to download export file.");
    }
  };

  return (
    <div className="admin-page">
      {/* PAGE HEADER */}
      <section className="admin-intro">
        <div>
          <span className="admin-overline">SYSTEM ADMINISTRATION & MONITORING</span>
          <h1>Admin Health & Security Dashboard</h1>
          <p>
            Real-time API response metrics, rule-based fraud detection, audit logging,
            and administrative controls.
          </p>
        </div>

        <div className="admin-status">
          <span
            className={`admin-status-dot ${
              healthData?.status === "HEALTHY" ? "dot-healthy" : "dot-warning"
            }`}
          ></span>
          <div>
            <strong>
              {healthData?.status === "HEALTHY"
                ? "System Operational"
                : "System Monitoring Active"}
            </strong>
            <small>Database Latency: {healthData?.database?.latency_ms ?? 0} ms</small>
          </div>
        </div>
      </section>

      {error && <div className="admin-alert-banner alert-error">{error}</div>}
      {actionMessage && (
        <div className="admin-alert-banner alert-success">{actionMessage}</div>
      )}

      {/* HEALTH & PERFORMANCE METRICS */}
      <section className="health-metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span>API Response Time</span>
            <span className="metric-tag">Avg</span>
          </div>
          <h3>{healthData?.performance?.avg_response_time_ms ?? "0.0"} ms</h3>
          <p>
            Slow Requests (&gt;500ms):{" "}
            <strong>{healthData?.performance?.slow_requests_count ?? 0}</strong>
          </p>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>API Failure Rate</span>
            <span className="metric-tag error-tag">Health</span>
          </div>
          <h3>{healthData?.performance?.error_rate_percentage ?? "0.0"}%</h3>
          <p>
            Errors (4xx/5xx):{" "}
            <strong>
              {(healthData?.performance?.status_distribution?.["4xx"] || 0) +
                (healthData?.performance?.status_distribution?.["5xx"] || 0)}
            </strong>
          </p>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Total API Requests</span>
            <span className="metric-tag">Audited</span>
          </div>
          <h3>{healthData?.performance?.total_requests ?? 0}</h3>
          <p>
            Success 2xx:{" "}
            <strong>
              {healthData?.performance?.status_distribution?.["2xx"] || 0}
            </strong>
          </p>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Fraud Alerts</span>
            <span className="metric-tag warning-tag">Security</span>
          </div>
          <h3>{healthData?.system_overview?.total_fraud_alerts ?? 0}</h3>
          <p>
            Pending Review:{" "}
            <strong className="text-warning">
              {healthData?.system_overview?.pending_fraud_reviews ?? 0}
            </strong>
          </p>
        </div>
      </section>

      {/* EXPORT DATA ACTIONS */}
      <section className="admin-export-bar">
        <div className="export-text">
          <h3>Data Export & Executive Reporting</h3>
          <p>Generate downloadable PDF or CSV snapshots for compliance and audits.</p>
        </div>
        <div className="export-actions">
          <button
            type="button"
            className="export-btn btn-pdf"
            onClick={() => handleExport("analytics_pdf")}
          >
            📄 Export Analytics PDF
          </button>
          <button
            type="button"
            className="export-btn btn-csv"
            onClick={() => handleExport("analytics_csv")}
          >
            📊 Export Analytics CSV
          </button>
          <button
            type="button"
            className="export-btn btn-csv-secondary"
            onClick={() => handleExport("transactions_csv")}
          >
            📑 Export Transactions CSV
          </button>
        </div>
      </section>

      {/* FRAUD LOGS & SECURITY AUDIT */}
      <section className="admin-tables-section">
        <div className="table-card">
          <div className="table-card-header">
            <div>
              <h2>🛡️ Rule-Based Fraud Detection Alerts</h2>
              <p>Suspicious activity flagged by burst & velocity detection engines.</p>
            </div>
            <span className="badge-count">{fraudLogs.length} Flagged</span>
          </div>

          <div className="admin-table-wrapper">
            <table className="admin-data-table">
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>User</th>
                  <th>Amount</th>
                  <th>Risk Level</th>
                  <th>Rule Triggered</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {fraudLogs.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center empty-cell">
                      No suspicious transactions flagged at this time.
                    </td>
                  </tr>
                ) : (
                  fraudLogs.map((log) => (
                    <tr key={log.id}>
                      <td>#{log.id}</td>
                      <td>
                        <strong>{log.username}</strong>
                        <br />
                        <small>{log.ip_address || "No IP"}</small>
                      </td>
                      <td>₹{Number(log.amount).toLocaleString("en-IN")}</td>
                      <td>
                        <span className={`risk-badge risk-${log.risk_level.toLowerCase()}`}>
                          {log.risk_level}
                        </span>
                      </td>
                      <td>
                        <div className="rule-desc">{log.rule_triggered}</div>
                        <small className="text-muted">{log.location}</small>
                      </td>
                      <td>
                        <span className={`status-pill status-${log.status.toLowerCase()}`}>
                          {log.status.replace("_", " ")}
                        </span>
                      </td>
                      <td>
                        {log.status === "UNDER_REVIEW" ? (
                          <div className="review-action-btns">
                            <button
                              type="button"
                              className="btn-resolve"
                              onClick={() => handleReviewFraud(log.id, "RESOLVED")}
                              title="Resolve Flag"
                            >
                              Resolve
                            </button>
                            <button
                              type="button"
                              className="btn-false"
                              onClick={() => handleReviewFraud(log.id, "FALSE_POSITIVE")}
                              title="False Positive"
                            >
                              False Pos
                            </button>
                            <button
                              type="button"
                              className="btn-confirm"
                              onClick={() => handleReviewFraud(log.id, "CONFIRMED")}
                              title="Confirm Fraud"
                            >
                              Confirm
                            </button>
                          </div>
                        ) : (
                          <small className="text-muted">Reviewed</small>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* RECENT AUDIT LOGS */}
        <div className="table-card">
          <div className="table-card-header">
            <div>
              <h2>📝 Administrative Audit Logs</h2>
              <p>Card blocks, unblocks, credit limit adjustments, and role updates.</p>
            </div>
            <span className="badge-count">{auditLogs.length} Entries</span>
          </div>

          <div className="admin-table-wrapper">
            <table className="admin-data-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Target</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center empty-cell">
                      No admin actions logged yet.
                    </td>
                  </tr>
                ) : (
                  auditLogs.slice(0, 10).map((log) => (
                    <tr key={log.id}>
                      <td>
                        <small>{new Date(log.created_at).toLocaleString("en-IN")}</small>
                      </td>
                      <td>
                        <strong>{log.actor_username || "System"}</strong>
                      </td>
                      <td>
                        <span className="audit-action-tag">{log.action}</span>
                      </td>
                      <td>
                        {log.target_type} #{log.target_id}
                      </td>
                      <td>
                        <small>{log.description}</small>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* DJANGO ADMIN INTEGRATION */}
      <section className="django-panel">
        <div className="django-panel-content">
          <span className="django-overline">CORE DJANGO ADMINISTRATION</span>
          <h2>Deep System Management</h2>
          <p>
            Direct access to raw models, database tables, group policies, and superuser
            maintenance console.
          </p>
          <button type="button" onClick={openAdmin} className="django-open-button">
            Open Django Admin Console <span>↗</span>
          </button>
        </div>
        <div className="django-panel-mark">DJANGO</div>
      </section>
    </div>
  );
}

export default AdminDashboard;