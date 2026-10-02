import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../services/api";

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: "", email: "", password: "" });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isLogin) {
        // Limpiar sesión previa
        localStorage.removeItem("token");
        localStorage.removeItem("user_id");

        // Iniciar sesión y guardar token
        const data = await apiFetch("/users/login", {
          method: "POST",
          body: JSON.stringify({ email: formData.email, password: formData.password }),
        });
        
        localStorage.setItem("token", data.access_token);

        // Obtener y guardar el ID del usuario autenticado
        const me = await apiFetch("/users/me");
        localStorage.setItem("user_id", me.id);

        navigate("/");
      } else {
        await apiFetch("/users/register", {
          method: "POST",
          body: JSON.stringify({
            username: formData.username,
            email: formData.email,
            password: formData.password,
          }),
        });
        
        alert("Cuenta creada con éxito. Ahora inicia sesión.");
        setIsLogin(true);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "50px auto", padding: "20px", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h2>{isLogin ? "Iniciar Sesión" : "Registro"}</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {!isLogin && (
          <input
            type="text"
            placeholder="Nombre de usuario"
            required
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            style={{ padding: "8px" }}
          />
        )}
        <input
          type="email"
          placeholder="Correo electrónico"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          style={{ padding: "8px" }}
        />
        <input
          type="password"
          placeholder="Contraseña"
          required
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          style={{ padding: "8px" }}
        />
        <button type="submit" style={{ padding: "10px", cursor: "pointer" }}>
          {isLogin ? "Entrar" : "Crear Cuenta"}
        </button>
      </form>
      <button onClick={() => setIsLogin(!isLogin)} style={{ marginTop: "15px", background: "none", border: "none", color: "blue", cursor: "pointer" }}>
        {isLogin ? "¿No tienes cuenta? Regístrate aquí" : "¿Ya tienes cuenta? Inicia sesión"}
      </button>
    </div>
  );
}