import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Auth from "./pages/Auth";
import Home from "./pages/Home";
import VideoPlayer from "./pages/VideoPlayer";
import Profile from "./pages/Profile";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: "20px", padding: "15px 20px", background: "#1a1a1a", color: "#fff", alignItems: "center" }}>
        <Link to="/" style={{ color: "#fff", textDecoration: "none", fontWeight: "bold" }}>MatyTube</Link>
        <Link to="/profile" style={{ color: "#fff", textDecoration: "none" }}>Mi Perfil</Link>
        <Link to="/auth" style={{ color: "#fff", textDecoration: "none", marginLeft: "auto" }}>Login / Registro</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/video/:id" element={<VideoPlayer />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </BrowserRouter>
  );
}