import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/global.css";

function CreatePost() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = () => {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }

    setLoading(true);
    setError("");

    axios.post("http://localhost:8000/create",
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

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ marginBottom: "16px" }}>
        <label>Title</label>
        <br />
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Post title..."
          style={{ width: "100%", padding: "8px", marginTop: "4px" }}
        />
      </div>

      <div style={{ marginBottom: "16px" }}>
        <label>Content</label>
        <br />
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your post..."
          rows={10}
          style={{ width: "100%", padding: "8px", marginTop: "4px" }}
        />
      </div>

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Publishing..." : "Publish Post"}
      </button>
    </div>
  );
}

export default CreatePost;
