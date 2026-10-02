const API_URL = "http://184.73.37.223:8000";

export const getToken = () => localStorage.getItem("token");

export const apiFetch = async (endpoint, options = {}) => {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    let errorMessage = "Error en la petición";
    if (Array.isArray(errorData.detail)) {
      errorMessage = errorData.detail.map((err) => `${err.loc.join("->")}: ${err.msg}`).join("\n");
    } else if (typeof errorData.detail === "string") {
      errorMessage = errorData.detail;
    }

    throw new Error(errorMessage);
  }
  return response.json();
};