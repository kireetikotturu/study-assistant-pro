import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import { useAuth } from "../AuthContext";

export default function Chat() {
  const { user, logout, refreshUser } = useAuth();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [personaUsed, setPersonaUsed] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleAsk = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setAnswer("");
    try {
      const res = await api.post("/chat/ask", { question });
      setAnswer(res.data.answer);
      setPersonaUsed(res.data.persona_used);
      await refreshUser();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async () => {
    try {
      const res = await api.post("/subscription/create-checkout-session");
      window.location.href = res.data.checkout_url;
    } catch {
      setError("Could not start checkout. Try again.");
    }
  };

  if (!user) return null;

  return (
    <div className="chat-page">
      <header className="chat-header">
        <div>
          <h2>Study Assistant</h2>
          <span className={`plan-badge ${user.plan}`}>{user.plan.toUpperCase()}</span>
        </div>
        <div className="header-actions">
          {user.plan === "free" && (
            <button className="upgrade-btn" onClick={handleUpgrade}>
              Upgrade to Pro
            </button>
          )}
          <button
            className="logout-btn"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Log out
          </button>
        </div>
      </header>

      {user.plan === "free" && (
        <p className="limit-note">
          Free plan: {user.questions_asked_today}/5 questions used today. Upgrade to Pro for
          unlimited questions and in-depth academic answers.
        </p>
      )}

      <form className="ask-form" onSubmit={handleAsk}>
        <textarea
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={4}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {answer && (
        <div className="answer-card">
          <span className="persona-tag">{personaUsed} persona</span>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
