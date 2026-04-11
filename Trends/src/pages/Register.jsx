import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/global.css";
import { useAuth } from "../context/AuthContext";


export default function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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

      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      console.log(formData)
      if (res.ok) {
        await checkAuth();          // sync frontend with backend
        navigate("/login");     // redirect to login-page
        return;
      }

      if (res.status === 401) {
        setError("Invalid credentials");
      } else if (res.status === 429) {
        setError("Too many attempts. Try again later.");
      } else {
        const text = await res.text();
        setError(text || "Registration failed");
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
        <h2>Register</h2>
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
          {loading ? "Submitting…" : "Register"}
        </button>
      </form>
    </div>
  );
}
