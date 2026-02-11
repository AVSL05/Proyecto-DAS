const form = document.getElementById("resetForm");
const msg = document.getElementById("msg");
const goLogin = document.getElementById("goLogin");

goLogin.addEventListener("click", () => window.location.href = "/login");

function getTokenFromURL() {
  const url = new URL(window.location.href);
  return url.searchParams.get("token");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  msg.className = "msg";
  msg.textContent = "Actualizando...";

  const token = getTokenFromURL();
  if (!token) {
    msg.classList.add("err");
    msg.textContent = "Falta el token en la URL.";
    return;
  }

  const data = Object.fromEntries(new FormData(form).entries());
  data.token = token;

  try {
    const res = await fetch("/api/auth/reset-password", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(data)
    });

    const body = await res.json().catch(() => ({}));

    if (!res.ok) {
      msg.classList.add("err");
      msg.textContent = body.detail || "No se pudo actualizar.";
      return;
    }

    msg.classList.add("ok");
    msg.textContent = body.message || "Contraseña actualizada. Ya puedes iniciar sesión.";
    form.reset();

    setTimeout(() => window.location.href = "/login", 900);
  } catch {
    msg.classList.add("err");
    msg.textContent = "No se pudo conectar al servidor.";
  }
});
