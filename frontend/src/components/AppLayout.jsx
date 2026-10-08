import React, { useEffect, useState } from "react";

import {
  Link,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router";

import "./AppLayout.css";
import { useTheme } from "./ThemeContext.jsx";

const DJANGO_BASE_URL = "http://127.0.0.1:8000";

function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();

  const { theme, toggleTheme } = useTheme();

  const [username, setUsername] = useState("Arun");

  const isActive = (path) => {
    return location.pathname === path;
  };

  useEffect(() => {
    const loadUser = async () => {
      const accessToken =
        localStorage.getItem("access_token");

      if (!accessToken) {
        navigate("/login");
        return;
      }

      const savedUsername =
        localStorage.getItem("username");

      if (savedUsername) {
        setUsername(savedUsername);
      }

      try {
        const response = await fetch(
          `${DJANGO_BASE_URL}/api/profile/`,
          {
            headers: {
              Authorization:
                `Bearer ${accessToken}`,
            },
          }
        );

        if (response.status === 401) {
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

        if (response.ok) {
          const data =
            await response.json();

          if (data.username) {
            setUsername(data.username);

            localStorage.setItem(
              "username",
              data.username
            );
          }
        }
      } catch (error) {
        console.error(
          "Profile loading error:",
          error
        );
      }
    };

    loadUser();
  }, [navigate]);

  const handleLogout = async () => {
    const accessToken =
      localStorage.getItem("access_token");

    const refreshToken =
      localStorage.getItem("refresh_token");

    try {
      if (
        accessToken &&
        refreshToken
      ) {
        await fetch(
          `${DJANGO_BASE_URL}/api/logout/`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${accessToken}`,
            },

            body: JSON.stringify({
              refresh: refreshToken,
            }),
          }
        );
      }
    } catch (error) {
      console.error(
        "Logout error:",
        error
      );
    } finally {
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
    }
  };

  return (
    <div className="app-shell">

      {/* =================================================
          GLOBAL NAVBAR
      ================================================= */}

      <header className="main-navbar">

        {/* BRAND */}

        <Link
          to="/dashboard"
          className="main-brand"
        >

          <div className="main-brand-icon">
            CC
          </div>

          <div className="main-brand-text">

            <strong>
              CardPay
            </strong>

            <span>
              SECURE PAYMENTS
            </span>

          </div>

        </Link>


        {/* NAVIGATION */}

        <nav className="main-navigation">

          <Link
            to="/dashboard"
            className={`main-nav-link ${
              isActive("/dashboard")
                ? "active"
                : ""
            }`}
          >
            Dashboard
          </Link>


          <Link
            to="/add-card"
            className={`main-nav-link ${
              isActive("/add-card")
                ? "active"
                : ""
            }`}
          >
            My Cards
          </Link>


          <Link
            to="/make-payment"
            className={`main-nav-link ${
              isActive("/make-payment")
                ? "active"
                : ""
            }`}
          >
            Make Payment
          </Link>


          <Link
            to="/transactions"
            className={`main-nav-link ${
              isActive("/transactions")
                ? "active"
                : ""
            }`}
          >
            Transactions
          </Link>


          <Link
            to="/admin-dashboard"
            className={`main-nav-link ${
              isActive("/admin-dashboard")
                ? "active"
                : ""
            }`}
          >
            Admin
          </Link>

        </nav>


        {/* USER AREA */}

        <div className="navbar-user">

          {/* THEME TOGGLE */}

          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${
              theme === "light"
                ? "dark"
                : "light"
            } mode`}
            title={
              theme === "light"
                ? "Switch to dark mode"
                : "Switch to light mode"
            }
          >
            {theme === "light"
              ? "🌙"
              : "☀️"}
          </button>


          {/* USER AVATAR */}

          <div className="navbar-avatar">
            {username
              .charAt(0)
              .toUpperCase()}
          </div>


          {/* USER INFORMATION */}

          <div className="navbar-user-info">

            <strong>
              {username}
            </strong>

            <span>
              Customer
            </span>

          </div>


          {/* LOGOUT */}

          <button
            type="button"
            className="navbar-logout"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>


      {/* =================================================
          PAGE CONTENT
      ================================================= */}

      <main className="app-content">
        <Outlet />
      </main>


      {/* =================================================
          GLOBAL DEFAULT FOOTER
      ================================================= */}

      <footer className="site-footer">

        <div className="site-footer-left">

          <strong>
            CardPay
          </strong>

          <span>
            Credit Card Payment System
          </span>

        </div>


        <div className="site-footer-center">

          <span>
            Secure Payments
          </span>

        </div>


        <div className="site-footer-right">

          <span>
            © 2026 CardPay
          </span>

        </div>

      </footer>

    </div>
  );
}

export default AppLayout;