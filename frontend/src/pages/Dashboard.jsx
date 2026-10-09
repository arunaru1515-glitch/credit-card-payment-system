import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";

import "./Dashboard.css";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";
const FASTAPI_BASE_URL = "http://127.0.0.1:8001";

function Dashboard() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [cards, setCards] = useState([]);

  const [dashboardData, setDashboardData] = useState({
    total_transactions: 0,
    total_amount_spent: 0,
    current_month_spending: 0,
    available_credit_limit: 0,
    last_5_transactions: [],
  });

  const [analyticsData, setAnalyticsData] = useState({
    monthly_spending: [],
    category_expenses: [],
    credit_utilization: {
      total_credit_limit: 0,
      total_credit_spent: 0,
      available_credit: 0,
      utilization_percentage: 0,
      cards_breakdown: [],
    },
    overall_summary: {
      total_spent: 0,
      total_transactions: 0,
      successful_transactions: 0,
      failed_transactions: 0,
      average_transaction_amount: 0,
    },
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }

    loadDashboard();
  }, [accessToken, navigate]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const headers = {
        Authorization: `Bearer ${accessToken}`,
      };

      const [
        profileResponse,
        cardsResponse,
        dashboardResponse,
        analyticsResponse,
      ] = await Promise.all([
        fetch(`${DJANGO_BASE_URL}/api/profile/`, { headers }),
        fetch(`${DJANGO_BASE_URL}/api/cards/list/`, { headers }),
        fetch(`${FASTAPI_BASE_URL}/dashboard/summary`, { headers }),
        fetch(`${DJANGO_BASE_URL}/api/transactions/analytics/card-usage/`, { headers }),
      ]);

      if (
        profileResponse.status === 401 ||
        cardsResponse.status === 401 ||
        dashboardResponse.status === 401
      ) {
        localStorage.clear();
        navigate("/login");
        return;
      }

      const profileData = await profileResponse.json();
      const cardsData = await cardsResponse.json();
      const dashboardResponseData = await dashboardResponse.json();

      if (!profileResponse.ok) {
        throw new Error(profileData.detail || profileData.error || "Unable to load profile.");
      }
      if (!cardsResponse.ok) {
        throw new Error(cardsData.detail || cardsData.error || "Unable to load saved cards.");
      }
      if (!dashboardResponse.ok) {
        throw new Error(dashboardResponseData.detail || dashboardResponseData.error || "Unable to load dashboard summary.");
      }

      setUsername(profileData.username || "User");
      setCards(cardsData.cards || []);

      setDashboardData({
        total_transactions: dashboardResponseData.total_transactions || 0,
        total_amount_spent: dashboardResponseData.total_amount_spent || 0,
        current_month_spending: dashboardResponseData.current_month_spending || 0,
        available_credit_limit: dashboardResponseData.available_credit_limit || 0,
        last_5_transactions: dashboardResponseData.last_5_transactions || [],
      });

      if (analyticsResponse.ok) {
        const aData = await analyticsResponse.json();
        setAnalyticsData(aData);
      }

      localStorage.setItem("username", profileData.username || "User");
    } catch (err) {
      setError(err.message || "Unable to load dashboard.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (endpoint, defaultFilename) => {
    try {
      setError("");
      const res = await fetch(`${DJANGO_BASE_URL}${endpoint}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (!res.ok) throw new Error("Download failed.");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = defaultFilename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "Download failed.");
    }
  };

  const recentTransactions = dashboardData.last_5_transactions || [];
  const successfulTransactions = recentTransactions.filter((t) => t.status === "SUCCESS");
  const failedTransactions = recentTransactions.filter((t) => t.status === "FAILED");
  const pendingTransactions = recentTransactions.filter((t) => t.status === "PENDING");

  // Calculate highest monthly spend for chart height calculation
  const maxMonthlySpend = Math.max(
    ...(analyticsData.monthly_spending || []).map((m) => m.total_amount),
    1000
  );

  const utilizationPct = analyticsData.credit_utilization?.utilization_percentage || 0;

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-skeleton-container">
          <div className="skeleton skeleton-hero"></div>
          <div className="dashboard-skeleton-stats">
            <div className="skeleton skeleton-stat"></div>
            <div className="skeleton skeleton-stat"></div>
            <div className="skeleton skeleton-stat"></div>
            <div className="skeleton skeleton-stat"></div>
          </div>
        </div>
        <p>Loading dashboard analytics...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <main className="dashboard-container">
        {/* HERO */}
        <section className="dashboard-hero">
          <div className="hero-content">
            <span className="dashboard-overline">PAYMENT DASHBOARD</span>
            <h1>
              Welcome back, <strong>{username}</strong>
            </h1>
            <p>
              Review your spending summary, credit utilization, visual expense
              breakdown, and saved cards.
            </p>

            <div className="hero-action-buttons">
              <button
                type="button"
                className="statement-download-button"
                onClick={() =>
                  handleDownload(
                    "/api/transactions/monthly-statement/",
                    "monthly_statement.pdf"
                  )
                }
              >
                📄 Monthly Statement (PDF)
              </button>
              <button
                type="button"
                className="statement-download-button btn-outline"
                onClick={() =>
                  handleDownload(
                    "/api/transactions/analytics/export/pdf/",
                    "analytics_report.pdf"
                  )
                }
              >
                📊 Analytics Report (PDF)
              </button>
              <button
                type="button"
                className="statement-download-button btn-outline"
                onClick={() =>
                  handleDownload(
                    "/api/transactions/analytics/export/csv/",
                    "analytics_data.csv"
                  )
                }
              >
                📑 Analytics (CSV)
              </button>
            </div>
          </div>

          <div className="account-status">
            <span className="account-status-dot"></span>
            <div>
              <strong>Account Protected</strong>
              <span>RBAC & Fraud Shield Active</span>
            </div>
          </div>
        </section>

        {error && <div className="dashboard-error">{error}</div>}

        {/* PRIMARY STAT CARDS */}
        <section className="dashboard-stats">
          <div className="stat-card blue">
            <div className="stat-icon">₹</div>
            <div className="stat-content">
              <span>Total Spent</span>
              <strong>
                ₹
                {Number(dashboardData.total_amount_spent || 0).toLocaleString(
                  "en-IN",
                  { minimumFractionDigits: 2 }
                )}
              </strong>
            </div>
          </div>

          <div className="stat-card purple">
            <div className="stat-icon">💳</div>
            <div className="stat-content">
              <span>Available Credit</span>
              <strong>
                ₹
                {Number(
                  dashboardData.available_credit_limit || 0
                ).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </strong>
            </div>
          </div>

          <div className="stat-card green">
            <div className="stat-icon">📈</div>
            <div className="stat-content">
              <span>Current Month</span>
              <strong>
                ₹
                {Number(
                  dashboardData.current_month_spending || 0
                ).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </strong>
            </div>
          </div>

          <div className="stat-card orange">
            <div className="stat-icon">⚡</div>
            <div className="stat-content">
              <span>Credit Utilization</span>
              <strong>{utilizationPct}%</strong>
            </div>
          </div>
        </section>

        {/* =======================================================
            VISUAL ANALYTICS CHARTS SECTION
        ======================================================== */}
        <section className="analytics-charts-grid">
          {/* 1. MONTHLY SPENDING BAR CHART */}
          <div className="analytics-card monthly-chart-card">
            <div className="analytics-card-header">
              <div>
                <h2>📊 Monthly Spending Trend</h2>
                <p>Total expense breakdown across months in {analyticsData.year || 2026}</p>
              </div>
              <span className="analytics-pill">Annual Overview</span>
            </div>

            <div className="bar-chart-container">
              {(analyticsData.monthly_spending || []).map((item) => {
                const heightPct =
                  maxMonthlySpend > 0
                    ? Math.max(
                        8,
                        Math.round((item.total_amount / maxMonthlySpend) * 100)
                      )
                    : 8;
                return (
                  <div key={item.month} className="bar-column">
                    <div className="bar-wrapper" title={`₹${item.total_amount.toLocaleString("en-IN")} (${item.count} txns)`}>
                      <div
                        className={`chart-bar ${item.total_amount > 0 ? "bar-active" : "bar-empty"}`}
                        style={{ height: `${heightPct}%` }}
                      >
                        {item.total_amount > 0 && (
                          <span className="bar-tooltip">
                            ₹{item.total_amount >= 1000 ? `${(item.total_amount / 1000).toFixed(1)}k` : item.total_amount}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className="bar-label">{item.month_name}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 2. CATEGORY-WISE EXPENSE DATA */}
          <div className="analytics-card category-chart-card">
            <div className="analytics-card-header">
              <div>
                <h2>🛍️ Category-Wise Expenses</h2>
                <p>Distribution of spending across expense categories</p>
              </div>
              <span className="analytics-pill">Spending Share</span>
            </div>

            <div className="category-bars-list">
              {(analyticsData.category_expenses || []).map((cat) => (
                <div key={cat.category} className="category-row">
                  <div className="cat-header">
                    <span className="cat-name">{cat.category}</span>
                    <span className="cat-amount">
                      ₹{cat.total_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      <small> ({cat.percentage}%)</small>
                    </span>
                  </div>
                  <div className="cat-progress-track">
                    <div
                      className="cat-progress-fill"
                      style={{ width: `${Math.min(cat.percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3. CREDIT UTILIZATION GAUGE & BREAKDOWN */}
          <div className="analytics-card utilization-card">
            <div className="analytics-card-header">
              <div>
                <h2>💳 Credit Utilization Gauge</h2>
                <p>Proportion of total credit limit utilized</p>
              </div>
              <span
                className={`util-badge ${
                  utilizationPct > 80
                    ? "badge-danger"
                    : utilizationPct > 50
                    ? "badge-warning"
                    : "badge-safe"
                }`}
              >
                {utilizationPct > 80
                  ? "High Risk (>80%)"
                  : utilizationPct > 50
                  ? "Moderate (50-80%)"
                  : "Optimal (<50%)"}
              </span>
            </div>

            <div className="utilization-gauge-content">
              <div className="gauge-circle-wrapper">
                <svg viewBox="0 0 100 100" className="gauge-svg">
                  <circle
                    className="gauge-bg"
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                    strokeWidth="10"
                  />
                  <circle
                    className="gauge-val"
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                    strokeWidth="10"
                    strokeDasharray="251.2"
                    strokeDashoffset={251.2 - (251.2 * Math.min(utilizationPct, 100)) / 100}
                  />
                </svg>
                <div className="gauge-text">
                  <h3>{utilizationPct}%</h3>
                  <span>Utilized</span>
                </div>
              </div>

              <div className="util-stats-column">
                <div className="util-stat-row">
                  <span>Total Limit:</span>
                  <strong>
                    ₹
                    {Number(
                      analyticsData.credit_utilization?.total_credit_limit || 0
                    ).toLocaleString("en-IN")}
                  </strong>
                </div>
                <div className="util-stat-row">
                  <span>Used Credit:</span>
                  <strong>
                    ₹
                    {Number(
                      analyticsData.credit_utilization?.total_credit_spent || 0
                    ).toLocaleString("en-IN")}
                  </strong>
                </div>
                <div className="util-stat-row">
                  <span>Available:</span>
                  <strong className="text-success">
                    ₹
                    {Number(
                      analyticsData.credit_utilization?.available_credit || 0
                    ).toLocaleString("en-IN")}
                  </strong>
                </div>
              </div>
            </div>

            {/* PER-CARD BREAKDOWN */}
            <div className="card-util-breakdown">
              <h4>Credit Cards Detail</h4>
              {(analyticsData.credit_utilization?.cards_breakdown || []).map((c) => (
                <div key={c.card_id} className="card-util-item">
                  <span>{c.masked_card_number}</span>
                  <div className="card-util-bar-wrapper">
                    <div
                      className="card-util-bar-fill"
                      style={{ width: `${c.utilization_percentage}%` }}
                    ></div>
                  </div>
                  <strong>{c.utilization_percentage}%</strong>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* QUICK NAVIGATION */}
        <section className="quick-actions">
          <div className="quick-grid">
            <Link to="/add-card" className="quick-card blue-border">
              <div className="quick-icon blue">+</div>
              <div className="quick-content">
                <h3>Add New Card</h3>
                <p>Link a credit or debit card.</p>
              </div>
              <span className="quick-arrow">→</span>
            </Link>

            <Link to="/make-payment" className="quick-card purple-border">
              <div className="quick-icon purple">₹</div>
              <div className="quick-content">
                <h3>Make Payment</h3>
                <p>Process a secure transaction.</p>
              </div>
              <span className="quick-arrow">→</span>
            </Link>

            <Link to="/transactions" className="quick-card cyan-border">
              <div className="quick-icon cyan">≡</div>
              <div className="quick-content">
                <h3>Transaction History</h3>
                <p>Advanced search & filters.</p>
              </div>
              <span className="quick-arrow">→</span>
            </Link>

            <Link to="/admin-dashboard" className="quick-card slate-border">
              <div className="quick-icon slate">🛡️</div>
              <div className="quick-content">
                <h3>Admin & Security</h3>
                <p>Live health, logs & fraud alerts.</p>
              </div>
              <span className="quick-arrow">→</span>
            </Link>
          </div>
        </section>

        {/* LOWER SECTION: SAVED CARDS & LAST 5 TRANSACTIONS */}
        <section className="dashboard-lower-grid">
          {/* SAVED CARDS */}
          <div className="dashboard-panel">
            <div className="panel-heading">
              <div>
                <span>PAYMENT METHODS</span>
                <h2>Saved Cards</h2>
              </div>
              <Link to="/add-card">+ Add Card</Link>
            </div>

            {cards.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">+</div>
                <h3>No saved cards</h3>
                <p>Add a card to start making payments.</p>
                <Link to="/add-card">Add your first card</Link>
              </div>
            ) : (
              <div className="bank-card-grid">
                {cards.slice(0, 2).map((card, index) => (
                  <div key={card.id} className={`bank-card bank-card-${index}`}>
                    <div className="bank-card-top">
                      <span>{card.card_type === "credit" ? "CREDIT" : "DEBIT"}</span>
                      <small className={card.is_blocked ? "blocked-tag" : "active-tag"}>
                        {card.is_blocked ? "BLOCKED" : "ACTIVE"}
                      </small>
                    </div>
                    <div className="bank-card-chip"></div>
                    <div className="bank-card-number">{card.masked_card_number}</div>
                    <div className="bank-card-bottom">
                      <span>Card Limit</span>
                      <strong>₹{Number(card.credit_limit).toLocaleString("en-IN")}</strong>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* RECENT TRANSACTIONS */}
          <div className="dashboard-panel">
            <div className="panel-heading">
              <div>
                <span>RECENT ACTIVITY</span>
                <h2>Last 5 Transactions</h2>
              </div>
              <Link to="/transactions">View all</Link>
            </div>

            {recentTransactions.length === 0 ? (
              <div className="empty-state">
                <h3>No transactions yet</h3>
                <p>Recent transactions will appear here.</p>
              </div>
            ) : (
              <div className="transaction-list">
                {recentTransactions.map((tx, idx) => (
                  <div key={idx} className="transaction-row">
                    <div className="transaction-left">
                      <div className={`transaction-status status-${tx.status.toLowerCase()}`}>
                        {tx.status === "SUCCESS" ? "✓" : tx.status === "FAILED" ? "✕" : "⏱"}
                      </div>
                      <div>
                        <strong>
                          ₹{Number(tx.amount || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        </strong>
                        <span>{tx.masked_card_number || "Card"}</span>
                      </div>
                    </div>
                    <div className="transaction-right">
                      <strong className={`tx-status-${tx.status.toLowerCase()}`}>{tx.status}</strong>
                      <span>{tx.date ? new Date(tx.date).toLocaleDateString("en-IN") : "-"}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* SUMMARY BAR */}
        <section className="dashboard-summary">
          <div className="summary-item">
            <span className="summary-dot green"></span>
            <span>Successful</span>
            <strong>{successfulTransactions.length}</strong>
          </div>
          <div className="summary-divider"></div>
          <div className="summary-item">
            <span className="summary-dot orange"></span>
            <span>Pending</span>
            <strong>{pendingTransactions.length}</strong>
          </div>
          <div className="summary-divider"></div>
          <div className="summary-item">
            <span className="summary-dot red"></span>
            <span>Failed</span>
            <strong>{failedTransactions.length}</strong>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Dashboard;