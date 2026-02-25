const ACCESS_ADMIN = "administrativo";
const reservationStatuses = ["pending", "confirmed", "in_progress", "completed", "cancelled"];
const vehicleStatuses = ["available", "reserved", "in_use", "maintenance", "unavailable"];
const userRoles = ["cliente", "administrativo"];

const msg = document.getElementById("msg");
const adminName = document.getElementById("adminName");
const reservationsTable = document.getElementById("reservationsTable");
const vehiclesTable = document.getElementById("vehiclesTable");
const usersTable = document.getElementById("usersTable");

const usersTotal = document.getElementById("usersTotal");
const reservationsTotal = document.getElementById("reservationsTotal");
const reservationsPending = document.getElementById("reservationsPending");
const vehiclesActive = document.getElementById("vehiclesActive");

const logoutBtn = document.getElementById("logoutBtn");
const goClient = document.getElementById("goClient");
const refreshReservations = document.getElementById("refreshReservations");
const refreshVehicles = document.getElementById("refreshVehicles");
const refreshUsers = document.getElementById("refreshUsers");

let currentUser = null;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function showMessage(text, type = "ok") {
  msg.className = `message ${type}`;
  msg.textContent = text;

  setTimeout(() => {
    msg.className = "message";
    msg.textContent = "";
  }, 3000);
}

function clearSession() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_type");
  localStorage.removeItem("user_role");
}

function requireToken() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/login";
    throw new Error("No hay token");
  }
  return token;
}

async function apiRequest(path, options = {}) {
  const token = requireToken();
  const response = await fetch(path, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    clearSession();
    window.location.href = "/login";
    throw new Error("Sesion expirada");
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || "Error de servidor");
  }
  return body;
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("es-MX");
}

function renderStatusOptions(options, selected) {
  return options
    .map((option) => {
      const isSelected = option === selected ? "selected" : "";
      return `<option value="${option}" ${isSelected}>${option}</option>`;
    })
    .join("");
}

async function loadSummary() {
  const summary = await apiRequest("/api/admin/summary");
  usersTotal.textContent = summary.users.total;
  reservationsTotal.textContent = summary.reservations.total;
  reservationsPending.textContent = summary.reservations.pending;
  vehiclesActive.textContent = summary.vehicles.active;
}

async function loadReservations() {
  const data = await apiRequest("/api/admin/reservations");
  if (!data.reservations.length) {
    reservationsTable.innerHTML = '<tr><td colspan="7">No hay reservaciones</td></tr>';
    return;
  }

  reservationsTable.innerHTML = data.reservations
    .map((reservation) => {
      const range = `${formatDate(reservation.start_date)}<br>${formatDate(reservation.end_date)}`;
      return `
        <tr>
          <td>#${reservation.id}</td>
          <td>
            <strong>${escapeHtml(reservation.user_name || "Sin nombre")}</strong><br>
            <small>${escapeHtml(reservation.user_email || "-")}</small>
          </td>
          <td>${escapeHtml(reservation.vehicle_name || "Sin vehiculo")}</td>
          <td>${range}</td>
          <td>
            <span class="status-pill">${escapeHtml(reservation.status)}</span>
            <select data-reservation-status="${reservation.id}">
              ${renderStatusOptions(reservationStatuses, reservation.status)}
            </select>
          </td>
          <td>
            <input
              data-reservation-note="${reservation.id}"
              type="text"
              value="${escapeHtml(reservation.admin_notes || "")}"
              placeholder="Nota interna"
            />
          </td>
          <td>
            <button class="btn inline" data-save-reservation="${reservation.id}" type="button">
              Guardar
            </button>
          </td>
        </tr>
      `;
    })
    .join("");
}

async function loadVehicles() {
  const data = await apiRequest("/api/admin/vehicles");
  if (!data.vehicles.length) {
    vehiclesTable.innerHTML = '<tr><td colspan="7">No hay vehiculos</td></tr>';
    return;
  }

  vehiclesTable.innerHTML = data.vehicles
    .map((vehicle) => {
      return `
        <tr>
          <td>#${vehicle.id}</td>
          <td>${escapeHtml(vehicle.brand)} ${escapeHtml(vehicle.model)} ${vehicle.year}</td>
          <td>${escapeHtml(vehicle.plate)}</td>
          <td>
            <input data-vehicle-price-day="${vehicle.id}" type="number" min="0" step="0.01"
              value="${vehicle.price_per_day ?? 0}" />
          </td>
          <td>
            <select data-vehicle-status="${vehicle.id}">
              ${renderStatusOptions(vehicleStatuses, vehicle.status)}
            </select>
          </td>
          <td>
            <input data-vehicle-active="${vehicle.id}" type="checkbox" ${vehicle.is_active ? "checked" : ""} />
          </td>
          <td>
            <button class="btn inline" data-save-vehicle="${vehicle.id}" type="button">
              Guardar
            </button>
          </td>
        </tr>
      `;
    })
    .join("");
}

async function loadUsers() {
  const data = await apiRequest("/api/admin/users");
  if (!data.users.length) {
    usersTable.innerHTML = '<tr><td colspan="6">No hay usuarios</td></tr>';
    return;
  }

  usersTable.innerHTML = data.users
    .map((user) => {
      return `
        <tr>
          <td>#${user.id}</td>
          <td>${escapeHtml(user.full_name)}</td>
          <td>${escapeHtml(user.email)}</td>
          <td>${escapeHtml(user.phone || "-")}</td>
          <td>
            <select data-user-role="${user.id}">
              ${renderStatusOptions(userRoles, user.role)}
            </select>
          </td>
          <td>
            <button class="btn inline" data-save-user="${user.id}" type="button">
              Guardar rol
            </button>
          </td>
        </tr>
      `;
    })
    .join("");
}

async function saveReservation(reservationId) {
  const statusSelect = document.querySelector(`[data-reservation-status="${reservationId}"]`);
  const noteInput = document.querySelector(`[data-reservation-note="${reservationId}"]`);
  if (!statusSelect || !noteInput) return;

  await apiRequest(`/api/admin/reservations/${reservationId}`, {
    method: "PATCH",
    body: JSON.stringify({
      status: statusSelect.value,
      admin_notes: noteInput.value,
    }),
  });

  showMessage(`Reservacion #${reservationId} actualizada`);
  await loadSummary();
  await loadReservations();
}

async function saveVehicle(vehicleId) {
  const statusSelect = document.querySelector(`[data-vehicle-status="${vehicleId}"]`);
  const activeInput = document.querySelector(`[data-vehicle-active="${vehicleId}"]`);
  const priceDayInput = document.querySelector(`[data-vehicle-price-day="${vehicleId}"]`);
  if (!statusSelect || !activeInput || !priceDayInput) return;

  await apiRequest(`/api/admin/vehicles/${vehicleId}`, {
    method: "PATCH",
    body: JSON.stringify({
      status: statusSelect.value,
      is_active: activeInput.checked,
      price_per_day: Number(priceDayInput.value),
    }),
  });

  showMessage(`Vehiculo #${vehicleId} actualizado`);
  await loadSummary();
}

async function saveUserRole(userId) {
  const roleSelect = document.querySelector(`[data-user-role="${userId}"]`);
  if (!roleSelect) return;

  await apiRequest(`/api/admin/users/${userId}/role`, {
    method: "PATCH",
    body: JSON.stringify({ role: roleSelect.value }),
  });

  showMessage(`Rol de usuario #${userId} actualizado`);
  await loadSummary();
  await loadUsers();
}

reservationsTable.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-save-reservation]");
  if (!button) return;

  try {
    button.disabled = true;
    await saveReservation(button.dataset.saveReservation);
  } catch (error) {
    showMessage(error.message, "err");
  } finally {
    button.disabled = false;
  }
});

vehiclesTable.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-save-vehicle]");
  if (!button) return;

  try {
    button.disabled = true;
    await saveVehicle(button.dataset.saveVehicle);
  } catch (error) {
    showMessage(error.message, "err");
  } finally {
    button.disabled = false;
  }
});

usersTable.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-save-user]");
  if (!button) return;

  try {
    button.disabled = true;
    await saveUserRole(button.dataset.saveUser);
  } catch (error) {
    showMessage(error.message, "err");
  } finally {
    button.disabled = false;
  }
});

refreshReservations.addEventListener("click", async () => {
  try {
    await loadReservations();
  } catch (error) {
    showMessage(error.message, "err");
  }
});

refreshVehicles.addEventListener("click", async () => {
  try {
    await loadVehicles();
  } catch (error) {
    showMessage(error.message, "err");
  }
});

refreshUsers.addEventListener("click", async () => {
  try {
    await loadUsers();
  } catch (error) {
    showMessage(error.message, "err");
  }
});

goClient.addEventListener("click", () => {
  window.location.href = "/";
});

logoutBtn.addEventListener("click", () => {
  clearSession();
  window.location.href = "/login";
});

async function bootstrap() {
  try {
    currentUser = await apiRequest("/api/auth/me");
    if (currentUser.role !== ACCESS_ADMIN) {
      showMessage("Tu cuenta no es administrativa.", "err");
      setTimeout(() => {
        window.location.href = "/";
      }, 700);
      return;
    }

    adminName.textContent = `${currentUser.full_name} (${currentUser.email})`;

    await Promise.all([loadSummary(), loadReservations(), loadVehicles(), loadUsers()]);
  } catch (error) {
    showMessage(error.message, "err");
  }
}

bootstrap();
