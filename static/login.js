const form = document.getElementById("loginForm");
const msg = document.getElementById("msg");
const goRegister = document.getElementById("goRegister");
const goForgot = document.getElementById("goForgot");

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
