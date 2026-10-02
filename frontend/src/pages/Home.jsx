import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../services/api";

export default function Home() {
  const [videos, setVideos] = useState([]);

  useEffect(() => {
    apiFetch("/videos")
      .then((data) => setVideos(data))
      .catch(console.error);
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h2>Catálogo de Videos</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "20px", marginTop: "20px" }}>
        {videos.map((video) => {
          const thumbnailUrl = video.thumbnail_url || `http://184.73.37.223:8000/videos/${video.id}/thumbnail`;

          return (
            <Link key={video.id} to={`/video/${video.id}`} style={{ textDecoration: "none", color: "inherit" }}>
              <div style={{ border: "1px solid #333", borderRadius: "8px", overflow: "hidden", background: "#1a1a1a" }}>
                <img
                  src={thumbnailUrl}
                  alt={video.title}
                  style={{ width: "100%", height: "150px", objectFit: "cover" }}
                  onError={(e) => { e.target.src = "https://via.placeholder.com/300x150?text=Sin+Miniatura"; }}
                />
                <div style={{ padding: "10px" }}>
                  <h3 style={{ margin: "0 0 5px 0", color: "#fff" }}>{video.title}</h3>
                  <p style={{ margin: "0", color: "#888", fontSize: "0.85rem" }}>
                    Por: {video.username || video.user_id}
                  </p>
                  <p style={{ margin: "5px 0 0 0", color: "#666", fontSize: "0.8rem" }}>
                    Vistas: {video.views || 0}
                  </p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}