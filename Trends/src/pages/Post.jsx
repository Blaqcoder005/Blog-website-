import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

function Post() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/posts/${slug}`)
      .then(res => setPost(res.data))
      .catch(err => console.log(err));
  }, [slug]);

  if (!post) return <p>Loading...</p>;
  if (post.error) return <p>{post.error}</p>;
  return (
    <div style={{ padding: "20px" }}>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </div>
  );
}

export default Post;
