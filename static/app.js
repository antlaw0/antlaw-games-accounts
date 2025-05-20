const API_URL = "https://antlaw-games-accounts.onrender.com";

async function loginUser(email, password) {
  try {
    const res = await fetch(`${API_URL}/auth/login`, { // Note /auth path
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (res.ok) {
      localStorage.setItem("token", data.token);
      alert("Login successful!");
      window.location.href = "/"; // Redirect or load dashboard
    } else {
      alert(data.error || "Login failed.");
    }
  } catch (err) {
    console.error("Login error:", err);
    alert("An error occurred. Please try again later.");
  }
}
