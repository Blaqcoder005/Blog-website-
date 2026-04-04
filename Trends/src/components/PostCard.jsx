import { Link } from "react-router-dom";

function PostCard({ post }) {
  return (
    <div style={{
      border: "1px solid #ddd",
      padding: "15px",
      marginBottom: "10px",
      borderRadius: "8px"
    }}>
      <h2>{post.title}</h2>
      <p>{post.content.slice(0, 100)}...</p>

      <Link to={`/post/${post.slug}`}>
        Read More
      </Link>
    </div>
  );
}

export default PostCard;
