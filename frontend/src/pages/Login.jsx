import { useState } from "react";
import { Link, useNavigate } from "react-router";
import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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

    if (!formData.username || !formData.password) {
      setError("Please enter your username and password.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/api/login/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const message =
          data?.non_field_errors?.[0] ||
          data?.detail ||
          "Invalid username or password.";

        throw new Error(message);
      }

      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);

      navigate("/dashboard");
    } catch (err) {
      setError(
        err.message || "Unable to login. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">

      {/* ================================================= */}
      {/* MAIN SHELL */}
      {/* ================================================= */}

      <div className="login-shell">

        {/* ================================================= */}
        {/* LEFT PANEL */}
        {/* ================================================= */}

        <div className="login-left">

          <div className="login-left-background"></div>
          <div className="login-left-glow-top"></div>
          <div className="login-left-glow-bottom"></div>

          <div className="login-left-content">

            {/* Brand */}
            <div className="login-brand">

              <div className="login-brand-icon">

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

                <p className="login-brand-label">
                  Secure Payments
                </p>

                <p className="login-brand-name">
                  CardPay
                </p>

              </div>

            </div>


            {/* Hero */}
            <div className="login-hero">

              <p className="login-eyebrow">
                Digital Payment Platform
              </p>

              <h1 className="login-title">
                Your payments.
                <span>
                  One secure place.
                </span>
              </h1>

              <p className="login-description">
                Manage saved cards, make secure payments,
                and keep track of your transactions from one
                centralized dashboard.
              </p>

            </div>


            {/* Payment Card */}
            <div className="login-card-area">

              <div className="login-payment-card">

                <div className="login-card-decoration-top"></div>
                <div className="login-card-decoration-bottom"></div>

                <div className="login-payment-card-content">

                  <div className="login-card-top">

                    <span className="login-card-label">
                      Premium Card
                    </span>

                    <div className="login-card-icon">

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
                          rx="2"
                        />
                      </svg>

                    </div>

                  </div>


                  <div className="login-card-number-row">

                    <div className="login-card-chip">

                      <span></span>
                      <span></span>
                      <span></span>
                      <span></span>

                    </div>

                    <p className="login-card-number">
                      **** **** **** 1111
                    </p>

                  </div>


                  <div className="login-card-bottom">

                    <div>

                      <p className="login-card-small-label">
                        Card Holder
                      </p>

                      <p className="login-card-small-value">
                        CARD USER
                      </p>

                    </div>


                    <div>

                      <p className="login-card-small-label">
                        Secure
                      </p>

                      <p className="login-card-small-value">
                        PAYMENT
                      </p>

                    </div>

                  </div>

                </div>

              </div>

            </div>


            {/* Trust Footer */}
            <div className="login-trust-footer">

              <div>
                <span className="trust-dot trust-green"></span>
                Secure Authentication
              </div>

              <div>
                <span className="trust-dot trust-blue"></span>
                Real-time Tracking
              </div>

            </div>

          </div>

        </div>


        {/* ================================================= */}
        {/* RIGHT PANEL */}
        {/* ================================================= */}

        <div className="login-right">

          {/* Decorative Shapes */}
          <div className="login-right-shape login-right-shape-one"></div>
          <div className="login-right-shape login-right-shape-two"></div>

          <div className="login-form-container">

            {/* Header */}
            <div className="login-form-header">

              <div className="welcome-badge">

                <span></span>
                Welcome back

              </div>

              <h2>
                Sign in
              </h2>

              <p>
                Access your secure payment dashboard and
                continue where you left off.
              </p>

            </div>


            {/* Error */}
            {error && (
              <div className="login-error">
                {error}
              </div>
            )}


            {/* Form */}
            <form
              className="login-form"
              onSubmit={handleSubmit}
            >

              {/* Username */}
              <div className="login-field">

                <label htmlFor="username">
                  Username
                </label>

                <div className="login-input-wrapper">

                  <svg
                    className="login-input-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <circle
                      cx="12"
                      cy="8"
                      r="3.5"
                    />

                    <path d="M5 20c.8-3.6 3.1-5.5 7-5.5s6.2 1.9 7 5.5" />
                  </svg>

                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Enter your username"
                    autoComplete="username"
                  />

                </div>

              </div>


              {/* Password */}
              <div className="login-field">

                <div className="password-label-row">

                  <label htmlFor="password">
                    Password
                  </label>

                  <span>
                    Protected
                  </span>

                </div>

                <div className="login-input-wrapper">

                  <svg
                    className="login-input-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  >
                    <rect
                      x="5"
                      y="10"
                      width="14"
                      height="10"
                      rx="2"
                    />

                    <path d="M8 10V7.5a4 4 0 018 0V10" />
                  </svg>

                  <input
                    id="password"
                    name="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                  />

                  <button
                    type="button"
                    className="show-password"
                    onClick={() =>
                      setShowPassword(
                        (previous) => !previous
                      )
                    }
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>

                </div>

              </div>


              {/* Login Button */}
              <button
                type="submit"
                className="login-button"
                disabled={loading}
              >

                {loading ? (
                  <>
                    <span className="login-spinner"></span>
                    Signing in...
                  </>
                ) : (
                  "Sign In →"
                )}

              </button>

            </form>


            {/* Security Box */}
            <div className="login-security-box">

              <div className="security-icon">

                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >
                  <path d="M12 3l7 3v5c0 4.5-2.8 8-7 10-4.2-2-7-5.5-7-10V6l7-3z" />
                  <path d="M9 12l2 2 4-4" />
                </svg>

              </div>

              <div>

                <p className="security-title">
                  Secure sign in
                </p>

                <p className="security-text">
                  Protected access with authenticated
                  login and encrypted password storage.
                </p>

              </div>

            </div>


            {/* Register */}
            <div className="login-register">

              <p>
                Don't have an account?

                <Link to="/register">
                  Create one
                </Link>
              </p>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Login;