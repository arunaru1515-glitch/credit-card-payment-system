import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import "./Transactions.css";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";

function Transactions() {
  const navigate = useNavigate();

  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [status, setStatus] = useState("");
  const [date, setDate] = useState("");
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");

  const [filters, setFilters] = useState({
    status: "",
    date: "",
    min_amount: "",
    max_amount: "",
  });

  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }

    fetchTransactions(filters);
  }, [accessToken, navigate, filters]);

  const fetchTransactions = async (currentFilters) => {
    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams();

      if (currentFilters.status) {
        params.append("status", currentFilters.status);
      }

      if (currentFilters.date) {
        params.append("date", currentFilters.date);
      }

      if (currentFilters.min_amount) {
        params.append(
          "min_amount",
          currentFilters.min_amount
        );
      }

      if (currentFilters.max_amount) {
        params.append(
          "max_amount",
          currentFilters.max_amount
        );
      }

      const query = params.toString();

      const url = query
        ? `${DJANGO_BASE_URL}/api/transactions/?${query}`
        : `${DJANGO_BASE_URL}/api/transactions/`;

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login");
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "Unable to load transactions."
        );
      }

      setTransactions(
        Array.isArray(data)
          ? data
          : data.results || []
      );
    } catch (err) {
      setError(
        err.message || "Unable to load transactions."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    setFilters({
      status,
      date,
      min_amount: minAmount,
      max_amount: maxAmount,
    });
  };

  const handleClear = () => {
    setStatus("");
    setDate("");
    setMinAmount("");
    setMaxAmount("");

    setFilters({
      status: "",
      date: "",
      min_amount: "",
      max_amount: "",
    });
  };

  const formatDate = (value) => {
    if (!value) {
      return "-";
    }

    const transactionDate = new Date(value);

    return transactionDate.toLocaleString("en-IN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  const getCardDisplay = (transaction) => {
    if (!transaction.card) {
      return "Card removed";
    }

    if (
      typeof transaction.card === "object" &&
      transaction.card.last_four_digits
    ) {
      return `**** **** **** ${transaction.card.last_four_digits}`;
    }

    return `Card #${transaction.card}`;
  };

  const getFailureReason = (transaction) => {
    if (transaction.failure_reason) {
      return transaction.failure_reason;
    }

    if (transaction.status === "FAILED") {
      return "Payment declined.";
    }

    return "-";
  };

  return (
    <div className="transactions-page">

      {/* ================= NAVBAR ================= */}

      <header className="transactions-navbar">
        <div className="transactions-navbar-inner">

          <div className="transactions-brand">
            <div className="brand-text">
              <span>SECURE PAYMENTS</span>
              <strong>Transaction History</strong>
            </div>
          </div>

          <Link
            to="/dashboard"
            className="transactions-back-button"
          >
            Back to Dashboard
          </Link>

        </div>
      </header>


      {/* ================= MAIN ================= */}

      <main className="transactions-container">

        {/* ================= PAGE HEADING ================= */}

        <section className="transactions-heading">

          <span className="heading-overline">
            ACCOUNT ACTIVITY
          </span>

          <h1>
            Transaction History
          </h1>

          <p>
            View and filter your payment transactions.
          </p>

        </section>


        {/* ================= ERROR ================= */}

        {error && (
          <div className="transactions-error">
            {error}
          </div>
        )}


        {/* ================= FILTERS ================= */}

        <section className="filter-panel">

          <div className="filter-heading">
            <h2>Filters</h2>

            <p>
              Filter transactions by status,
              date, or amount.
            </p>
          </div>


          <div className="filter-grid">

            {/* STATUS */}

            <div className="filter-field">

              <label htmlFor="status">
                Status
              </label>

              <select
                id="status"
                value={status}
                onChange={(event) =>
                  setStatus(event.target.value)
                }
              >
                <option value="">
                  All Statuses
                </option>

                <option value="SUCCESS">
                  Success
                </option>

                <option value="FAILED">
                  Failed
                </option>

                <option value="PENDING">
                  Pending
                </option>
              </select>

            </div>


            {/* DATE */}

            <div className="filter-field">

              <label htmlFor="date">
                Date
              </label>

              <input
                id="date"
                type="date"
                value={date}
                onChange={(event) =>
                  setDate(event.target.value)
                }
              />

            </div>


            {/* MINIMUM */}

            <div className="filter-field">

              <label htmlFor="minAmount">
                Minimum Amount
              </label>

              <div className="amount-input">

                <span>₹</span>

                <input
                  id="minAmount"
                  type="number"
                  min="0"
                  value={minAmount}
                  onChange={(event) =>
                    setMinAmount(event.target.value)
                  }
                  placeholder="0"
                />

              </div>

            </div>


            {/* MAXIMUM */}

            <div className="filter-field">

              <label htmlFor="maxAmount">
                Maximum Amount
              </label>

              <div className="amount-input">

                <span>₹</span>

                <input
                  id="maxAmount"
                  type="number"
                  min="0"
                  value={maxAmount}
                  onChange={(event) =>
                    setMaxAmount(event.target.value)
                  }
                  placeholder="100000"
                />

              </div>

            </div>


            {/* BUTTONS */}

            <div className="filter-buttons">

              <button
                type="button"
                onClick={handleApply}
                className="apply-button"
              >
                Apply
              </button>

              <button
                type="button"
                onClick={handleClear}
                className="clear-button"
              >
                Clear
              </button>

            </div>

          </div>

        </section>


        {/* ================= TRANSACTIONS ================= */}

        <section className="transaction-panel">

          <div className="transaction-panel-header">

            <div>
              <span className="section-overline">
                ACCOUNT ACTIVITY
              </span>

              <h2>
                Transactions
              </h2>

              <p>
                {transactions.length}{" "}
                {transactions.length === 1
                  ? "transaction"
                  : "transactions"}{" "}
                found
              </p>
            </div>

          </div>


          {/* LOADING */}

          {loading && (
            <div className="transactions-loading">

              <div className="loading-spinner"></div>

              <p>
                Loading transactions...
              </p>

            </div>
          )}


          {/* EMPTY */}

          {!loading &&
            transactions.length === 0 && (
              <div className="transactions-empty">

                <div className="empty-icon">
                  —
                </div>

                <h3>
                  No transactions found
                </h3>

                <p>
                  Try changing your filters.
                </p>

              </div>
            )}


          {/* TABLE */}

          {!loading &&
            transactions.length > 0 && (
              <div className="table-wrapper">

                <table className="transaction-table">

                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>CARD</th>
                      <th>AMOUNT</th>
                      <th>STATUS</th>
                      <th>DATE</th>
                      <th>FAILURE REASON</th>
                    </tr>
                  </thead>

                  <tbody>

                    {transactions.map(
                      (transaction) => (
                        <tr
                          key={transaction.id}
                        >

                          <td className="id-cell">
                            #{transaction.id}
                          </td>

                          <td className="card-cell">
                            {getCardDisplay(
                              transaction
                            )}
                          </td>

                          <td className="amount-cell">
                            ₹
                            {Number(
                              transaction.amount
                            ).toFixed(2)}
                          </td>

                          <td>
                            <span
                              className={`status-pill ${
                                transaction.status ===
                                "SUCCESS"
                                  ? "success"
                                  : transaction.status ===
                                    "FAILED"
                                  ? "failed"
                                  : "pending"
                              }`}
                            >
                              {transaction.status}
                            </span>
                          </td>

                          <td className="date-cell">
                            {formatDate(
                              transaction.transaction_date
                            )}
                          </td>

                          <td className="reason-cell">
                            {getFailureReason(
                              transaction
                            )}
                          </td>

                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>
            )}

        </section>

      </main>

    </div>
  );
}

export default Transactions;