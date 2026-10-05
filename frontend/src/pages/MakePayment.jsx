import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import "./MakePayment.css";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";
const FASTAPI_BASE_URL = "http://127.0.0.1:8001";

function MakePayment() {
  const navigate = useNavigate();

  const [cards, setCards] = useState([]);

  const [formData, setFormData] = useState({
    card_id: "",
    amount: "",
  });

  const [loadingCards, setLoadingCards] = useState(true);
  const [processing, setProcessing] = useState(false);

  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const accessToken = localStorage.getItem("access_token");

  useEffect(() => {
    if (!accessToken) {
      navigate("/login");
      return;
    }

    loadCards();
  }, [accessToken, navigate]);

  const loadCards = async () => {
    try {
      setLoadingCards(true);
      setError("");

      const response = await fetch(
        `${DJANGO_BASE_URL}/api/cards/list/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login");
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            data.detail ||
            "Unable to load saved cards."
        );
      }

      const savedCards = data.cards || [];

      setCards(savedCards);

      if (savedCards.length > 0) {
        setFormData((previous) => ({
          ...previous,
          card_id: String(savedCards[0].id),
        }));
      }
    } catch (err) {
      setError(
        err.message ||
          "Unable to load saved cards."
      );
    } finally {
      setLoadingCards(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setResult(null);

    const cardId = Number(formData.card_id);
    const amount = Number(formData.amount);

    if (!formData.card_id) {
      setError("Please select a saved card.");
      return;
    }

    if (!formData.amount || Number.isNaN(amount)) {
      setError("Please enter a valid payment amount.");
      return;
    }

    if (amount <= 0) {
      setError(
        "Payment amount must be greater than 0."
      );
      return;
    }

    try {
      setProcessing(true);

      const response = await fetch(
        `${FASTAPI_BASE_URL}/payments/`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },

          body: JSON.stringify({
            card_id: cardId,
            amount: amount,
          }),
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login");
        return;
      }

      if (!response.ok) {
        const errorMessage =
          data?.detail?.error ||
          data?.detail ||
          data?.error ||
          "Payment processing failed.";

        throw new Error(
          typeof errorMessage === "string"
            ? errorMessage
            : "Payment processing failed."
        );
      }

      setResult(data.payment);

      setFormData((previous) => ({
        ...previous,
        amount: "",
      }));
    } catch (err) {
      setError(
        err.message ||
          "Unable to process payment."
      );
    } finally {
      setProcessing(false);
    }
  };

  const selectedCard = cards.find(
    (card) =>
      String(card.id) ===
      String(formData.card_id)
  );

  const selectedLastFour =
    selectedCard?.last_four_digits || "";

  return (
    <div className="make-payment-page">

      {/* =================================================
          HEADER
          ================================================= */}

      <header className="payment-header">
        <div className="payment-header-inner">

          <div className="payment-header-brand">

            <div className="payment-header-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >
                <rect
                  x="3"
                  y="6"
                  width="18"
                  height="12"
                  rx="2.5"
                />

                <path d="M3 10h18" />

                <path d="M7 15h3" />
              </svg>
            </div>

            <div>
              <span>
                SECURE PAYMENTS
              </span>

              <strong>
                Make Payment
              </strong>
            </div>

          </div>

          <Link
            to="/dashboard"
            className="payment-back-button"
          >
            Back to Dashboard
          </Link>

        </div>
      </header>


      {/* =================================================
          MAIN
          ================================================= */}

      <main className="payment-container">

        {/* PAGE INTRO */}

        <section className="payment-intro">

          <span>
            SECURE PAYMENT PROCESSING
          </span>

          <h1>
            Make a Payment
          </h1>

          <p>
            Select a saved card and enter
            the amount you want to pay.
          </p>

        </section>


        {/* ERROR */}

        {error && (
          <div className="payment-error">

            <div className="payment-error-icon">
              !
            </div>

            <div>
              <strong>
                Payment Error
              </strong>

              <span>
                {error}
              </span>
            </div>

          </div>
        )}


        {/* =================================================
            PAYMENT AREA
            ================================================= */}

        <div className="payment-layout">

          {/* PAYMENT FORM */}

          <section className="payment-form-panel">

            <div className="payment-panel-heading">

              <div>
                <span>
                  PAYMENT DETAILS
                </span>

                <h2>
                  Secure Checkout
                </h2>

                <p>
                  Your payment starts as
                  PENDING and is then processed.
                </p>
              </div>

              <div className="payment-secure-badge">
                <span>●</span>
                Secure
              </div>

            </div>


            {loadingCards ? (

              <div className="payment-loading">

                <div className="payment-spinner"></div>

                <p>
                  Loading saved cards...
                </p>

              </div>

            ) : cards.length === 0 ? (

              <div className="no-cards-box">

                <div className="no-cards-icon">
                  +
                </div>

                <h3>
                  No saved cards
                </h3>

                <p>
                  You need to add a card
                  before making a payment.
                </p>

                <Link
                  to="/add-card"
                  className="add-card-link"
                >
                  Add a Card →
                </Link>

              </div>

            ) : (

              <form
                onSubmit={handleSubmit}
                className="payment-form"
              >

                {/* SELECT CARD */}

                <div className="payment-field">

                  <label htmlFor="card_id">
                    Select Card
                  </label>

                  <select
                    id="card_id"
                    name="card_id"
                    value={formData.card_id}
                    onChange={handleChange}
                  >
                    {cards.map((card) => (
                      <option
                        key={card.id}
                        value={card.id}
                      >
                        {card.card_type === "credit"
                          ? "Credit Card"
                          : "Debit Card"}{" "}
                        - ****{" "}
                        {card.last_four_digits}
                      </option>
                    ))}
                  </select>

                </div>


                {/* PAYMENT AMOUNT */}

                <div className="payment-field">

                  <label htmlFor="amount">
                    Payment Amount
                  </label>

                  <div className="amount-input-wrapper">

                    <span>
                      ₹
                    </span>

                    <input
                      id="amount"
                      name="amount"
                      type="number"
                      min="1"
                      step="0.01"
                      value={formData.amount}
                      onChange={handleChange}
                      placeholder="Enter payment amount"
                    />

                  </div>

                </div>


                {/* SUBMIT */}

                <button
                  type="submit"
                  disabled={processing}
                  className="make-payment-button"
                >
                  {processing ? (
                    <>
                      <span className="button-spinner"></span>
                      Processing Payment...
                    </>
                  ) : (
                    <>
                      Make Payment
                      <span>→</span>
                    </>
                  )}
                </button>

              </form>
            )}

          </section>


          {/* =================================================
              PAYMENT SUMMARY
              ================================================= */}

          <aside className="payment-summary-panel">

            <span className="summary-overline">
              PAYMENT SUMMARY
            </span>

            <h2>
              Secure Checkout
            </h2>


            <div className="summary-details">

              {/* CARD */}

              <div className="summary-row">

                <span>
                  Card
                </span>

                <strong>
                  {formData.card_id
                    ? `**** ${selectedLastFour}`
                    : "Not selected"}
                </strong>

              </div>


              {/* AMOUNT */}

              <div className="summary-row">

                <span>
                  Amount
                </span>

                <strong>
                  ₹
                  {formData.amount
                    ? Number(
                        formData.amount
                      ).toFixed(2)
                    : "0.00"}
                </strong>

              </div>


              {/* STATUS */}

              <div className="summary-status">

                <span>
                  STATUS
                </span>

                <p>
                  Payment will begin in{" "}
                  <strong>
                    PENDING
                  </strong>{" "}
                  status and then move to
                  its final result.
                </p>

              </div>

            </div>

          </aside>

        </div>


        {/* =================================================
            PAYMENT RESULT
            ================================================= */}

        {result && (
          <section className="payment-result-section">

            <div
              className={`payment-result-card ${
                result.final_status === "SUCCESS"
                  ? "result-success"
                  : "result-failed"
              }`}
            >

              <div className="payment-result-header">

                <div>

                  <span>
                    PAYMENT RESULT
                  </span>

                  <h2>
                    {result.final_status ===
                    "SUCCESS"
                      ? "Payment Successful"
                      : "Payment Failed"}
                  </h2>

                </div>

                <div className="result-status-badge">
                  {result.final_status}
                </div>

              </div>


              <div className="result-grid">

                {/* TRANSACTION ID */}

                <div className="result-item">

                  <span>
                    TRANSACTION ID
                  </span>

                  <strong>
                    #{result.transaction_id}
                  </strong>

                </div>


                {/* INITIAL STATUS */}

                <div className="result-item">

                  <span>
                    INITIAL STATUS
                  </span>

                  <strong>
                    {result.initial_status}
                  </strong>

                </div>


                {/* AMOUNT */}

                <div className="result-item">

                  <span>
                    AMOUNT
                  </span>

                  <strong>
                    ₹
                    {Number(
                      result.amount
                    ).toFixed(2)}
                  </strong>

                </div>


                {/* CARD */}

                <div className="result-item">

                  <span>
                    CARD
                  </span>

                  <strong>
                    ****{" "}
                    {
                      cards.find(
                        (card) =>
                          String(card.id) ===
                          String(
                            result.card_id
                          )
                      )?.last_four_digits
                    }
                  </strong>

                </div>

              </div>


              {/* FAILURE REASON */}

              {result.failure_reason && (
                <div className="failure-reason">

                  <strong>
                    FAILURE REASON
                  </strong>

                  <p>
                    {result.failure_reason}
                  </p>

                </div>
              )}


              {/* TRANSACTION LINK */}

              <div className="result-link-wrapper">

                <Link
                  to="/transactions"
                  className="transaction-history-link"
                >
                  View Transaction History →
                </Link>

              </div>

            </div>

          </section>
        )}

      </main>

    </div>
  );
}

export default MakePayment;