import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Post from "./pages/Post";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Comment from "./pages/Comment";
import CreatePost from "./pages/CreatePost";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Navbar />}>
         <Route path="/" element={<Home />} />
         <Route path="/create" element={<CreatePost />} />
         <Route path="/post/:slug" element={<Post />} />
        </Route>
      </Route>
    </Routes>
  );
}
export default App;
