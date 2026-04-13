import { useEffect, useState } from "react";
import { FaRegComment } from "react-icons/fa";
import { useParams } from "react-router-dom";
import Comment from "../pages/Comment";
import axios from "axios";

function Post() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const API_BASE = "http://localhost:8000";

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

      <div className="post-body">
       <div className="post-meta">
        {post.content.split("\n").map((para, i) => (
          <p key={i}>{para}</p>
        ))}
       </div>
	{post.image_url && (
	  <img src={post.image_url} alt={post.title}
	    style={{ width: "100%", maxHeight: "400px", objectFit: "cover", borderRadius: "12px", marginBottom: "1.5rem" }}
	  />
	)}
      </div>
      <p>{Comment.slug}</p> 
      <Comment slug={slug} onCommentAdded={fetchComments} />
    </div>
  );
}

export default Post;
