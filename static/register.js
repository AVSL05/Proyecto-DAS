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
      msg.textContent = body.detail || "Error al registrar.";
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
