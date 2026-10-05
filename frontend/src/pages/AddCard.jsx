import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import "./AddCard.css";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";

function AddCard() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    card_number: "",
    card_type: "credit",
  });

  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [cardsLoading, setCardsLoading] = useState(true);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

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
      setCardsLoading(true);
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

      setCards(data.cards || []);
    } catch (err) {
      setError(
        err.message ||
          "Unable to load saved cards."
      );
    } finally {
      setCardsLoading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;

    if (name === "card_number") {
      const cleanedValue = value.replace(/\D/g, "");

      if (cleanedValue.length > 19) {
        return;
      }

      setFormData((previous) => ({
        ...previous,
        card_number: cleanedValue,
      }));

      return;
    }

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    const cardNumber = formData.card_number.trim();

    if (!cardNumber) {
      setError(
        "Please enter your card number."
      );
      return;
    }

    if (
      cardNumber.length < 13 ||
      cardNumber.length > 19
    ) {
      setError(
        "Card number must contain 13 to 19 digits."
      );
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        `${DJANGO_BASE_URL}/api/cards/`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Authorization:
              `Bearer ${accessToken}`,
          },

          body: JSON.stringify({
            card_number: cardNumber,
            card_type: formData.card_type,
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
        throw new Error(
          data.error ||
            data.detail ||
            "Unable to add card."
        );
      }

      setMessage(
        data.message ||
          "Card added successfully."
      );

      setFormData({
        card_number: "",
        card_type: "credit",
      });

      await loadCards();
    } catch (err) {
      setError(
        err.message ||
          "Unable to add card."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (cardId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this saved card?"
    );

    if (!confirmed) {
      return;
    }

    setMessage("");
    setError("");

    try {
      const response = await fetch(
        `${DJANGO_BASE_URL}/api/cards/${cardId}/`,
        {
          method: "DELETE",

          headers: {
            Authorization:
              `Bearer ${accessToken}`,
          },
        }
      );

      const data =
        await response
          .json()
          .catch(() => ({}));

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login");
        return;
      }

      if (!response.ok) {
        throw new Error(
          data.error ||
            data.detail ||
            "Unable to delete card."
        );
      }

      setMessage(
        data.message ||
          "Card deleted successfully."
      );

      await loadCards();
    } catch (err) {
      setError(
        err.message ||
          "Unable to delete card."
      );
    }
  };

  return (
    <div className="add-card-page">

      {/* =================================================
          NAVBAR
          ================================================= */}

      <header className="add-card-navbar">

        <div className="add-card-navbar-inner">

          <div className="add-card-brand">

            <div className="add-card-brand-icon">
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
                Card Management
              </strong>
            </div>

          </div>


          <Link
            to="/dashboard"
            className="back-dashboard-button"
          >
            Back to Dashboard
          </Link>

        </div>

      </header>


      {/* =================================================
          MAIN
          ================================================= */}

      <main className="add-card-container">


        {/* PAGE HEADER */}

        <section className="add-card-intro">

          <div>

            <span className="add-card-overline">
              PAYMENT METHODS
            </span>

            <h1>
              Add Card
            </h1>

            <p>
              Add a credit or debit card
              for secure future payments.
            </p>

          </div>

        </section>


        {/* MESSAGES */}

        {message && (
          <div className="add-card-message success-message">
            <div className="message-icon">
              ✓
            </div>

            <div>
              <strong>
                Success
              </strong>

              <span>
                {message}
              </span>
            </div>
          </div>
        )}


        {error && (
          <div className="add-card-message error-message">
            <div className="message-icon">
              !
            </div>

            <div>
              <strong>
                Unable to continue
              </strong>

              <span>
                {error}
              </span>
            </div>
          </div>
        )}


        {/* =================================================
            CARD DETAILS
            ================================================= */}

        <section className="card-details-panel">

          <div className="card-details-heading">

            <div>

              <span className="panel-overline">
                SECURE CARD STORAGE
              </span>

              <h2>
                Card Details
              </h2>

              <p>
                Only masked card information will
                be retained by the system.
              </p>

            </div>

            <div className="security-badge">
              <span>●</span>
              Secure
            </div>

          </div>


          <form
            onSubmit={handleSubmit}
            className="add-card-form"
          >


            {/* CARD TYPE */}

            <div className="form-field">

              <label htmlFor="card_type">
                Card Type
              </label>

              <select
                id="card_type"
                name="card_type"
                value={formData.card_type}
                onChange={handleChange}
              >
                <option value="credit">
                  Credit Card
                </option>

                <option value="debit">
                  Debit Card
                </option>
              </select>

            </div>


            {/* CARD NUMBER */}

            <div className="form-field">

              <label htmlFor="card_number">
                Card Number
              </label>

              <div className="input-wrapper">

                <span className="input-card-icon">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.7"
                  >
                    <rect
                      x="3"
                      y="6"
                      width="18"
                      height="12"
                      rx="2"
                    />

                    <path d="M3 10h18" />
                  </svg>
                </span>

                <input
                  id="card_number"
                  name="card_number"
                  type="text"
                  inputMode="numeric"
                  autoComplete="cc-number"
                  value={formData.card_number}
                  onChange={handleChange}
                  placeholder="Enter card number"
                  maxLength={19}
                />

              </div>

              <p className="field-helper">
                Enter 13 to 19 digits.
                CVV is not required.
              </p>

            </div>


            {/* SUBMIT */}

            <div className="form-action">

              <button
                type="submit"
                disabled={loading}
                className="add-card-button"
              >

                {loading ? (
                  <>
                    <span className="button-spinner"></span>
                    Adding Card...
                  </>
                ) : (
                  <>
                    Add Card
                    <span>→</span>
                  </>
                )}

              </button>

            </div>

          </form>

        </section>


        {/* =================================================
            SAVED CARDS
            ================================================= */}

        <section className="saved-cards-section">

          <div className="saved-cards-heading">

            <div>

              <span className="section-overline">
                YOUR PAYMENT METHODS
              </span>

              <h2>
                Saved Cards
              </h2>

              <p>
                Your saved credit and debit cards.
              </p>

            </div>

            <span className="saved-count">
              {cards.length}{" "}
              {cards.length === 1
                ? "Card"
                : "Cards"}
            </span>

          </div>


          {/* LOADING */}

          {cardsLoading && (
            <div className="saved-cards-state">

              <div className="state-spinner"></div>

              <p>
                Loading saved cards...
              </p>

            </div>
          )}


          {/* EMPTY */}

          {!cardsLoading &&
            cards.length === 0 && (
              <div className="saved-cards-state">

                <div className="empty-card-icon">
                  +
                </div>

                <h3>
                  No saved cards
                </h3>

                <p>
                  Add your first card above
                  to make secure payments.
                </p>

              </div>
            )}


          {/* CARDS */}

          {!cardsLoading &&
            cards.length > 0 && (
              <div className="saved-card-grid">

                {cards.map(
                  (card, index) => (
                    <div
                      key={card.id}
                      className={`saved-bank-card saved-bank-card-${index % 3}`}
                    >

                      {/* decorative circle */}

                      <div className="bank-card-glow"></div>


                      <div className="saved-bank-card-content">

                        <div className="saved-bank-card-top">

                          <div>
                            <span>
                              {card.card_type === "credit"
                                ? "CREDIT CARD"
                                : "DEBIT CARD"}
                            </span>

                            <strong>
                              CardPay
                            </strong>
                          </div>


                          <button
                            type="button"
                            onClick={() =>
                              handleDelete(
                                card.id
                              )
                            }
                            className="delete-card-button"
                          >
                            Delete
                          </button>

                        </div>


                        <div className="saved-bank-card-number">

                          {card.masked_card_number}

                        </div>


                        <div className="saved-bank-card-bottom">

                          <div>

                            <span>
                              LAST FOUR DIGITS
                            </span>

                            <strong>
                              {card.last_four_digits}
                            </strong>

                          </div>


                          <div className="bank-chip">

                            <i></i>
                            <i></i>
                            <i></i>
                            <i></i>

                          </div>

                        </div>

                      </div>

                    </div>
                  )
                )}

              </div>
            )}

        </section>

      </main>

    </div>
  );
}

export default AddCard;