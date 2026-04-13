import { Link, Outlet } from "react-router-dom";

function Navbar() {
  return (
    <>
      <nav className="navbar">
        <span className="navbar-brand">MyBlog</span>
        <Link to="/">Home</Link>
        <Link to="/create">Create Post</Link>
      </nav>
      <Outlet />
    </>
  );
}

export default Navbar;
