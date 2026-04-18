import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles/global.css";
import { AuthProvider } from "./context/AuthContext";

const API_BASE = import.meta.env.VITE_API_URL;

// Ping backend on app load
fetch(`${API_BASE}/ping`, { credentials: "include" }).catch(() => {});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>  {/* Add this wrapper */}
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
