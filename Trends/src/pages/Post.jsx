import { useEffect, useState } from "react";
import { FaRegComment } from "react-icons/fa";
import { useParams } from "react-router-dom";
import Comment from "../pages/Comment";
import axios from "axios";

function Post() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  const fetchComments = () => {
    axios.get(`${API_BASE}/comments/${slug}`)
      .then(res => {
        if (Array.isArray(res.data)) setComments(res.data);
        else setComments([]);
      })
      .catch(err => console.log(err));
  };

  useEffect(() => {
    axios.get(`${API_BASE}/posts/${slug}`)
      .then(res => setPost(res.data))
      .catch(err => console.log(err));

    fetchComments();
  }, [slug]);

  if (!post) return <p>Loading...</p>;
  if (post.error) return <p>{post.error}</p>;

  return (
    <div className="page post-page">
      <h1>{post.title}</h1>

      <div className="post-meta">
        <FaRegComment />
        <span>{comments.length} comments</span>
      </div>

      <div className="post-body">
        {post.content.split("\n").map((para, i) => (
          <p key={i}>{para}</p>
        ))}
      </div>

      <Comment slug={slug} onCommentAdded={fetchComments} />
    </div>
  );
}

export default Post;
