import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function CreatePost() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  const handleSubmit = () => {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }

    setLoading(true);
    setError("");

    axios.post(`${API_BASE}/create`,
      { title, content },
      { withCredentials: true }
    )
    .then(res => {
      navigate(`/post/${res.data.slug}`);
    })
    .catch(err => {
      if (err.response?.status === 401) {
        navigate("/login");
      } else {
        setError("Failed to create post. Try again.");
        console.log(err);
      }
    })
    .finally(() => setLoading(false));
  };

  return (
    <div className="page create-post">
      <h2>Create Post</h2>

      {error && <div className="error">{error}</div>}

      <div className="form-group">
        <label>Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Post title..."
        />
      </div>

      <div className="form-group">
        <label>Content</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your post..."
          rows={10}
        />
      </div>

      <button onClick={handleSubmit} disabled={loading} className="btn btn-primary">
        {loading ? "Publishing..." : "Publish Post"}
      </button>
    </div>
  );
}

export default CreatePost;
