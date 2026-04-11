import { Link } from "react-router-dom";

function PostCard({ post }) {
  return (
    <div className="post-card">
      <h2>{post.title}</h2>
      <p>{post.content.slice(0, 120)}...</p>
      <Link to={`/post/${post.slug}`} className="read-more">Read More</Link> jja
    </div>
  );
}

export default PostCard;

