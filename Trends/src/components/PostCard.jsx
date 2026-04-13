import { Link } from "react-router-dom";

function PostCard({ post }) {
  return (
    <div className="post-card">
     {post.image_url && (
       <img src={post.image_url} alt={post.title}
         style={{ width: "100%", height: "180px", objectFit: "cover", borderRadius: "8px", marginBottom: "12px" }}
       />
     )}
      <h2>{post.title}</h2>
      <p>{post.content.slice(0, 120)}...</p>
      <Link to={`/post/${post.slug}`} className="read-more">Read More</Link>

    </div>
  );
}

export default PostCard;

