import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";

export default function Profile() {
  const [userVideos, setUserVideos] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [videoFile, setVideoFile] = useState(null);
  const [thumbFile, setThumbFile] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiFetch("/users/me")
      .then((userData) => {
        setCurrentUser(userData);
        localStorage.setItem("user_id", userData.id);
        
        return apiFetch("/videos").then((videos) => {
          setUserVideos(videos.filter((v) => String(v.user_id) === String(userData.id)));
        });
      })
      .catch(console.error);
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!videoFile || !thumbFile) return alert("Selecciona video e imagen");
    if (!currentUser) return alert("No se ha detectado el usuario activo");

    setLoading(true);

    try {
      const videoData = await apiFetch("/videos", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          filename: videoFile.name,
          s3_key: `videos/${currentUser.id}/${videoFile.name}`,
          thumbnail_key: `thumbnails/${currentUser.id}/${thumbFile.name}`,
        }),
      });

      if (videoData.upload_video_url) {
        await fetch(videoData.upload_video_url, { method: "PUT", body: videoFile });
      }
      if (videoData.upload_thumb_url) {
        await fetch(videoData.upload_thumb_url, { method: "PUT", body: thumbFile });
      }

      alert("Video publicado con éxito");
      setTitle("");
      setDescription("");
      setVideoFile(null);
      setThumbFile(null);
      
      const updatedVideos = await apiFetch("/videos");
      setUserVideos(updatedVideos.filter((v) => String(v.user_id) === String(currentUser.id)));
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para eliminar el video
  const handleDelete = async (videoId) => {
    if (!window.confirm("¿Estás seguro de que deseas eliminar este video?")) return;

    try {
      await apiFetch(`/videos/${videoId}`, {
        method: "DELETE",
      });

      // Actualizar la lista local filtrando el video eliminado
      setUserVideos(userVideos.filter((v) => v.id !== videoId));
      alert("Video eliminado correctamente");
    } catch (err) {
      alert("Error al eliminar el video: " + err.message);
    }
  };

  return (
    <div style={{ padding: "20px", color: "#fff" }}>
      <h2>Perfil de {currentUser ? currentUser.username : "Cargando..."}</h2>
      <p><strong>Videos publicados:</strong> {userVideos.length}</p>

      <hr style={{ borderColor: "#333", margin: "20px 0" }} />
      
      <h3>Publicar Video</h3>
      <form onSubmit={handleUpload} style={{ display: "flex", flexDirection: "column", gap: "10px", maxWidth: "400px" }}>
        <input 
          type="text" 
          placeholder="Título" 
          required 
          value={title} 
          onChange={(e) => setTitle(e.target.value)} 
          style={{ padding: "8px", background: "#222", border: "1px solid #444", color: "#fff", borderRadius: "4px" }} 
        />
        <textarea 
          placeholder="Descripción" 
          required 
          value={description} 
          onChange={(e) => setDescription(e.target.value)} 
          style={{ padding: "8px", background: "#222", border: "1px solid #444", color: "#fff", borderRadius: "4px" }} 
        />
        <label>Video (.mp4):</label>
        <input type="file" accept="video/mp4" required onChange={(e) => setVideoFile(e.target.files[0])} />
        
        <label>Miniatura (.jpg, .png):</label>
        <input type="file" accept="image/*" required onChange={(e) => setThumbFile(e.target.files[0])} />
        
        <button type="submit" disabled={loading} style={{ padding: "10px", cursor: "pointer", background: "#007bff", color: "#fff", border: "none", borderRadius: "4px" }}>
          {loading ? "Subiendo..." : "Publicar"}
        </button>
      </form>

      <hr style={{ borderColor: "#333", margin: "20px 0" }} />
      
      <h3>Mis Videos</h3>
      {userVideos.length === 0 ? (
        <p style={{ color: "#aaa" }}>No tienes videos publicados aún.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, maxWidth: "600px" }}>
          {userVideos.map((v) => (
            <li key={v.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #333", padding: "12px 0" }}>
              <div>
                <strong>{v.title}</strong>
                <div style={{ fontSize: "0.85rem", color: "#aaa" }}>Vistas: {v.views || 0}</div>
              </div>
              <button 
                onClick={() => handleDelete(v.id)} 
                style={{ backgroundColor: "#dc3545", color: "#fff", border: "none", padding: "6px 12px", borderRadius: "4px", cursor: "pointer" }}
              >
                Eliminar
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}