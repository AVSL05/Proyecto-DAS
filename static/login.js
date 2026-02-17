const form = document.getElementById("loginForm");
const msg = document.getElementById("msg");
const goRegister = document.getElementById("goRegister");
const goForgot = document.getElementById("goForgot");
const googleLogin = document.getElementById("googleLogin");

// Verificar si hay un token en la URL (desde Google OAuth)
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
const provider = urlParams.get('provider');

if (token && provider === 'google') {
  // Guardar el token
  localStorage.setItem("access_token", token);
  localStorage.setItem("token_type", "bearer");
  
  msg.className = "msg ok";
  msg.textContent = "✅ Login con Google exitoso. Redirigiendo...";
  
  // Limpiar la URL
  window.history.replaceState({}, document.title, "/login");
  
  // Redirigir al dashboard
  setTimeout(() => {
    window.location.href = "/";
  }, 700);
}

googleLogin.addEventListener("click", () => {
  // Redirigir al endpoint de Google OAuth
  window.location.href = "/api/auth/google/login";
});

goRegister.addEventListener("click", () => {
  window.location.href = "/register";
});

goForgot.addEventListener("click", () => {
  window.location.href = "/forgot-password";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  msg.className = "msg";
  msg.textContent = "Iniciando sesión...";

  const data = Object.fromEntries(new FormData(form).entries());

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });

    const body = await res.json().catch(() => ({}));

    if (!res.ok) {
      msg.classList.add("err");
      msg.textContent = body.detail || "Credenciales inválidas.";
      return;
    }

    // Guarda JWT
    localStorage.setItem("access_token", body.token);
    localStorage.setItem("token_type", body.token_type);

    msg.classList.add("ok");
    msg.textContent = "✅ Login OK. Redirigiendo...";

    // Aquí luego mandas a tu dashboard real
    setTimeout(() => {
      // Por ahora lo mandamos a /register o a una ruta que crees después
      window.location.href = "/register";
    }, 700);

  } catch {
    msg.classList.add("err");
    msg.textContent = "No se pudo conectar al servidor.";
  }
});
