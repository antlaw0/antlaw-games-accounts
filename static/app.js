const API_URL = "https://your-render-server.onrender.com/auth";

async function loginUser(email, password) {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (res.ok) return data.token;
  else alert(data.error);
}
