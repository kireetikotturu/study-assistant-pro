import { Link } from "react-router-dom";

export default function UpgradeCancelled() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Upgrade cancelled</h1>
        <p>No charge was made. You can upgrade any time from the chat page.</p>
        <Link to="/chat">
          <button type="button">Back to Study Assistant</button>
        </Link>
      </div>
    </div>
  );
}
