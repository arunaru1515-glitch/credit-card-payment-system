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
      ] = await Promise.all([
        fetch(`${DJANGO_BASE_URL}/api/profile/`, {
          method: "GET",
          headers,
        }),

        fetch(`${DJANGO_BASE_URL}/api/cards/list/`, {
          method: "GET",
          headers,
        }),

        fetch(`${FASTAPI_BASE_URL}/dashboard/summary`, {
          method: "GET",
          headers,
        }),
      ]);

      // JWT authentication error
      if (
        profileResponse.status === 401 ||
        cardsResponse.status === 401 ||
        dashboardResponse.status === 401
      ) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("username");

        navigate("/login");
        return;
      }

      const profileData =
        await profileResponse.json();

      const cardsData =
        await cardsResponse.json();

      const dashboardResponseData =
        await dashboardResponse.json();

      // Profile error
      if (!profileResponse.ok) {
        throw new Error(
          profileData.detail ||
            profileData.error ||
            "Unable to load profile."
        );
      }

      // Cards error
      if (!cardsResponse.ok) {
        throw new Error(
          cardsData.detail ||
            cardsData.error ||
            "Unable to load saved cards."
        );
      }

      // Dashboard error
      if (!dashboardResponse.ok) {
        throw new Error(
          dashboardResponseData.detail ||
            dashboardResponseData.error ||
            "Unable to load dashboard summary."
        );
      }

      // Username
      setUsername(
        profileData.username || "User"
      );

      // Cards
      setCards(
        cardsData.cards || []
      );

      // Dashboard summary
      setDashboardData({
        total_transactions:
          dashboardResponseData.total_transactions || 0,

        total_amount_spent:
          dashboardResponseData.total_amount_spent || 0,

        current_month_spending:
          dashboardResponseData.current_month_spending || 0,

        available_credit_limit:
          dashboardResponseData.available_credit_limit || 0,

        last_5_transactions:
          dashboardResponseData.last_5_transactions || [],
      });

      localStorage.setItem(
        "username",
        profileData.username || "User"
      );

    } catch (err) {
      console.error(
        "Dashboard error:",
        err
      );

      setError(
        err.message ||
          "Unable to load dashboard."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // DOWNLOAD MONTHLY STATEMENT
  // ==========================================

  const downloadMonthlyStatement = async () => {
    try {
      setError("");

      const response = await fetch(
        `${DJANGO_BASE_URL}/api/transactions/monthly-statement/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      // JWT authentication error
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("username");

        navigate("/login");
        return;
      }

      // API error
      if (!response.ok) {
        const errorData =
          await response.json().catch(() => ({}));

        throw new Error(
          errorData.detail ||
            errorData.error ||
            "Unable to generate monthly statement."
        );
      }

      // Convert response to PDF blob
      const blob = await response.blob();

      // Create temporary download URL
      const url =
        window.URL.createObjectURL(blob);

      // Create download link
      const link =
        document.createElement("a");

      link.href = url;
      link.download =
        "monthly_statement.pdf";

      document.body.appendChild(link);

      link.click();

      link.remove();

      // Clean up temporary URL
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error(
        "Monthly statement error:",
        err
      );

      setError(
        err.message ||
          "Unable to download monthly statement."
      );
    }
  };

  // Last 5 transactions
  const recentTransactions =
    dashboardData.last_5_transactions || [];

  // Transaction status counts
  const successfulTransactions =
    recentTransactions.filter(
      (transaction) =>
        transaction.status === "SUCCESS"
    );

  const failedTransactions =
    recentTransactions.filter(
      (transaction) =>
        transaction.status === "FAILED"
    );

  const pendingTransactions =
    recentTransactions.filter(
      (transaction) =>
        transaction.status === "PENDING"
    );

  // ==========================================
  // LOADING
  // ==========================================

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

          <div className="dashboard-skeleton-lower">

            <div className="skeleton skeleton-panel"></div>

            <div className="skeleton skeleton-panel"></div>

          </div>

        </div>

        <p>
          Loading dashboard...
        </p>

      </div>
    );
  }

  return (
    <div className="dashboard-page">

      <main className="dashboard-container">

        {/* =====================================
            HERO SECTION
        ====================================== */}

        <section className="dashboard-hero">

          <div className="hero-content">

            <span className="dashboard-overline">
              PAYMENT DASHBOARD
            </span>

            <h1>
              Welcome back,{" "}
              <strong>
                {username}
              </strong>
            </h1>

            <p>
              Manage your payment methods,
              transactions, and account activity
              from one place.
            </p>

            {/* MONTHLY STATEMENT BUTTON */}

            <button
              type="button"
              className="statement-download-button"
              onClick={downloadMonthlyStatement}
            >
              Download Monthly Statement
            </button>

          </div>

          <div className="account-status">

            <span className="account-status-dot"></span>

            <div>

              <strong>
                Account Active
              </strong>

              <span>
                Secure access enabled
              </span>

            </div>

          </div>

        </section>

        {/* =====================================
            ERROR MESSAGE
        ====================================== */}

        {error && (
          <div className="dashboard-error">
            {error}
          </div>
        )}

        {/* =====================================
            TASK 1 REQUIRED STAT CARDS
        ====================================== */}

        <section className="dashboard-stats">

          {/* TOTAL SPENT */}

          <div className="stat-card blue">

            <div className="stat-icon">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path d="M4 7h16v10H4z" />
                <path d="M4 10h16" />
                <path d="M8 14h3" />
              </svg>

            </div>

            <div className="stat-content">

              <span>
                Total Spent
              </span>

              <strong>
                ₹
                {Number(
                  dashboardData.total_amount_spent || 0
                ).toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </strong>

            </div>

          </div>

          {/* AVAILABLE CREDIT */}

          <div className="stat-card purple">

            <div className="stat-icon">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <rect
                  x="3"
                  y="5"
                  width="18"
                  height="14"
                  rx="2"
                />

                <path d="M3 10h18" />

                <path d="M7 15h4" />

              </svg>

            </div>

            <div className="stat-content">

              <span>
                Available Credit
              </span>

              <strong>
                ₹
                {Number(
                  dashboardData.available_credit_limit || 0
                ).toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </strong>

            </div>

          </div>

          {/* TOTAL TRANSACTIONS */}

          <div className="stat-card green">

            <div className="stat-icon">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path d="M5 6h14" />
                <path d="M5 12h14" />
                <path d="M5 18h14" />
              </svg>

            </div>

            <div className="stat-content">

              <span>
                Total Transactions
              </span>

              <strong>
                {dashboardData.total_transactions}
              </strong>

            </div>

          </div>

          {/* THIS MONTH SPENDING */}

          <div className="stat-card orange">

            <div className="stat-icon rupee">
              ₹
            </div>

            <div className="stat-content">

              <span>
                This Month Spending
              </span>

              <strong>
                ₹
                {Number(
                  dashboardData.current_month_spending || 0
                ).toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </strong>

            </div>

          </div>

        </section>

        {/* =====================================
            QUICK ACTIONS
        ====================================== */}

        <section className="dashboard-section">

          <div className="section-heading">

            <span>
              OPERATIONS
            </span>

            <h2>
              Quick Actions
            </h2>

          </div>

          <div className="quick-actions">

            {/* ADD CARD */}

            <Link
              to="/add-card"
              className="quick-card blue-border"
            >

              <div className="quick-icon blue">
                +
              </div>

              <div className="quick-content">

                <h3>
                  Add Card
                </h3>

                <p>
                  Save a credit or debit
                  card for future payments.
                </p>

              </div>

              <span className="quick-arrow">
                →
              </span>

            </Link>

            {/* MAKE PAYMENT */}

            <Link
              to="/make-payment"
              className="quick-card purple-border"
            >

              <div className="quick-icon purple">
                ₹
              </div>

              <div className="quick-content">

                <h3>
                  Make Payment
                </h3>

                <p>
                  Make a payment using
                  one of your saved cards.
                </p>

              </div>

              <span className="quick-arrow">
                →
              </span>

            </Link>

            {/* TRANSACTION HISTORY */}

            <Link
              to="/transactions"
              className="quick-card cyan-border"
            >

              <div className="quick-icon cyan">
                ≡
              </div>

              <div className="quick-content">

                <h3>
                  Transaction History
                </h3>

                <p>
                  Review and filter your
                  complete payment history.
                </p>

              </div>

              <span className="quick-arrow">
                →
              </span>

            </Link>

            {/* ADMIN */}

            <Link
              to="/admin-dashboard"
              className="quick-card slate-border"
            >

              <div className="quick-icon slate">
                A
              </div>

              <div className="quick-content">

                <h3>
                  Admin Dashboard
                </h3>

                <p>
                  Manage users, cards,
                  transactions and summaries.
                </p>

              </div>

              <span className="quick-arrow">
                →
              </span>

            </Link>

          </div>

        </section>

        {/* =====================================
            SAVED CARDS + LAST 5 TRANSACTIONS
        ====================================== */}

        <section className="dashboard-lower-grid">

          {/* SAVED CARDS */}

          <div className="dashboard-panel">

            <div className="panel-heading">

              <div>

                <span>
                  PAYMENT METHODS
                </span>

                <h2>
                  Saved Cards
                </h2>

              </div>

              <Link to="/add-card">
                + Add Card
              </Link>

            </div>

            {cards.length === 0 ? (

              <div className="empty-state">

                <div className="empty-state-icon">
                  +
                </div>

                <h3>
                  No saved cards
                </h3>

                <p>
                  Add a card to start
                  making payments.
                </p>

                <Link to="/add-card">
                  Add your first card
                </Link>

              </div>

            ) : (

              <div className="bank-card-grid">

                {cards.slice(0, 2).map(
                  (card, index) => (

                    <div
                      key={card.id}
                      className={`bank-card bank-card-${index}`}
                    >

                      {/* CARD TOP */}

                      <div className="bank-card-top">

                        <span>
                          {card.card_type === "credit"
                            ? "CREDIT"
                            : "DEBIT"}
                        </span>

                        <small>
                          SAVED
                        </small>

                      </div>

                      {/* CARD BRAND */}

                      <div className="bank-card-brand">
                        CardPay
                      </div>

                      {/* CARD NUMBER */}

                      <div className="bank-card-number">
                        {card.masked_card_number}
                      </div>

                      {/* CARD BOTTOM */}

                      <div className="bank-card-bottom">

                        <div>

                          <span>
                            LAST FOUR
                          </span>

                          <strong>
                            {card.last_four_digits}
                          </strong>

                        </div>

                        <div className="card-chip">

                          <i></i>
                          <i></i>
                          <i></i>
                          <i></i>

                        </div>

                      </div>

                      {/* CREDIT LIMIT */}

                      {card.card_type === "credit" && (

                        <div className="card-credit-limit">

                          <span>
                            CREDIT LIMIT
                          </span>

                          <strong>
                            ₹
                            {Number(
                              card.credit_limit || 0
                            ).toLocaleString("en-IN")}
                          </strong>

                        </div>

                      )}

                    </div>

                  )
                )}

              </div>

            )}

          </div>

          {/* LAST 5 TRANSACTIONS */}

          <div className="dashboard-panel">

            <div className="panel-heading">

              <div>

                <span>
                  ACCOUNT ACTIVITY
                </span>

                <h2>
                  Last 5 Transactions
                </h2>

              </div>

              <Link to="/transactions">
                View All
              </Link>

            </div>

            {recentTransactions.length === 0 ? (

              <div className="empty-state">

                <div className="empty-state-icon">
                  ≡
                </div>

                <h3>
                  No transactions
                </h3>

                <p>
                  Recent payment activity
                  will appear here.
                </p>

              </div>

            ) : (

              <div className="transaction-list">

                {recentTransactions.map(
                  (transaction, index) => {

                    let statusClass = "pending";
                    let statusSymbol = "•";

                    if (
                      transaction.status === "SUCCESS"
                    ) {
                      statusClass = "success";
                      statusSymbol = "✓";
                    }

                    if (
                      transaction.status === "FAILED"
                    ) {
                      statusClass = "failed";
                      statusSymbol = "!";
                    }

                    return (
                      <div
                        className="transaction-row"
                        key={`${transaction.id || index}-${transaction.date}`}
                      >

                        <div className="transaction-left">

                          <div
                            className={`transaction-status ${statusClass}`}
                          >
                            {statusSymbol}
                          </div>

                          <div>

                            <strong>
                              ₹
                              {Number(
                                transaction.amount || 0
                              ).toLocaleString("en-IN", {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              })}
                            </strong>

                            <span>
                              {transaction.masked_card_number ||
                                "Card unavailable"}
                            </span>

                          </div>

                        </div>

                        <div className="transaction-right">

                          <strong
                            className={`transaction-status-text ${statusClass}`}
                          >
                            {transaction.status}
                          </strong>

                          <span>
                            {transaction.date
                              ? new Date(
                                  transaction.date
                                ).toLocaleDateString("en-IN")
                              : "N/A"}
                          </span>

                        </div>

                      </div>
                    );
                  }
                )}

              </div>

            )}

            {/* FAILED PAYMENT NOTICE */}

            {failedTransactions.length > 0 && (

              <div className="failed-notice">

                <div className="failed-notice-icon">
                  !
                </div>

                <div>

                  <strong>
                    Failed payment detected
                  </strong>

                  <span>
                    {failedTransactions.length} failed payment
                    {failedTransactions.length > 1
                      ? "s"
                      : ""}.
                  </span>

                </div>

              </div>

            )}

          </div>

        </section>

        {/* =====================================
            STATUS SUMMARY
        ====================================== */}

        <section className="dashboard-summary">

          <div className="summary-item">

            <span className="summary-dot green"></span>

            <span>
              Successful
            </span>

            <strong>
              {successfulTransactions.length}
            </strong>

          </div>

          <div className="summary-divider"></div>

          <div className="summary-item">

            <span className="summary-dot orange"></span>

            <span>
              Pending
            </span>

            <strong>
              {pendingTransactions.length}
            </strong>

          </div>

          <div className="summary-divider"></div>

          <div className="summary-item">

            <span className="summary-dot red"></span>

            <span>
              Failed
            </span>

            <strong>
              {failedTransactions.length}
            </strong>

          </div>

        </section>

      </main>

    </div>
  );
}

export default Dashboard;