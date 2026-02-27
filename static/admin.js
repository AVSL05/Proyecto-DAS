const ACCESS_ADMIN = "administrativo";
const reservationStatuses = ["pending", "confirmed", "in_progress", "completed", "cancelled"];
const vehicleStatuses = ["available", "reserved", "in_use", "maintenance", "unavailable"];
const userRoles = ["cliente", "administrativo"];
const vehicleStatusLabels = {
  available: "disponible",
  reserved: "reservado",
  maintenance: "mantenimiento",
  in_use: "en uso",
  unavailable: "no disponible",
};

const msg = document.getElementById("msg");
const adminName = document.getElementById("adminName");
const reservationsTable = document.getElementById("reservationsTable");
const vehiclesTable = document.getElementById("vehiclesTable");
const usersTable = document.getElementById("usersTable");
const salesTable = document.getElementById("salesTable");

const usersTotal = document.getElementById("usersTotal");
const reservationsTotal = document.getElementById("reservationsTotal");
const reservationsPending = document.getElementById("reservationsPending");
const vehiclesActive = document.getElementById("vehiclesActive");
const salesIncomeDay = document.getElementById("salesIncomeDay");
const salesIncomeMonth = document.getElementById("salesIncomeMonth");
const salesClosedReservations = document.getElementById("salesClosedReservations");
const salesCancelledReservations = document.getElementById("salesCancelledReservations");
const salesRefundPending = document.getElementById("salesRefundPending");
const salesAvgTicket = document.getElementById("salesAvgTicket");
const crmTotalCases = document.getElementById("crmTotalCases");
const crmOpenCases = document.getElementById("crmOpenCases");
const crmHighPriority = document.getElementById("crmHighPriority");
const crmRefundPending = document.getElementById("crmRefundPending");
const crmCasesTable = document.getElementById("crmCasesTable");
const crmDetailPanel = document.getElementById("crmDetailPanel");
const crmDetailHint = document.getElementById("crmDetailHint");
const crmDetailBody = document.getElementById("crmDetailBody");
const crmDetailCaseId = document.getElementById("crmDetailCaseId");
const crmDetailFolio = document.getElementById("crmDetailFolio");
const crmDetailClient = document.getElementById("crmDetailClient");
const crmDetailContact = document.getElementById("crmDetailContact");
const crmDetailType = document.getElementById("crmDetailType");
const crmDetailPriority = document.getElementById("crmDetailPriority");
const crmDetailStatus = document.getElementById("crmDetailStatus");
const crmDetailReservationStatus = document.getElementById("crmDetailReservationStatus");
const crmDetailRefundStatus = document.getElementById("crmDetailRefundStatus");
const crmDetailChannel = document.getElementById("crmDetailChannel");
const crmDetailAmount = document.getElementById("crmDetailAmount");
const crmDetailInvoice = document.getElementById("crmDetailInvoice");
const crmDetailLastUpdate = document.getElementById("crmDetailLastUpdate");
const crmDetailMessage = document.getElementById("crmDetailMessage");
const priorityPaymentAlerts = document.getElementById("priorityPaymentAlerts");

const logoutBtn = document.getElementById("logoutBtn");
const goClient = document.getElementById("goClient");
const refreshReservations = document.getElementById("refreshReservations");
const refreshVehicles = document.getElementById("refreshVehicles");
const refreshUsers = document.getElementById("refreshUsers");
const sidebarToggle = document.getElementById("sidebarToggle");
const adminSidebar = document.getElementById("adminSidebar");
const sidebarItems = document.querySelectorAll("[data-sidebar-view]");
const adminViews = document.querySelectorAll("[data-admin-view]");
const orgRoleCards = document.querySelectorAll("[data-org-role]");
const orgEmployeePanel = document.getElementById("orgEmployeePanel");
const orgDetailHint = document.getElementById("orgDetailHint");
const orgDetailBody = document.getElementById("orgDetailBody");
const orgEmployeeRole = document.getElementById("orgEmployeeRole");
const orgEmployeeArea = document.getElementById("orgEmployeeArea");
const orgEmployeeName = document.getElementById("orgEmployeeName");
const orgEmployeeId = document.getElementById("orgEmployeeId");
const orgEmployeeEmail = document.getElementById("orgEmployeeEmail");
const orgEmployeePhone = document.getElementById("orgEmployeePhone");
const orgEmployeeBranch = document.getElementById("orgEmployeeBranch");
const orgEmployeeShift = document.getElementById("orgEmployeeShift");
const orgEmployeeSeniority = document.getElementById("orgEmployeeSeniority");
const orgEmployeeStatus = document.getElementById("orgEmployeeStatus");
const orgEmployeeInitials = document.getElementById("orgEmployeeInitials");
const orgEmployeeNationality = document.getElementById("orgEmployeeNationality");
const orgEmployeeIssueDate = document.getElementById("orgEmployeeIssueDate");
const orgEmployeeHireDate = document.getElementById("orgEmployeeHireDate");
const orgEmployeeBirthDate = document.getElementById("orgEmployeeBirthDate");
const orgEmployeeBloodType = document.getElementById("orgEmployeeBloodType");
const orgEmployeeEmergencyContact = document.getElementById("orgEmployeeEmergencyContact");
const orgEmployeeCertifications = document.getElementById("orgEmployeeCertifications");
const orgEmployeeNotes = document.getElementById("orgEmployeeNotes");
const orgEmployeesMeta = document.getElementById("orgEmployeesMeta");
const orgEmployeesList = document.getElementById("orgEmployeesList");

const DEFAULT_ADMIN_VIEW = "configuracion";
let crmCasesCache = [];

function buildOrgTeam(role, area, employees) {
  return employees.map((employee) => ({
    role,
    area,
    status: "Activo",
    nationality: "Nacionalidad MX",
    ...employee,
  }));
}

const orgEmployeeProfiles = {
  direccion_general: buildOrgTeam("Direccion General", "Direccion Ejecutiva", [
    {
      name: "Patricia Salazar Navarro",
      employeeId: "EMP-0001",
      email: "patricia.salazar@cuidado-pug.com",
      phone: "81 2230 4401",
      branch: "Corporativo Monterrey",
      shift: "L-V 09:00 a 18:00",
      seniority: "8 anios",
      issueDate: "Emitido 2026-01-15",
      hireDate: "2018-03-12",
      birthDate: "1986-11-02",
      bloodType: "O+",
      emergencyContact: "Laura Salazar (Hermana) - 81 1122 9933",
      certifications: "Direccion estrategica, ISO 9001, Compliance",
      notes: "Aprueba presupuestos, auditorias trimestrales y prioridades de expansion.",
    },
  ]),
  gerencia_operaciones: buildOrgTeam("Gerencia de Operaciones", "Operaciones", [
    {
      name: "Javier Mendoza Rios",
      employeeId: "EMP-0042",
      email: "javier.mendoza@cuidado-pug.com",
      phone: "81 4410 2190",
      branch: "Sucursal Apodaca",
      shift: "L-S 08:00 a 17:00",
      seniority: "5 anios",
      issueDate: "Emitido 2025-10-08",
      hireDate: "2020-06-21",
      birthDate: "1990-02-14",
      bloodType: "A+",
      emergencyContact: "Sofia Mendoza (Esposa) - 81 4400 7788",
      certifications: "Lean Logistics, Gestion de riesgos, ISO 39001",
      notes: "Coordina patios, entregas y mantenimiento preventivo de unidades.",
    },
    {
      name: "Ana Sofia Trevino",
      employeeId: "EMP-0118",
      email: "ana.trevino@cuidado-pug.com",
      phone: "81 7701 2234",
      branch: "Patio Escobedo",
      shift: "L-S 07:00 a 16:00",
      seniority: "4 anios",
      issueDate: "Emitido 2025-06-19",
      hireDate: "2021-02-08",
      birthDate: "1992-09-01",
      bloodType: "B+",
      emergencyContact: "Manuel Trevino (Padre) - 81 5530 1144",
      certifications: "Control de inventario, KPI operativos",
      notes: "Responsable de programacion semanal de flota y ocupacion de patios.",
    },
    {
      name: "Carlos Ruiz Leal",
      employeeId: "EMP-0154",
      email: "carlos.ruiz@cuidado-pug.com",
      phone: "81 6640 1298",
      branch: "Monterrey Centro",
      shift: "L-V 10:00 a 19:00",
      seniority: "2 anios",
      issueDate: "Emitido 2025-08-23",
      hireDate: "2023-04-03",
      birthDate: "1995-12-11",
      bloodType: "O+",
      emergencyContact: "Laura Leal (Madre) - 81 2190 6622",
      certifications: "Planeacion de ruta, Excel avanzado",
      notes: "Gestiona reasignaciones de ultimo minuto y balance diario de disponibilidad.",
    },
  ]),
  gerencia_comercial: buildOrgTeam("Gerencia Comercial", "Comercial y Ventas", [
    {
      name: "Lucia R. Fernandez",
      employeeId: "EMP-0028",
      email: "lucia.fernandez@cuidado-pug.com",
      phone: "81 1980 5522",
      branch: "Monterrey Centro",
      shift: "L-V 09:00 a 19:00",
      seniority: "6 anios",
      issueDate: "Emitido 2025-12-01",
      hireDate: "2019-01-18",
      birthDate: "1988-07-27",
      bloodType: "B+",
      emergencyContact: "Hector Rocha (Conyuge) - 81 3002 6610",
      certifications: "Negociacion avanzada, CRM, Revenue management",
      notes: "Gestiona cuotas mensuales, alianzas comerciales y equipos de campo.",
    },
    {
      name: "Daniela Gomez Ibarra",
      employeeId: "EMP-0091",
      email: "daniela.gomez@cuidado-pug.com",
      phone: "81 5008 3321",
      branch: "San Pedro",
      shift: "L-V 09:00 a 18:00",
      seniority: "3 anios",
      issueDate: "Emitido 2025-07-10",
      hireDate: "2022-01-24",
      birthDate: "1993-10-05",
      bloodType: "A-",
      emergencyContact: "Rafael Gomez (Padre) - 81 9034 1188",
      certifications: "Prospeccion B2B, HubSpot",
      notes: "Encargada de cuentas empresariales y acuerdos corporativos.",
    },
    {
      name: "Marco A. Villarreal",
      employeeId: "EMP-0102",
      email: "marco.villarreal@cuidado-pug.com",
      phone: "81 7102 5533",
      branch: "Monterrey Centro",
      shift: "L-S 10:00 a 18:00",
      seniority: "2 anios",
      issueDate: "Emitido 2025-05-30",
      hireDate: "2023-02-13",
      birthDate: "1997-04-22",
      bloodType: "O-",
      emergencyContact: "Martha Villarreal (Madre) - 81 6610 4141",
      certifications: "Inside sales, cierre consultivo",
      notes: "Lidera conversion de leads digitales y seguimiento multicanal.",
    },
    {
      name: "Fernanda Paredes Luna",
      employeeId: "EMP-0127",
      email: "fernanda.paredes@cuidado-pug.com",
      phone: "81 6221 3309",
      branch: "Apodaca",
      shift: "L-V 08:30 a 17:30",
      seniority: "1 anio",
      issueDate: "Emitido 2025-09-14",
      hireDate: "2024-06-10",
      birthDate: "1998-06-16",
      bloodType: "AB+",
      emergencyContact: "Jorge Paredes (Hermano) - 81 1299 8700",
      certifications: "Atencion comercial, cotizacion rapida",
      notes: "Gestiona cartera de renovaciones y seguimiento postventa.",
    },
  ]),
  atencion_cliente: buildOrgTeam("Atencion al Cliente", "Experiencia del cliente", [
    {
      name: "Eduardo Castillo Vega",
      employeeId: "EMP-0076",
      email: "eduardo.castillo@cuidado-pug.com",
      phone: "81 3021 7789",
      branch: "San Nicolas",
      shift: "L-D 12:00 a 20:00",
      seniority: "3 anios",
      issueDate: "Emitido 2025-11-20",
      hireDate: "2022-08-03",
      birthDate: "1994-05-09",
      bloodType: "AB+",
      emergencyContact: "Rosa Vega (Madre) - 81 2219 4021",
      certifications: "Servicio al cliente, Resolucion de conflictos, NPS",
      notes: "Responsable de escalaciones VIP, reclamos criticos y seguimiento post-servicio.",
    },
    {
      name: "Karen Juarez Molina",
      employeeId: "EMP-0131",
      email: "karen.juarez@cuidado-pug.com",
      phone: "81 8120 1141",
      branch: "Monterrey Centro",
      shift: "L-V 09:00 a 17:00",
      seniority: "2 anios",
      issueDate: "Emitido 2025-05-22",
      hireDate: "2023-01-30",
      birthDate: "1996-08-29",
      bloodType: "B+",
      emergencyContact: "Ricardo Juarez (Padre) - 81 4550 6644",
      certifications: "Atencion telefonica, CSAT",
      notes: "Monitorea calidad de llamadas y gestiona encuestas de salida.",
    },
    {
      name: "Jose Manuel Ayala",
      employeeId: "EMP-0132",
      email: "jose.ayala@cuidado-pug.com",
      phone: "81 8120 1142",
      branch: "Monterrey Centro",
      shift: "L-V 11:00 a 19:00",
      seniority: "2 anios",
      issueDate: "Emitido 2025-05-22",
      hireDate: "2023-01-30",
      birthDate: "1995-11-11",
      bloodType: "O+",
      emergencyContact: "Elena Ayala (Madre) - 81 4020 9911",
      certifications: "Chat support, QA de conversaciones",
      notes: "Especialista en seguimiento de casos web y app.",
    },
    {
      name: "Monica Lopez Torres",
      employeeId: "EMP-0133",
      email: "monica.lopez@cuidado-pug.com",
      phone: "81 8120 1143",
      branch: "San Nicolas",
      shift: "L-S 08:00 a 16:00",
      seniority: "4 anios",
      issueDate: "Emitido 2025-02-18",
      hireDate: "2021-04-05",
      birthDate: "1991-07-03",
      bloodType: "A+",
      emergencyContact: "David Torres (Conyuge) - 81 4770 2300",
      certifications: "Manejo de quejas, SLA",
      notes: "Coordina tiempos de respuesta y derivaciones a operaciones.",
    },
    {
      name: "Pedro Infante Aguilar",
      employeeId: "EMP-0134",
      email: "pedro.infante@cuidado-pug.com",
      phone: "81 8120 1144",
      branch: "Apodaca",
      shift: "L-S 12:00 a 20:00",
      seniority: "1 anio",
      issueDate: "Emitido 2025-09-02",
      hireDate: "2024-04-15",
      birthDate: "1999-01-27",
      bloodType: "O-",
      emergencyContact: "Tania Aguilar (Hermana) - 81 6211 4455",
      certifications: "Retencion de clientes",
      notes: "Atiende incidencias de facturacion y reembolsos.",
    },
    {
      name: "Rebeca Solis Garza",
      employeeId: "EMP-0135",
      email: "rebeca.solis@cuidado-pug.com",
      phone: "81 8120 1145",
      branch: "San Pedro",
      shift: "L-V 10:00 a 18:00",
      seniority: "2 anios",
      issueDate: "Emitido 2025-03-14",
      hireDate: "2022-10-03",
      birthDate: "1994-03-19",
      bloodType: "AB-",
      emergencyContact: "Luis Solis (Padre) - 81 7622 5588",
      certifications: "Experiencia cliente, NPS",
      notes: "Administra casos de clientes recurrentes y preventas.",
    },
    {
      name: "Armando De la Cruz",
      employeeId: "EMP-0136",
      email: "armando.cruz@cuidado-pug.com",
      phone: "81 8120 1146",
      branch: "Escobedo",
      shift: "L-D 14:00 a 22:00",
      seniority: "3 anios",
      issueDate: "Emitido 2025-01-07",
      hireDate: "2021-11-09",
      birthDate: "1990-12-30",
      bloodType: "B-",
      emergencyContact: "Rocio De la Cruz (Esposa) - 81 8871 2200",
      certifications: "Atencion omnicanal",
      notes: "Cubre turno nocturno y coordinacion con monitoreo.",
    },
    {
      name: "Valeria Cantu Rojas",
      employeeId: "EMP-0137",
      email: "valeria.cantu@cuidado-pug.com",
      phone: "81 8120 1147",
      branch: "Monterrey Centro",
      shift: "L-V 08:00 a 16:00",
      seniority: "1 anio",
      issueDate: "Emitido 2025-10-11",
      hireDate: "2024-07-22",
      birthDate: "2000-02-12",
      bloodType: "A+",
      emergencyContact: "Elisa Rojas (Madre) - 81 9920 7301",
      certifications: "Protocolos de atencion inicial",
      notes: "Primer contacto y clasificacion de tickets entrantes.",
    },
  ]),
  logistica_flota: buildOrgTeam("Logistica y Flota", "Flota y mantenimiento", [
    {
      name: "Marina Ponce Trevino",
      employeeId: "EMP-0035",
      email: "marina.ponce@cuidado-pug.com",
      phone: "81 3774 1034",
      branch: "Patio Logistico Escobedo",
      shift: "L-S 07:00 a 16:00",
      seniority: "7 anios",
      issueDate: "Emitido 2025-09-05",
      hireDate: "2017-10-02",
      birthDate: "1987-03-30",
      bloodType: "O-",
      emergencyContact: "Daniel Ponce (Hermano) - 81 1933 2244",
      certifications: "Mantenimiento de flotas, Seguridad operativa, KPI de taller",
      notes: "Supervisa inspecciones, disponibilidad diaria y coordinacion de talleres externos.",
    },
    {
      name: "Hector Zamora Salinas",
      employeeId: "EMP-0201",
      email: "hector.zamora@cuidado-pug.com",
      phone: "81 6601 2201",
      branch: "Patio Escobedo",
      shift: "L-S 06:00 a 15:00",
      seniority: "5 anios",
      issueDate: "Emitido 2025-03-10",
      hireDate: "2020-01-06",
      birthDate: "1989-06-13",
      bloodType: "A+",
      emergencyContact: "Lilia Salinas (Esposa) - 81 3309 1100",
      certifications: "Diagnostico de unidades, control de taller",
      notes: "Encargado de recepcion de unidades para revision preventiva.",
    },
    {
      name: "Brenda Ortiz Gil",
      employeeId: "EMP-0202",
      email: "brenda.ortiz@cuidado-pug.com",
      phone: "81 6601 2202",
      branch: "Patio Escobedo",
      shift: "L-V 08:00 a 17:00",
      seniority: "3 anios",
      issueDate: "Emitido 2025-02-14",
      hireDate: "2022-03-01",
      birthDate: "1992-04-25",
      bloodType: "B+",
      emergencyContact: "Nora Gil (Madre) - 81 4422 1188",
      certifications: "Planeacion de mantenimiento",
      notes: "Programa mantenimientos por kilometraje y antiguedad.",
    },
    {
      name: "Ricardo Mena Flores",
      employeeId: "EMP-0203",
      email: "ricardo.mena@cuidado-pug.com",
      phone: "81 6601 2203",
      branch: "Apodaca",
      shift: "L-S 09:00 a 18:00",
      seniority: "4 anios",
      issueDate: "Emitido 2025-07-06",
      hireDate: "2021-01-18",
      birthDate: "1991-01-08",
      bloodType: "O+",
      emergencyContact: "Mayra Flores (Conyuge) - 81 1114 2200",
      certifications: "Inventario de refacciones",
      notes: "Controla stock de refacciones y solicitud de compras.",
    },
    {
      name: "Selene Villar Chavez",
      employeeId: "EMP-0204",
      email: "selene.villar@cuidado-pug.com",
      phone: "81 6601 2204",
      branch: "Monterrey Centro",
      shift: "L-V 10:00 a 19:00",
      seniority: "2 anios",
      issueDate: "Emitido 2025-04-28",
      hireDate: "2023-02-27",
      birthDate: "1997-09-14",
      bloodType: "AB+",
      emergencyContact: "Oscar Chavez (Padre) - 81 5521 0066",
      certifications: "Telemetria de flota",
      notes: "Monitorea alertas de GPS y uso de unidad en ruta.",
    },
    {
      name: "Mauricio Rangel Soto",
      employeeId: "EMP-0205",
      email: "mauricio.rangel@cuidado-pug.com",
      phone: "81 6601 2205",
      branch: "San Nicolas",
      shift: "L-S 07:00 a 16:00",
      seniority: "6 anios",
      issueDate: "Emitido 2025-01-19",
      hireDate: "2019-05-20",
      birthDate: "1988-10-17",
      bloodType: "A-",
      emergencyContact: "Silvia Soto (Hermana) - 81 9980 2233",
      certifications: "Seguridad operativa",
      notes: "Valida checklists de salida y retorno de unidad.",
    },
    {
      name: "Paola Garza Elizondo",
      employeeId: "EMP-0206",
      email: "paola.garza@cuidado-pug.com",
      phone: "81 6601 2206",
      branch: "Patio Escobedo",
      shift: "L-V 08:30 a 17:30",
      seniority: "1 anio",
      issueDate: "Emitido 2025-11-04",
      hireDate: "2024-05-13",
      birthDate: "1999-12-01",
      bloodType: "O+",
      emergencyContact: "Hector Elizondo (Padre) - 81 4180 3355",
      certifications: "Procesos de entrega-recepcion",
      notes: "Coordina documentacion de entrega y devolucion de autos.",
    },
    {
      name: "Gilberto Nunez Mora",
      employeeId: "EMP-0207",
      email: "gilberto.nunez@cuidado-pug.com",
      phone: "81 6601 2207",
      branch: "Apodaca",
      shift: "L-S 12:00 a 20:00",
      seniority: "3 anios",
      issueDate: "Emitido 2025-08-16",
      hireDate: "2022-07-04",
      birthDate: "1993-03-09",
      bloodType: "B-",
      emergencyContact: "Elena Mora (Madre) - 81 6219 1144",
      certifications: "Diagnostico rapido",
      notes: "Atiende incidencias mecanicas reportadas por sucursales.",
    },
    {
      name: "Sandra Beltran Vela",
      employeeId: "EMP-0208",
      email: "sandra.beltran@cuidado-pug.com",
      phone: "81 6601 2208",
      branch: "Escobedo",
      shift: "L-V 11:00 a 19:00",
      seniority: "2 anios",
      issueDate: "Emitido 2025-06-02",
      hireDate: "2023-03-06",
      birthDate: "1996-05-18",
      bloodType: "AB-",
      emergencyContact: "Omar Vela (Conyuge) - 81 7210 8844",
      certifications: "Auditoria de flota",
      notes: "Consolida reportes semanales de disponibilidad y estatus de patio.",
    },
    {
      name: "Ivan Cardenas Perez",
      employeeId: "EMP-0209",
      email: "ivan.cardenas@cuidado-pug.com",
      phone: "81 6601 2209",
      branch: "Monterrey Centro",
      shift: "L-S 06:30 a 15:30",
      seniority: "4 anios",
      issueDate: "Emitido 2025-09-26",
      hireDate: "2021-08-30",
      birthDate: "1992-02-20",
      bloodType: "O+",
      emergencyContact: "Miriam Perez (Madre) - 81 2244 7711",
      certifications: "Control de patio y llaves",
      notes: "Responsable de salidas tempranas y entrega de llaves operativas.",
    },
  ]),
};

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

function formatCurrency(value) {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "$0";
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatSalesStatus(status, isPaid) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "accepted" || isPaid) return "Pagado";
  if (normalized === "refunded" || normalized === "reimbursed") return "Reembolsado";
  if (normalized === "no_aplica") return "No aplica";
  if (normalized === "pending") return "Pendiente";
  if (normalized === "cancelled") return "Cancelado";
  if (normalized === "completed") return "Completado";
  return normalized || "-";
}

function formatPaymentMethod(method) {
  const normalized = String(method || "").toLowerCase();
  if (normalized === "tarjeta") return "Tarjeta";
  if (normalized === "cheque") return "Cheque";
  if (normalized === "deposito") return "Deposito";
  if (normalized === "efectivo") return "Efectivo";
  if (normalized === "msi") return "Meses sin intereses";
  if (normalized === "sin_registro") return "Sin registro";
  return normalized || "-";
}

function formatReservationStatus(status) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "pending") return "Pendiente";
  if (normalized === "confirmed") return "Confirmada";
  if (normalized === "in_progress") return "En curso";
  if (normalized === "completed") return "Completada";
  if (normalized === "cancelled") return "Cancelada";
  return normalized || "-";
}

function formatRefundStatus(status) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "pendiente") return "Pendiente";
  if (normalized === "reembolsado") return "Reembolsado";
  return "No aplica";
}

function formatPriority(priority) {
  const normalized = String(priority || "").toLowerCase();
  if (normalized === "alta") return "Alta";
  if (normalized === "media") return "Media";
  if (normalized === "baja") return "Baja";
  return normalized || "-";
}

function resetCrmDetail() {
  if (!crmDetailHint || !crmDetailBody) return;
  crmDetailHint.hidden = false;
  crmDetailBody.hidden = true;
  if (crmDetailPanel) {
    crmDetailPanel.classList.remove("expanded");
  }
}

function fillCrmDetail(field, value) {
  if (!field) return;
  field.textContent = value || "-";
}

function renderCrmDetail(caseItem) {
  if (!caseItem || !crmDetailHint || !crmDetailBody) return;

  const contactParts = [caseItem.email, caseItem.phone].filter(Boolean);
  fillCrmDetail(crmDetailCaseId, caseItem.case_id || "-");
  fillCrmDetail(crmDetailFolio, caseItem.folio || "-");
  fillCrmDetail(crmDetailClient, caseItem.client || "Sin cliente");
  fillCrmDetail(crmDetailContact, contactParts.join(" | ") || "-");
  fillCrmDetail(crmDetailType, caseItem.case_type || "-");
  fillCrmDetail(crmDetailPriority, formatPriority(caseItem.priority));
  fillCrmDetail(crmDetailStatus, caseItem.status || "-");
  fillCrmDetail(crmDetailReservationStatus, formatReservationStatus(caseItem.reservation_status));
  fillCrmDetail(crmDetailRefundStatus, formatRefundStatus(caseItem.refund_status));
  fillCrmDetail(crmDetailChannel, caseItem.channel || "-");
  fillCrmDetail(crmDetailAmount, formatCurrency(caseItem.amount));
  fillCrmDetail(crmDetailInvoice, caseItem.invoice_number || "-");
  fillCrmDetail(crmDetailLastUpdate, formatDate(caseItem.last_update));
  fillCrmDetail(crmDetailMessage, caseItem.message || "Sin descripcion adicional.");

  crmDetailHint.hidden = true;
  crmDetailBody.hidden = false;
  if (crmDetailPanel) {
    crmDetailPanel.classList.add("expanded");
  }
}

function renderStatusOptions(options, selected) {
  return options
    .map((option) => {
      const isSelected = option === selected ? "selected" : "";
      return `<option value="${option}" ${isSelected}>${option}</option>`;
    })
    .join("");
}

function getVehicleStatusStyleClass(status) {
  const normalized = String(status || "").toLowerCase();
  if (normalized === "available") return "status-available";
  if (normalized === "reserved") return "status-reserved";
  if (normalized === "maintenance") return "status-maintenance";
  if (normalized === "in_use") return "status-in-use";
  if (normalized === "unavailable") return "status-unavailable";
  return "status-neutral";
}

function getVehicleStatusLabel(status) {
  const normalized = String(status || "").toLowerCase();
  return vehicleStatusLabels[normalized] || normalized || "-";
}

function renderVehicleStatusOptions(selected) {
  return vehicleStatuses
    .map((option) => {
      const isSelected = option === selected ? "selected" : "";
      return `<option value="${option}" ${isSelected}>${escapeHtml(getVehicleStatusLabel(option))}</option>`;
    })
    .join("");
}

function getViewFromHash() {
  const hash = (window.location.hash || "").replace("#", "").trim().toLowerCase();
  return hash || DEFAULT_ADMIN_VIEW;
}

function activateAdminView(viewName) {
  const requestedView = (viewName || "").toLowerCase();
  const targetView = [...adminViews].some((node) => node.dataset.adminView === requestedView)
    ? requestedView
    : DEFAULT_ADMIN_VIEW;

  sidebarItems.forEach((item) => {
    item.classList.toggle("active", item.dataset.sidebarView === targetView);
  });

  adminViews.forEach((view) => {
    view.classList.toggle("active", view.dataset.adminView === targetView);
  });

  return targetView;
}

function initSidebar() {
  if (!sidebarToggle || !adminSidebar) return;

  const mobileQuery = window.matchMedia("(max-width: 900px)");

  function syncSidebarToggle() {
    const expanded = mobileQuery.matches
      ? document.body.classList.contains("sidebar-open")
      : !document.body.classList.contains("sidebar-collapsed");
    sidebarToggle.setAttribute("aria-expanded", String(expanded));
  }

  sidebarToggle.addEventListener("click", () => {
    if (mobileQuery.matches) {
      document.body.classList.toggle("sidebar-open");
    } else {
      document.body.classList.toggle("sidebar-collapsed");
    }
    syncSidebarToggle();
  });

  document.addEventListener("click", (event) => {
    if (!mobileQuery.matches || !document.body.classList.contains("sidebar-open")) return;

    const insideSidebar = adminSidebar.contains(event.target);
    const insideToggle = sidebarToggle.contains(event.target);
    if (!insideSidebar && !insideToggle) {
      document.body.classList.remove("sidebar-open");
      syncSidebarToggle();
    }
  });

  window.addEventListener("resize", () => {
    if (!mobileQuery.matches) {
      document.body.classList.remove("sidebar-open");
    }
    syncSidebarToggle();
  });

  sidebarItems.forEach((item) => {
    item.addEventListener("click", () => {
      const targetView = activateAdminView(item.dataset.sidebarView);
      const targetHash = `#${targetView}`;
      if (window.location.hash !== targetHash) {
        window.location.hash = targetView;
      }

      if (mobileQuery.matches) {
        document.body.classList.remove("sidebar-open");
        syncSidebarToggle();
      }
    });
  });

  window.addEventListener("hashchange", () => {
    activateAdminView(getViewFromHash());
  });

  const initialView = activateAdminView(getViewFromHash());
  if (window.location.hash !== `#${initialView}`) {
    history.replaceState(null, "", `#${initialView}`);
  }

  syncSidebarToggle();
}

function initOrgChartDetails() {
  if (
    !orgRoleCards.length ||
    !orgEmployeePanel ||
    !orgDetailHint ||
    !orgDetailBody ||
    !orgEmployeeRole ||
    !orgEmployeeArea ||
    !orgEmployeeName ||
    !orgEmployeeId ||
    !orgEmployeeEmail ||
    !orgEmployeePhone ||
    !orgEmployeeBranch ||
    !orgEmployeeShift ||
    !orgEmployeeSeniority ||
    !orgEmployeeStatus ||
    !orgEmployeeInitials ||
    !orgEmployeeNationality ||
    !orgEmployeeIssueDate ||
    !orgEmployeeHireDate ||
    !orgEmployeeBirthDate ||
    !orgEmployeeBloodType ||
    !orgEmployeeEmergencyContact ||
    !orgEmployeeCertifications ||
    !orgEmployeeNotes ||
    !orgEmployeesMeta ||
    !orgEmployeesList
  ) {
    return;
  }

  function renderOrgEmployeeList(roleKey, team, selectedIndex) {
    orgEmployeesMeta.textContent = `Mostrando ${selectedIndex + 1} de ${team.length} colaboradores de ${team[0].role}.`;
    orgEmployeesList.innerHTML = team
      .map((employee, index) => {
        const isActive = index === selectedIndex ? "active" : "";
        return `
          <button class="org-employee-chip ${isActive}" type="button" data-org-role-key="${roleKey}" data-org-employee-index="${index}">
            <span>${escapeHtml(employee.name)}</span>
            <small>${escapeHtml(employee.employeeId)}</small>
          </button>
        `;
      })
      .join("");
  }

  function renderOrgProfile(roleKey, employeeIndex = 0) {
    const team = orgEmployeeProfiles[roleKey];
    if (!Array.isArray(team) || !team.length) return;
    const safeIndex = Math.min(Math.max(employeeIndex, 0), team.length - 1);
    const profile = team[safeIndex];

    orgRoleCards.forEach((card) => {
      card.classList.toggle("active", card.dataset.orgRole === roleKey);
    });

    renderOrgEmployeeList(roleKey, team, safeIndex);

    orgEmployeeRole.textContent = profile.role;
    orgEmployeeArea.textContent = profile.area;
    orgEmployeeName.textContent = profile.name;
    orgEmployeeId.textContent = profile.employeeId;
    orgEmployeeEmail.textContent = profile.email;
    orgEmployeePhone.textContent = profile.phone;
    orgEmployeeBranch.textContent = profile.branch;
    orgEmployeeShift.textContent = profile.shift;
    orgEmployeeSeniority.textContent = profile.seniority;
    orgEmployeeStatus.textContent = profile.status;
    orgEmployeeNationality.textContent = profile.nationality;
    orgEmployeeIssueDate.textContent = profile.issueDate;
    orgEmployeeHireDate.textContent = profile.hireDate;
    orgEmployeeBirthDate.textContent = profile.birthDate;
    orgEmployeeBloodType.textContent = profile.bloodType;
    orgEmployeeEmergencyContact.textContent = profile.emergencyContact;
    orgEmployeeCertifications.textContent = profile.certifications;
    orgEmployeeNotes.textContent = profile.notes;

    const initials = profile.name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((chunk) => chunk[0])
      .join("")
      .toUpperCase();
    orgEmployeeInitials.textContent = initials || "-";

    orgDetailHint.hidden = true;
    orgDetailBody.hidden = false;
    orgEmployeePanel.classList.add("expanded");
    orgDetailBody.scrollTop = 0;
  }

  orgRoleCards.forEach((card) => {
    card.addEventListener("click", () => {
      renderOrgProfile(card.dataset.orgRole, 0);
    });
  });

  orgEmployeesList.addEventListener("click", (event) => {
    const chip = event.target.closest("[data-org-employee-index]");
    if (!chip) return;

    const roleKey = chip.dataset.orgRoleKey;
    const employeeIndex = Number.parseInt(chip.dataset.orgEmployeeIndex || "", 10);
    if (!roleKey || Number.isNaN(employeeIndex)) return;

    renderOrgProfile(roleKey, employeeIndex);
  });
}

async function loadSummary() {
  const summary = await apiRequest("/api/admin/summary");
  usersTotal.textContent = summary.users.total;
  reservationsTotal.textContent = summary.reservations.total;
  reservationsPending.textContent = summary.reservations.pending;
  vehiclesActive.textContent = summary.vehicles.active;
}

async function loadSales() {
  if (
    !salesTable ||
    !salesIncomeDay ||
    !salesIncomeMonth ||
    !salesClosedReservations ||
    !salesCancelledReservations ||
    !salesRefundPending ||
    !salesAvgTicket
  ) {
    return;
  }

  const data = await apiRequest("/api/admin/sales");
  const totals = data.totals || {};
  const transactions = Array.isArray(data.transactions) ? data.transactions : [];

  salesIncomeDay.textContent = formatCurrency(totals.day);
  salesIncomeMonth.textContent = formatCurrency(totals.month);
  salesClosedReservations.textContent = String(totals.closed_reservations ?? 0);
  salesCancelledReservations.textContent = String(totals.cancelled_reservations ?? 0);
  salesRefundPending.textContent = String(totals.refund_pending ?? 0);
  salesAvgTicket.textContent = formatCurrency(totals.average_ticket);

  if (!transactions.length) {
    salesTable.innerHTML = '<tr><td colspan="8">No hay transacciones</td></tr>';
    return;
  }

  salesTable.innerHTML = transactions
    .map((transaction) => {
      return `
        <tr>
          <td>${escapeHtml(transaction.folio || `VT-${transaction.id ?? "-"}`)}</td>
          <td>${escapeHtml(transaction.client || "Sin cliente")}</td>
          <td>${escapeHtml(transaction.channel || "-")}</td>
          <td>${escapeHtml(formatPaymentMethod(transaction.payment_method))}</td>
          <td>${escapeHtml(formatCurrency(transaction.amount))}</td>
          <td>${escapeHtml(formatReservationStatus(transaction.reservation_status))}</td>
          <td>${escapeHtml(formatRefundStatus(transaction.refund_status))}</td>
          <td>${escapeHtml(formatSalesStatus(transaction.status, transaction.is_paid))}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadCrm() {
  if (
    !crmCasesTable ||
    !crmTotalCases ||
    !crmOpenCases ||
    !crmHighPriority ||
    !crmRefundPending
  ) {
    return;
  }

  const data = await apiRequest("/api/admin/crm");
  const totals = data.totals || {};
  const cases = Array.isArray(data.cases) ? data.cases : [];
  crmCasesCache = cases;

  crmTotalCases.textContent = String(totals.total_cases ?? 0);
  crmOpenCases.textContent = String(totals.open_cases ?? 0);
  crmHighPriority.textContent = String(totals.high_priority ?? 0);
  crmRefundPending.textContent = String(totals.refund_pending ?? 0);

  if (!cases.length) {
    crmCasesTable.innerHTML = '<tr><td colspan="7">No hay casos CRM</td></tr>';
    resetCrmDetail();
    return;
  }

  crmCasesTable.innerHTML = cases
    .map((item, index) => {
      const slaRisk = item.sla_at_risk ? " (Riesgo SLA)" : "";
      return `
        <tr>
          <td>
            <input type="checkbox" data-crm-case-index="${index}" aria-label="Seleccionar caso ${escapeHtml(item.case_id || index + 1)}" />
          </td>
          <td>${escapeHtml(item.folio || `VT-${item.reservation_id ?? "-"}`)}</td>
          <td>
            <strong>${escapeHtml(item.client || "Sin cliente")}</strong><br>
            <small>${escapeHtml(item.email || "-")}</small>
          </td>
          <td>${escapeHtml(item.case_type || "-")}</td>
          <td>${escapeHtml(formatPriority(item.priority))}</td>
          <td>${escapeHtml(item.status || "-")}</td>
          <td>${escapeHtml(formatDate(item.last_update))}${escapeHtml(slaRisk)}</td>
        </tr>
      `;
    })
    .join("");

  resetCrmDetail();
}

async function loadPaymentAlerts() {
  if (!priorityPaymentAlerts) return;

  const data = await apiRequest("/api/admin/payment-alerts");
  const alerts = Array.isArray(data.alerts) ? data.alerts : [];
  const threshold = data.threshold_days ?? 45;

  if (!alerts.length) {
    priorityPaymentAlerts.innerHTML = `<li>No hay alertas de pago mayores a ${threshold} dias.</li>`;
    return;
  }

  priorityPaymentAlerts.innerHTML = alerts
    .slice(0, 6)
    .map((alert) => {
      const clientLabel = alert.client || "Sin cliente";
      const amountLabel = formatCurrency(alert.amount_due);
      return `
        <li>
          ${escapeHtml(clientLabel)} | ${escapeHtml(alert.folio || `VT-${alert.reservation_id ?? "-"}`)} |
          ${escapeHtml(String(alert.days_without_payment ?? 0))} dias sin pago |
          ${escapeHtml(amountLabel)}
        </li>
      `;
    })
    .join("");
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
      const statusLabel = getVehicleStatusLabel(vehicle.status);
      const statusClass = getVehicleStatusStyleClass(vehicle.status);
      return `
        <tr>
          <td>#${vehicle.id}</td>
          <td>${escapeHtml(vehicle.brand)} ${escapeHtml(vehicle.model)} ${vehicle.year}</td>
          <td>${escapeHtml(vehicle.plate)}</td>
          <td>
            <input data-vehicle-price-day="${vehicle.id}" type="number" min="0" step="0.01"
              value="${vehicle.price_per_day ?? 0}" />
          </td>
          <td class="vehicle-status-cell">
            <span class="status-pill vehicle-status-pill ${statusClass}" data-vehicle-status-pill="${vehicle.id}">
              ${escapeHtml(statusLabel)}
            </span>
            <select data-vehicle-status="${vehicle.id}">
              ${renderVehicleStatusOptions(vehicle.status)}
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
  await Promise.all([loadSummary(), loadReservations(), loadSales(), loadVehicles(), loadCrm(), loadPaymentAlerts()]);
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
  await Promise.all([loadSummary(), loadVehicles()]);
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

vehiclesTable.addEventListener("change", (event) => {
  const select = event.target.closest("[data-vehicle-status]");
  if (!select) return;

  const vehicleId = select.dataset.vehicleStatus;
  const pill = document.querySelector(`[data-vehicle-status-pill="${vehicleId}"]`);
  if (!pill) return;

  const statusLabel = getVehicleStatusLabel(select.value);
  const statusClass = getVehicleStatusStyleClass(select.value);
  pill.className = `status-pill vehicle-status-pill ${statusClass}`;
  pill.textContent = statusLabel;
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

crmCasesTable.addEventListener("change", (event) => {
  const input = event.target.closest("[data-crm-case-index]");
  if (!input) return;

  const caseIndex = Number.parseInt(input.dataset.crmCaseIndex || "", 10);
  if (Number.isNaN(caseIndex)) return;

  const checkboxes = crmCasesTable.querySelectorAll("[data-crm-case-index]");
  checkboxes.forEach((checkboxNode) => {
    if (checkboxNode !== input) {
      checkboxNode.checked = false;
    }
  });

  if (!input.checked) {
    resetCrmDetail();
    return;
  }

  const selectedCase = crmCasesCache[caseIndex];
  renderCrmDetail(selectedCase);
});

refreshReservations.addEventListener("click", async () => {
  try {
    await Promise.all([loadReservations(), loadSales(), loadVehicles(), loadCrm(), loadPaymentAlerts()]);
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
    initSidebar();
    initOrgChartDetails();

    currentUser = await apiRequest("/api/auth/me");
    if (currentUser.role !== ACCESS_ADMIN) {
      showMessage("Tu cuenta no es administrativa.", "err");
      setTimeout(() => {
        window.location.href = "/";
      }, 700);
      return;
    }

    adminName.textContent = `${currentUser.full_name} (${currentUser.email})`;

    await Promise.all([
      loadSummary(),
      loadSales(),
      loadReservations(),
      loadVehicles(),
      loadUsers(),
      loadCrm(),
      loadPaymentAlerts(),
    ]);
  } catch (error) {
    showMessage(error.message, "err");
  }
}

bootstrap();
