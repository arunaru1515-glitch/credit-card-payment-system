import { Link } from "react-router";
import "./AdminDashboard.css";

const DJANGO_ADMIN_URL = "http://127.0.0.1:8000/admin/";

function AdminDashboard() {
  const openAdmin = () => {
    window.open(DJANGO_ADMIN_URL, "_blank");
  };

  return (
    <div className="admin-page">

      {/* ==========================================
          PAGE INTRO
      =========================================== */}

      <section className="admin-intro">

        <div>
          <span className="admin-overline">
            SYSTEM ADMINISTRATION
          </span>

          <h1>
            Admin Dashboard
          </h1>

          <p>
            Manage users, saved cards, transactions,
            and daily payment operations from one place.
          </p>
        </div>

        <div className="admin-status">

          <span className="admin-status-dot"></span>

          <div>
            <strong>
              Administration Active
            </strong>

            <small>
              System management access
            </small>
          </div>

        </div>

      </section>


      {/* ==========================================
          ADMIN FEATURES
      =========================================== */}

      <section className="admin-feature-grid">

        {/* USERS */}

        <article className="admin-feature-card users-card">

          <div className="feature-card-top">

            <div className="feature-icon">
              U
            </div>

            <span className="feature-code">
              01
            </span>

          </div>

          <div className="feature-card-content">

            <h2>
              Manage Users
            </h2>

            <p>
              View and manage registered users
              through Django administration.
            </p>

          </div>

          <button
            type="button"
            onClick={openAdmin}
            className="feature-link"
          >
            Open Users
            <span>→</span>
          </button>

        </article>


        {/* CARDS */}

        <article className="admin-feature-card cards-card">

          <div className="feature-card-top">

            <div className="feature-icon">
              C
            </div>

            <span className="feature-code">
              02
            </span>

          </div>

          <div className="feature-card-content">

            <h2>
              View Cards
            </h2>

            <p>
              Review saved credit and debit cards
              with masked card information.
            </p>

          </div>

          <button
            type="button"
            onClick={openAdmin}
            className="feature-link"
          >
            Open Cards
            <span>→</span>
          </button>

        </article>


        {/* TRANSACTIONS */}

        <article className="admin-feature-card transactions-card">

          <div className="feature-card-top">

            <div className="feature-icon">
              T
            </div>

            <span className="feature-code">
              03
            </span>

          </div>

          <div className="feature-card-content">

            <h2>
              Transactions
            </h2>

            <p>
              Review payment activity and filter
              transactions by supported criteria.
            </p>

          </div>

          <button
            type="button"
            onClick={openAdmin}
            className="feature-link"
          >
            Open Transactions
            <span>→</span>
          </button>

        </article>


        {/* DAILY SUMMARY */}

        <article className="admin-feature-card summary-card">

          <div className="feature-card-top">

            <div className="feature-icon rupee-icon">
              ₹
            </div>

            <span className="feature-code">
              04
            </span>

          </div>

          <div className="feature-card-content">

            <h2>
              Daily Summary
            </h2>

            <p>
              Review today's payment totals,
              success, failure, and pending counts.
            </p>

          </div>

          <button
            type="button"
            onClick={openAdmin}
            className="feature-link"
          >
            Open Summary
            <span>→</span>
          </button>

        </article>

      </section>


      {/* ==========================================
          DJANGO ADMIN PANEL
      =========================================== */}

      <section className="django-panel">

        <div className="django-panel-content">

          <span className="django-overline">
            DJANGO ADMINISTRATION
          </span>

          <h2>
            System Management Panel
          </h2>

          <p>
            Use the Django administration panel to manage
            users, review saved cards, inspect transactions,
            export transaction data, and view the daily
            payment summary.
          </p>

          <button
            type="button"
            onClick={openAdmin}
            className="django-open-button"
          >
            Open Administration Panel
            <span>↗</span>
          </button>

        </div>

        <div className="django-panel-mark">
          DJANGO
        </div>

      </section>


      {/* ==========================================
          QUICK NAVIGATION
      =========================================== */}

      <section className="admin-navigation">

        <Link
          to="/dashboard"
          className="admin-navigation-card"
        >

          <div className="navigation-icon">
            D
          </div>

          <div>

            <span>
              USER AREA
            </span>

            <h3>
              User Dashboard
            </h3>

            <p>
              Return to the main payment dashboard.
            </p>

          </div>

          <strong>
            →
          </strong>

        </Link>


        <Link
          to="/transactions"
          className="admin-navigation-card"
        >

          <div className="navigation-icon">
            T
          </div>

          <div>

            <span>
              ACTIVITY
            </span>

            <h3>
              Transaction History
            </h3>

            <p>
              View the frontend transaction history.
            </p>

          </div>

          <strong>
            →
          </strong>

        </Link>


        <Link
          to="/make-payment"
          className="admin-navigation-card"
        >

          <div className="navigation-icon">
            ₹
          </div>

          <div>

            <span>
              PAYMENTS
            </span>

            <h3>
              Make Payment
            </h3>

            <p>
              Return to the payment processing page.
            </p>

          </div>

          <strong>
            →
          </strong>

        </Link>

      </section>

    </div>
  );
}

export default AdminDashboard;