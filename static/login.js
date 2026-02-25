const form = document.getElementById("loginForm");
const msg = document.getElementById("msg");
const goRegister = document.getElementById("goRegister");
const goForgot = document.getElementById("goForgot");
const googleLogin = document.getElementById("googleLogin");
const roleInput = document.getElementById("roleInput");
const roleButtons = document.querySelectorAll("[data-role-option]");

const ACCESS_CLIENT = "cliente";
const ACCESS_ADMIN = "administrativo";

function setRole(role) {
  roleInput.value = role;
  roleButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.roleOption === role);
  });
}

function redirectByRole(role) {
  window.location.href = role === ACCESS_ADMIN ? "/admin" : "/";
}

async function resolveRoleFromToken(token) {
  const response = await fetch("/api/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    return ACCESS_CLIENT;
  }

  const body = await response.json();
  return body.role || ACCESS_CLIENT;
}

function persistSession(token, tokenType, role) {
  localStorage.setItem("access_token", token);
  localStorage.setItem("token_type", tokenType || "bearer");
  localStorage.setItem("user_role", role || ACCESS_CLIENT);
}

roleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setRole(button.dataset.roleOption);
  });
});

setRole(roleInput.value || ACCESS_CLIENT);

const urlParams = new URLSearchParams(window.location.search);
const oauthToken = urlParams.get("token");
const provider = urlParams.get("provider");

if (oauthToken && provider === "google") {
  msg.className = "msg";
  msg.textContent = "Validando inicio de sesion con Google...";

  resolveRoleFromToken(oauthToken)
    .then((role) => {
      persistSession(oauthToken, "bearer", role);
      msg.classList.add("ok");
      msg.textContent = "Login exitoso. Redirigiendo...";
      window.history.replaceState({}, document.title, "/login");
      setTimeout(() => redirectByRole(role), 700);
    })
    .catch(() => {
      msg.classList.add("err");
      msg.textContent = "No se pudo validar el acceso de Google.";
    });
}

googleLogin.addEventListener("click", () => {
  if (roleInput.value === ACCESS_ADMIN) {
    msg.className = "msg err";
    msg.textContent = "El acceso administrativo no usa inicio con Google.";
    return;
  }
  window.location.href = "/api/auth/google/login";
});

goRegister.addEventListener("click", () => {
  window.location.href = "/register";
});

goForgot.addEventListener("click", () => {
  window.location.href = "/forgot-password";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  msg.className = "msg";
  msg.textContent = "Iniciando sesion...";

  const data = Object.fromEntries(new FormData(form).entries());

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
      msg.classList.add("err");
      msg.textContent = body.detail || "Credenciales invalidas.";
      return;
    }

    const userRole = body?.user?.role || ACCESS_CLIENT;
    persistSession(body.token, body.token_type, userRole);

    msg.classList.add("ok");
    msg.textContent = "Login correcto. Redirigiendo...";
    setTimeout(() => redirectByRole(userRole), 700);
  } catch (error) {
    msg.classList.add("err");
    msg.textContent = "No se pudo conectar al servidor.";
  }
});
