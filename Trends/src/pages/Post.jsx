import { useEffect, useState } from "react";
import { FaRegComment } from "react-icons/fa";
import { useParams } from "react-router-dom";
import Comment from "../pages/Comment";
import axios from "axios";

function Post() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);

  useEffect(() => {
    axios.get(`http://localhost:8000/posts/${slug}`)
      .then(res => setPost(res.data))
      .catch(err => console.log(err));

    axios.get(`http://localhost:8000/comments/${slug}`)
      .then(res => setComments(res.data))
      .catch(err => console.log(err));
  }, [slug]);

  if (!post) return <p>Loading...</p>;
  if (post.error) return <p>{post.error}</p>;

  return (
    <div className="page post-page">
      <h1>{post.title}</h1>
      <p>{post.content}</p>

      <Comment slug={slug} onCommentAdded={() => {
        axios.get(`http://localhost:8000/comments/${slug}`)
          .then(res => setComments(res.data))
      }} />
    </div>
  );
}

export default Post;
