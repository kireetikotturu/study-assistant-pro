import { useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function UpgradeSuccess() {
  const { refreshUser } = useAuth();

  useEffect(() => {
    // Give the Stripe webhook a moment to update the plan in the database
    const timer = setTimeout(() => refreshUser(), 1500);
    return () => clearTimeout(timer);
  }, [refreshUser]);

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>🎉 You're on Pro now</h1>
        <p>Your subscription is active. Unlimited questions and the Academic persona are unlocked.</p>
        <Link to="/chat">
          <button type="button">Go to Study Assistant</button>
        </Link>
      </div>
    </div>
  );
}
