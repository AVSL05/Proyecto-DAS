const form = document.getElementById("forgotForm");
const msg = document.getElementById("msg");
const goLogin = document.getElementById("goLogin");

goLogin.addEventListener("click", () => window.location.href = "/login");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  msg.className = "msg";
  msg.textContent = "Enviando...";

  const data = Object.fromEntries(new FormData(form).entries());

  try {
    const res = await fetch("/api/auth/forgot-password", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(data)
    });

    const body = await res.json().catch(() => ({}));
    
    if (!res.ok) {
      msg.classList.add("err");
      // Manejar errores de validación
      if (Array.isArray(body.detail)) {
        const errores = body.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
        msg.textContent = errores;
      } else if (typeof body.detail === 'string') {
        msg.textContent = body.detail;
      } else {
        msg.textContent = "Error al enviar. Verifica el correo.";
      }
      return;
    }
    
    msg.classList.add("ok");
    msg.textContent = body.message || "Listo. Revisa tu correo (modo dev: mira consola).";
  } catch {
    msg.classList.add("err");
    msg.textContent = "No se pudo conectar al servidor.";
  }
});
