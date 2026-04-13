import { useEffect, useState } from "react";
import axios from "axios";
import PostCard from "../components/PostCard";

function Home() {
  const [posts, setPosts] = useState([]);
  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    axios.get(`${API_BASE}/posts`)
      .then(res => setPosts(res.data))
      .catch(err => console.log(err));
  }, []);

  return (
    <div className="page">
      <div className="home-header">
        <h1>Latest Posts</h1>
        <p>Thoughts, ideas and stories.</p>
      </div>
      {posts.map(post => (
        <PostCard key={post.title} post={post} />
      ))}
    </div>
  );
}

export default Home;
