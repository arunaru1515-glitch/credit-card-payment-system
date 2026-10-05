import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";

import "./Dashboard.css";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";

function Dashboard() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [cards, setCards] = useState([]);
  const [transactions, setTransactions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const accessToken =
    localStorage.getItem("access_token");

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
        transactionsResponse,
      ] = await Promise.all([
        fetch(
          `${DJANGO_BASE_URL}/api/profile/`,
          { headers }
        ),

        fetch(
          `${DJANGO_BASE_URL}/api/cards/list/`,
          { headers }
        ),

        fetch(
          `${DJANGO_BASE_URL}/api/transactions/`,
          { headers }
        ),
      ]);

      if (
        profileResponse.status === 401 ||
        cardsResponse.status === 401 ||
        transactionsResponse.status === 401
      ) {
        localStorage.removeItem(
          "access_token"
        );

        localStorage.removeItem(
          "refresh_token"
        );

        localStorage.removeItem(
          "username"
        );

        navigate("/login");
        return;
      }

      const profileData =
        await profileResponse.json();

      const cardsData =
        await cardsResponse.json();

      const transactionsData =
        await transactionsResponse.json();

      if (!profileResponse.ok) {
        throw new Error(
          profileData.detail ||
            "Unable to load profile."
        );
      }

      if (!cardsResponse.ok) {
        throw new Error(
          "Unable to load saved cards."
        );
      }

      if (!transactionsResponse.ok) {
        throw new Error(
          "Unable to load transactions."
        );
      }

      setUsername(
        profileData.username || "User"
      );

      setCards(
        cardsData.cards || []
      );

      setTransactions(
        transactionsData || []
      );

      localStorage.setItem(
        "username",
        profileData.username || "User"
      );
    } catch (err) {
      setError(
        err.message ||
          "Unable to load dashboard."
      );
    } finally {
      setLoading(false);
    }
  };

  const successfulTransactions =
    transactions.filter(
      (transaction) =>
        transaction.status === "SUCCESS"
    );

  const failedTransactions =
    transactions.filter(
      (transaction) =>
        transaction.status === "FAILED"
    );

  const pendingTransactions =
    transactions.filter(
      (transaction) =>
        transaction.status === "PENDING"
    );

  const totalAmount =
    transactions.reduce(
      (total, transaction) =>
        total +
        Number(
          transaction.amount || 0
        ),
      0
    );

  const recentTransactions =
    transactions.slice(0, 4);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-loading-spinner"></div>

        <p>
          Loading dashboard...
        </p>
      </div>
    );
  }

  return (
    <div className="dashboard-page">

      {/* =========================================
          MAIN CONTENT
      ========================================== */}

      <main className="dashboard-container">

        {/* =========================================
            HERO
        ========================================== */}

        <section className="dashboard-hero">

          <div className="hero-content">

            <span className="hero-label">
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


        {/* =========================================
            ERROR
        ========================================== */}

        {error && (
          <div className="dashboard-error">
            {error}
          </div>
        )}


        {/* =========================================
            STATISTICS
        ========================================== */}

        <section className="dashboard-stats">

          <div className="stat-card blue">

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
              </svg>
            </div>

            <div className="stat-content">
              <span>
                Saved Cards
              </span>

              <strong>
                {cards.length}
              </strong>
            </div>

          </div>


          <div className="stat-card purple">

            <div className="stat-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <path d="M4 17l5-5 4 4 7-8" />
                <path d="M16 8h4v4" />
              </svg>
            </div>

            <div className="stat-content">
              <span>
                Total Transactions
              </span>

              <strong>
                {transactions.length}
              </strong>
            </div>

          </div>


          <div className="stat-card green">

            <div className="stat-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M5 12l4 4L19 6" />
              </svg>
            </div>

            <div className="stat-content">
              <span>
                Successful Payments
              </span>

              <strong>
                {successfulTransactions.length}
              </strong>
            </div>

          </div>


          <div className="stat-card orange">

            <div className="stat-icon rupee">
              ₹
            </div>

            <div className="stat-content">
              <span>
                Total Amount
              </span>

              <strong>
                ₹
                {totalAmount.toFixed(2)}
              </strong>
            </div>

          </div>

        </section>


        {/* =========================================
            QUICK ACTIONS
        ========================================== */}

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


        {/* =========================================
            LOWER GRID
        ========================================== */}

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

                      <div className="bank-card-top">

                        <span>
                          {card.card_type ===
                          "credit"
                            ? "CREDIT"
                            : "DEBIT"}
                        </span>

                        <small>
                          SAVED
                        </small>

                      </div>


                      <div className="bank-card-brand">
                        CardPay
                      </div>


                      <div className="bank-card-number">
                        {card.masked_card_number}
                      </div>


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

                    </div>

                  )
                )}

              </div>

            )}

          </div>


          {/* RECENT TRANSACTIONS */}

          <div className="dashboard-panel">

            <div className="panel-heading">

              <div>
                <span>
                  ACCOUNT ACTIVITY
                </span>

                <h2>
                  Recent Transactions
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
                  (transaction) => {

                    let statusClass =
                      "pending";

                    let statusSymbol =
                      "•";

                    if (
                      transaction.status ===
                      "SUCCESS"
                    ) {
                      statusClass =
                        "success";

                      statusSymbol =
                        "✓";
                    }

                    if (
                      transaction.status ===
                      "FAILED"
                    ) {
                      statusClass =
                        "failed";

                      statusSymbol =
                        "!";
                    }

                    return (
                      <div
                        className="transaction-row"
                        key={transaction.id}
                      >

                        <div className="transaction-left">

                          <div
                            className={`transaction-status ${statusClass}`}
                          >
                            {statusSymbol}
                          </div>

                          <div>
                            <strong>
                              Payment #
                              {transaction.id}
                            </strong>

                            <span>
                              {transaction.card
                                ? `Card #${transaction.card}`
                                : "Card removed"}
                            </span>
                          </div>

                        </div>


                        <div className="transaction-right">

                          <strong>
                            ₹
                            {Number(
                              transaction.amount || 0
                            ).toFixed(2)}
                          </strong>

                          <span>
                            {new Date(
                              transaction.transaction_date
                            ).toLocaleDateString()}
                          </span>

                        </div>

                      </div>
                    );
                  }
                )}

              </div>

            )}


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
                    {failedTransactions.length}{" "}
                    failed payment
                    {failedTransactions.length >
                    1
                      ? "s"
                      : ""}
                    .
                  </span>
                </div>

              </div>

            )}

          </div>

        </section>


        {/* =========================================
            STATUS SUMMARY
        ========================================== */}

        <section className="dashboard-summary">

          <div className="summary-item">
            <span className="summary-dot green"></span>
            <span>Successful</span>
            <strong>
              {successfulTransactions.length}
            </strong>
          </div>

          <div className="summary-divider"></div>

          <div className="summary-item">
            <span className="summary-dot orange"></span>
            <span>Pending</span>
            <strong>
              {pendingTransactions.length}
            </strong>
          </div>

          <div className="summary-divider"></div>

          <div className="summary-item">
            <span className="summary-dot red"></span>
            <span>Failed</span>
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