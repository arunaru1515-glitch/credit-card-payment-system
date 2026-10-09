import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import "./Transactions.css";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";

function Transactions() {
  const navigate = useNavigate();

  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filters state
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");
  const [cardSearch, setCardSearch] = useState("");
  const [sortBy, setSortBy] = useState("-transaction_date");

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 10;

  const [appliedFilters, setAppliedFilters] = useState({
    status: "",
    category: "",
    start_date: "",
    end_date: "",
    min_amount: "",
    max_amount: "",
    search: "",
    sort_by: "-transaction_date",
  });

  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }

    fetchTransactions(appliedFilters, currentPage);
  }, [accessToken, navigate, appliedFilters, currentPage]);

  const fetchTransactions = async (filters, page) => {
    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams();
      if (filters.status) params.append("status", filters.status);
      if (filters.category) params.append("category", filters.category);
      if (filters.start_date) params.append("start_date", filters.start_date);
      if (filters.end_date) params.append("end_date", filters.end_date);
      if (filters.min_amount) params.append("min_amount", filters.min_amount);
      if (filters.max_amount) params.append("max_amount", filters.max_amount);
      if (filters.search) params.append("search", filters.search);
      if (filters.sort_by) params.append("sort_by", filters.sort_by);

      params.append("page", page);
      params.append("page_size", pageSize);

      const url = `${DJANGO_BASE_URL}/api/transactions/?${params.toString()}`;

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (response.status === 401) {
        localStorage.clear();
        navigate("/login");
        return;
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || "Unable to load transactions.");
      }

      if (Array.isArray(data)) {
        setTransactions(data);
        setTotalCount(data.length);
        setTotalPages(1);
      } else {
        setTransactions(data.results || []);
        setTotalCount(data.count || 0);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      setError(err.message || "Unable to load transactions.");
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    setCurrentPage(1);
    setAppliedFilters({
      status,
      category,
      start_date: startDate,
      end_date: endDate,
      min_amount: minAmount,
      max_amount: maxAmount,
      search: cardSearch,
      sort_by: sortBy,
    });
  };

  const handleClear = () => {
    setStatus("");
    setCategory("");
    setStartDate("");
    setEndDate("");
    setMinAmount("");
    setMaxAmount("");
    setCardSearch("");
    setSortBy("-transaction_date");
    setCurrentPage(1);

    setAppliedFilters({
      status: "",
      category: "",
      start_date: "",
      end_date: "",
      min_amount: "",
      max_amount: "",
      search: "",
      sort_by: "-transaction_date",
    });
  };

  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams();
      if (appliedFilters.status) params.append("status", appliedFilters.status);
      if (appliedFilters.category) params.append("category", appliedFilters.category);
      if (appliedFilters.start_date) params.append("start_date", appliedFilters.start_date);
      if (appliedFilters.end_date) params.append("end_date", appliedFilters.end_date);
      if (appliedFilters.min_amount) params.append("min_amount", appliedFilters.min_amount);
      if (appliedFilters.max_amount) params.append("max_amount", appliedFilters.max_amount);
      if (appliedFilters.search) params.append("search", appliedFilters.search);

      const url = `${DJANGO_BASE_URL}/api/transactions/export/csv/?${params.toString()}`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      if (!res.ok) throw new Error("Export failed.");

      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = "transactions_export.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      setError(err.message || "Unable to export transactions.");
    }
  };

  const formatDate = (value) => {
    if (!value) return "-";
    return new Date(value).toLocaleString("en-IN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  const getCardDisplay = (transaction) => {
    if (transaction.card_masked_number) {
      return transaction.card_masked_number;
    }
    if (transaction.card && typeof transaction.card === "object") {
      return transaction.card.masked_card_number || `**** **** **** ${transaction.card.last_four_digits}`;
    }
    if (transaction.card) {
      return `Card #${transaction.card}`;
    }
    return "Card removed";
  };

  return (
    <div className="transactions-page">
      <main className="transactions-container">
        {/* HEADING */}
        <section className="transactions-heading">
          <div>
            <span className="heading-overline">ACCOUNT ACTIVITY & SEARCH</span>
            <h1>Transaction History</h1>
            <p>
              Advanced filtering with date range, amounts, categories, and masked card search.
            </p>
          </div>

          <button
            type="button"
            className="filter-button apply-btn export-csv-btn"
            onClick={handleExportCSV}
          >
            📥 Export to CSV
          </button>
        </section>

        {error && <div className="transactions-error">{error}</div>}

        {/* ADVANCED FILTERS */}
        <section className="filter-panel">
          <div className="filter-heading">
            <h2>Search & Filters</h2>
            <p>Narrow down payment records across multiple criteria.</p>
          </div>

          <div className="filter-grid">
            {/* STATUS */}
            <div className="filter-field">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="SUCCESS">Success</option>
                <option value="FAILED">Failed</option>
                <option value="PENDING">Pending</option>
              </select>
            </div>

            {/* CATEGORY */}
            <div className="filter-field">
              <label htmlFor="category">Category</label>
              <select
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                <option value="Groceries">Groceries</option>
                <option value="Shopping">Shopping</option>
                <option value="Dining">Dining</option>
                <option value="Utilities">Utilities</option>
                <option value="Travel">Travel</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Healthcare">Healthcare</option>
                <option value="General">General</option>
              </select>
            </div>

            {/* START DATE */}
            <div className="filter-field">
              <label htmlFor="startDate">Start Date</label>
              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            {/* END DATE */}
            <div className="filter-field">
              <label htmlFor="endDate">End Date</label>
              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            {/* MIN AMOUNT */}
            <div className="filter-field">
              <label htmlFor="minAmount">Min Amount (₹)</label>
              <input
                id="minAmount"
                type="number"
                min="0"
                value={minAmount}
                onChange={(e) => setMinAmount(e.target.value)}
                placeholder="0.00"
              />
            </div>

            {/* MAX AMOUNT */}
            <div className="filter-field">
              <label htmlFor="maxAmount">Max Amount (₹)</label>
              <input
                id="maxAmount"
                type="number"
                min="0"
                value={maxAmount}
                onChange={(e) => setMaxAmount(e.target.value)}
                placeholder="100000.00"
              />
            </div>

            {/* CARD SEARCH */}
            <div className="filter-field">
              <label htmlFor="cardSearch">Card Number / Last 4</label>
              <input
                id="cardSearch"
                type="text"
                value={cardSearch}
                onChange={(e) => setCardSearch(e.target.value)}
                placeholder="e.g. 1111 or ****"
              />
            </div>

            {/* SORTING */}
            <div className="filter-field">
              <label htmlFor="sortBy">Sort By</label>
              <select
                id="sortBy"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="-transaction_date">Date: Newest First</option>
                <option value="transaction_date">Date: Oldest First</option>
                <option value="-amount">Amount: Highest First</option>
                <option value="amount">Amount: Lowest First</option>
              </select>
            </div>
          </div>

          <div className="filter-actions">
            <button type="button" onClick={handleClear} className="filter-button clear-btn">
              Clear Filters
            </button>
            <button type="button" onClick={handleApply} className="filter-button apply-btn">
              Apply Filters
            </button>
          </div>
        </section>

        {/* RESULTS TABLE */}
        <section className="transactions-table-section">
          <div className="results-header">
            <h3>Found {totalCount} Transactions</h3>
            {totalPages > 1 && (
              <span>Page {currentPage} of {totalPages}</span>
            )}
          </div>

          {loading ? (
            <div className="transactions-loading-panel">Loading records...</div>
          ) : transactions.length === 0 ? (
            <div className="transactions-empty">
              <h3>No matching transactions found</h3>
              <p>Try broadening your filters.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="transactions-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Date & Time</th>
                    <th>Card Number</th>
                    <th>Category</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Fraud Status</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td>#{tx.id}</td>
                      <td>{formatDate(tx.transaction_date)}</td>
                      <td>{getCardDisplay(tx)}</td>
                      <td>
                        <span className="category-tag">{tx.category || "General"}</span>
                      </td>
                      <td>
                        <strong>
                          ₹{Number(tx.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        </strong>
                      </td>
                      <td>
                        <span className={`status-pill status-${tx.status.toLowerCase()}`}>
                          {tx.status}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`fraud-pill fraud-${(tx.fraud_status || "CLEAN").toLowerCase()}`}
                        >
                          {tx.fraud_status || "CLEAN"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* PAGINATION CONTROLS */}
          {totalPages > 1 && (
            <div className="pagination-bar">
              <button
                type="button"
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                className="pagination-btn"
              >
                ← Previous
              </button>

              <span className="pagination-info">
                Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
              </span>

              <button
                type="button"
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                className="pagination-btn"
              >
                Next →
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Transactions;