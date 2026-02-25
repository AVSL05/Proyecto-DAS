const form = document.getElementById("registerForm");
const msg = document.getElementById("msg");
const goLogin = document.getElementById("goLogin");

goLogin.addEventListener("click", () => {
  window.location.href = "/login";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  msg.className = "msg";
  msg.textContent = "Registrando...";

  const data = Object.fromEntries(new FormData(form).entries());

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });

    const body = await res.json().catch(() => ({}));

    if (!res.ok) {
      msg.classList.add("err");
      // Manejar errores de validación (arrays de objetos)
      if (Array.isArray(body.detail)) {
        const errores = body.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
        msg.textContent = errores;
      } else if (typeof body.detail === 'string') {
        msg.textContent = body.detail;
      } else {
        msg.textContent = "Error al registrar. Verifica los datos.";
      }
      return;
    }

    msg.classList.add("ok");
    msg.textContent = "✅ Cuenta creada. Redirigiendo a iniciar sesión...";
    form.reset();

    setTimeout(() => {
      window.location.href = "/login";
    }, 800);

  } catch (err) {
    msg.classList.add("err");
    msg.textContent = "No se pudo conectar al servidor.";
  }
});
