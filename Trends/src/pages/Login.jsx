import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles/global.css";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const API_BASE = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();
  const { checkAuth } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("email", email);
      formData.append("password", password);

      const res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (res.ok) {
        await checkAuth();
        console.log("API BASE:", import.meta.env.VITE_API_URL)
        console.log("Auth checked, navigating...");
        navigate("/");
        return;
      }

      if (res.status === 401) {
        setError("Invalid credentials");
      } else if (res.status === 429) {
        setError("Too many attempts. Try again later.");
      } else {
        const text = await res.text();
        setError(text || "Login failed");
      }
    } catch (err) {
      console.error(err);
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <form onSubmit={handleSubmit} className="auth-card">
        <h2>Login</h2>
        {error && <div className="error">{error}</div>}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? "Logging in…" : "Login"}
        </button>
        <p>Don't have an account? Sign up <Link to="/register">here</Link></p>
      </form>
    </div>
  );
}
