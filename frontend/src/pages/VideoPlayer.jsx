import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiFetch } from "../services/api";

export default function VideoPlayer() {
  const { id } = useParams();
  const [video, setVideo] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");

  useEffect(() => {
    apiFetch(`/videos/${id}`)
      .then((data) => setVideo(data))
      .catch(console.error);

    apiFetch(`/videos/${id}/comments`)
      .then((data) => setComments(data))
      .catch(() => setComments([]));
  }, [id]);

  const handleComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await apiFetch(`/videos/${id}/comments`, {
        method: "POST",
        body: JSON.stringify({ content: newComment }),
      });
      setNewComment("");
      const updatedComments = await apiFetch(`/videos/${id}/comments`);
      setComments(updatedComments);
    } catch (err) {
      alert(err.message);
    }
  };

  if (!video) return <div style={{ padding: "20px", color: "#fff" }}>Cargando video...</div>;

  const streamUrl = video.video_url || `http://184.73.37.223:8000/videos/${id}/stream`;

  return (
    <div style={{ display: "flex", gap: "20px", padding: "20px", color: "#fff" }}>
      <div style={{ flex: 1 }}>
        <video controls style={{ width: "100%", maxHeight: "500px", backgroundColor: "#000" }} key={streamUrl}>
          <source src={streamUrl} type="video/mp4" />
          Tu navegador no soporta la reproducción de video.
        </video>

        <h1 style={{ marginTop: "15px" }}>{video.title}</h1>
        <p style={{ color: "#aaa" }}>{video.views || 0} vistas</p>
        <p style={{ fontWeight: "bold" }}>Publicado por: {video.username || "Usuario"}</p>
        <p>{video.description}</p>

        <hr style={{ borderColor: "#333", margin: "20px 0" }} />

        <h3>Comentarios</h3>
        <form onSubmit={handleComment} style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
          <input
            type="text"
            placeholder="Escribe un comentario..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            style={{ flex: 1, padding: "8px", borderRadius: "4px", border: "1px solid #444", background: "#222", color: "#fff" }}
          />
          <button type="submit" style={{ padding: "8px 16px", cursor: "pointer" }}>Comentar</button>
        </form>

        <div>
          {comments.map((c) => (
            <div key={c.id} style={{ borderBottom: "1px solid #222", padding: "8px 0" }}>
              <strong>{c.username || "Usuario"}:</strong> {c.content}
            </div>
          ))}
        </div>
      </div>

      <div style={{ width: "300px" }}>
        <h3>Recomendados</h3>
      </div>
    </div>
  );
}