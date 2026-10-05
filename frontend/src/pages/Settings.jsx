import { useNavigate } from "react-router";
import "./Settings.css";

function Settings() {
  const navigate = useNavigate();

  return (
    <div className="settings-page">

      <div className="settings-header">

        <span className="settings-overline">
          ACCOUNT
        </span>

        <h1>Settings</h1>

        <p>
          Manage your account preferences and
          security information.
        </p>

      </div>


      <div className="settings-grid">

        <div className="settings-card">

          <div className="settings-card-icon">
            ⚙
          </div>

          <div>
            <h2>
              Account Settings
            </h2>

            <p>
              Account preference management is
              currently limited to the available
              application features.
            </p>
          </div>

        </div>


        <div className="settings-card">

          <div className="settings-card-icon security">
            🔒
          </div>

          <div>
            <h2>
              Security
            </h2>

            <p>
              Your account uses JWT authentication
              and protected API routes.
            </p>
          </div>

        </div>


        <div className="settings-card settings-action">

          <div>
            <h2>
              Return to Dashboard
            </h2>

            <p>
              Go back to your payment overview.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate("/dashboard")}
          >
            Dashboard →
          </button>

        </div>

      </div>

    </div>
  );
}

export default Settings;