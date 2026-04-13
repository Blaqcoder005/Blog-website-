import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function CreatePost() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const API_BASE = "http://localhost:8000";

  const handleSubmit = () => {
    if (!title.trim() || !content.trim()) {
      setError("Title and content are required");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("title", title);
    formData.append("content", content);
    if (image) formData.append("image", image);

    axios.post(`${API_BASE}/create`, formData, {
      withCredentials: true,
      headers: { "Content-Type": "multipart/form-data" }
    })
    .then(res => navigate(`/post/${res.data.slug}`))
    .catch(err => {
      if (err.response?.status === 401) navigate("/login");
      else setError("Failed to create post. Try again.");
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

        <label>Cover Image</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImage(e.target.files[0])}
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
