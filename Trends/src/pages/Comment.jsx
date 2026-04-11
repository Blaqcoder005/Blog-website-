import { useState, useEffect } from "react";
import axios from "axios";

function Comment({ slug, onCommentAdded }) {
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`http://localhost:8000/comments/${slug}`)
      .then(res => {
        if (Array.isArray(res.data)) {
          setComments(res.data);
        } else {
          setComments([]);
        }
      })
      .catch(err => console.log(err));
  }, [slug]);

  const handleSubmit = () => {
    if (!commentText.trim()) return;
    setLoading(true);

    axios.post("http://localhost:8000/comment", 
      new URLSearchParams({ slug, comment: commentText }),
      { withCredentials: true }
    )
   .then(res => {
     if (Array.isArray(res.data)) {
       setComments(res.data);
     } else {
       setComments([]);
     }
   })
    .then(res => setComments(res.data))
    .catch(err => console.log(err))
    .finally(() => setLoading(false));
  };

  return (
    <div className="comment-section">
      <h3>💬 ({comments.length})</h3>

	{comments.length > 0 ? (
	  comments.map((c, i) => (
	    <div key={i} className="comment-item">
	      <p>{c.comment}</p>
	    </div>
	  ))
	) : (
	  <p style={{ color: "#94a3b8" }}>No comments yet.</p>
	)}

      <h3>Add Comment</h3>
      <textarea
        className="comment-form"
        value={commentText}
        onChange={(e) => setCommentText(e.target.value)}
        placeholder="Write something..."
      />
      <br />
      <button onClick={handleSubmit} disabled={loading} className="comment-item">
        {loading ? "Submitting..." : "Submit"}
      </button>
    </div>
  );
}

export default Comment;
