const API_BASE_URL = "http://localhost:8000/api";

let pendingReservation = null;
let activePromotions = [];

const summaryVehicle = document.getElementById("summaryVehicle");
const summaryOrigin = document.getElementById("summaryOrigin");
const summaryDestination = document.getElementById("summaryDestination");
const summaryPassengers = document.getElementById("summaryPassengers");
const summaryPricePerDay = document.getElementById("summaryPricePerDay");
const summarySubtotal = document.getElementById("summarySubtotal");
const summaryDiscount = document.getElementById("summaryDiscount");
const summaryTotal = document.getElementById("summaryTotal");

const promotionSelect = document.getElementById("promotionSelect");
const promotionHelp = document.getElementById("promotionHelp");

const paymentForm = document.getElementById("paymentForm");
const paymentMessage = document.getElementById("paymentMessage");
const confirmPaymentBtn = document.getElementById("confirmPaymentBtn");
const cancelPaymentBtn = document.getElementById("cancelPaymentBtn");

const payerName = document.getElementById("payerName");
const payerEmail = document.getElementById("payerEmail");
const payerPhone = document.getElementById("payerPhone");

const startDateInput = document.getElementById("startDate");
const endDateInput = document.getElementById("endDate");
const pickupLocationInput = document.getElementById("pickupLocation");
const returnLocationInput = document.getElementById("returnLocation");
const notesInput = document.getElementById("paymentNotes");

const cardHolderInput = document.getElementById("cardHolder");
const cardNumberInput = document.getElementById("cardNumber");
const cardExpiryInput = document.getElementById("cardExpiry");
const cardCvvInput = document.getElementById("cardCvv");

const checkBankInput = document.getElementById("checkBank");
const checkNumberInput = document.getElementById("checkNumber");
const checkHolderInput = document.getElementById("checkHolder");

const depositBankInput = document.getElementById("depositBank");
const depositRefInput = document.getElementById("depositRef");
const depositDateInput = document.getElementById("depositDate");

const fieldsTarjeta = document.getElementById("fieldsTarjeta");
const fieldsCheque = document.getElementById("fieldsCheque");
const fieldsDeposito = document.getElementById("fieldsDeposito");

function formatCurrency(value) {
    const amount = Number(value || 0);
    if (!Number.isFinite(amount)) return "$0";
    return new Intl.NumberFormat("es-MX", {
        style: "currency",
        currency: "MXN",
        maximumFractionDigits: 2,
    }).format(amount);
}

function showPaymentMessage(message, type) {
    paymentMessage.hidden = false;
    paymentMessage.className = `payment-message ${type}`;
    paymentMessage.textContent = message;
}

function clearPaymentMessage() {
    paymentMessage.hidden = true;
    paymentMessage.className = "payment-message";
    paymentMessage.textContent = "";
}

function getAuthToken() {
    return localStorage.getItem("access_token") || "";
}

function plusDays(dateValue, days) {
    const date = new Date(`${dateValue}T00:00:00`);
    if (Number.isNaN(date.getTime())) return "";
    date.setDate(date.getDate() + days);
    return date.toISOString().split("T")[0];
}

function toIsoAtUtcMorning(dateValue, isEndDate = false) {
    const [year, month, day] = String(dateValue || "")
        .split("-")
        .map((item) => Number.parseInt(item, 10));
    if (!year || !month || !day) return null;

    const targetHour = isEndDate ? 23 : 12;
    const utcDate = new Date(Date.UTC(year, month - 1, day, targetHour, 0, 0, 0));
    if (Number.isNaN(utcDate.getTime())) return null;

    if (!isEndDate) {
        const now = new Date();
        if (utcDate.getTime() <= now.getTime()) {
            return new Date(now.getTime() + 5 * 60 * 1000).toISOString();
        }
    }

    return utcDate.toISOString();
}

function getSelectedPaymentMethod() {
    const selected = document.querySelector('input[name="payment_method"]:checked');
    return selected ? selected.value : "efectivo";
}

function setMethodRequired(method) {
    [
        cardHolderInput,
        cardNumberInput,
        cardExpiryInput,
        cardCvvInput,
        checkBankInput,
        checkNumberInput,
        checkHolderInput,
        depositBankInput,
        depositRefInput,
        depositDateInput,
    ].forEach((field) => {
        field.required = false;
    });

    if (method === "tarjeta") {
        cardHolderInput.required = true;
        cardNumberInput.required = true;
        cardExpiryInput.required = true;
        cardCvvInput.required = true;
    } else if (method === "cheque") {
        checkBankInput.required = true;
        checkNumberInput.required = true;
        checkHolderInput.required = true;
    } else if (method === "deposito") {
        depositBankInput.required = true;
        depositRefInput.required = true;
        depositDateInput.required = true;
    }
}

function togglePaymentMethodFields() {
    const method = getSelectedPaymentMethod();

    fieldsTarjeta.hidden = method !== "tarjeta";
    fieldsCheque.hidden = method !== "cheque";
    fieldsDeposito.hidden = method !== "deposito";

    setMethodRequired(method);
}

function getSelectedPromotion() {
    const promoId = Number.parseInt(promotionSelect.value || "", 10);
    if (Number.isNaN(promoId)) return null;
    return activePromotions.find((promo) => promo.id === promoId) || null;
}

function calculatePricing() {
    const pricePerDay = Number(pendingReservation?.price_per_day || 0);
    const startValue = startDateInput.value;
    const endValue = endDateInput.value;

    const start = new Date(`${startValue}T00:00:00`);
    const end = new Date(`${endValue}T00:00:00`);
    const diffMs = end.getTime() - start.getTime();
    const totalDays = Number.isFinite(diffMs) && diffMs > 0
        ? Math.max(1, Math.ceil(diffMs / (1000 * 60 * 60 * 24)))
        : 0;

    const subtotal = totalDays * pricePerDay;
    const promo = getSelectedPromotion();
    const discountPercent = promo ? Number(promo.descuento || 0) : 0;
    const discountAmount = subtotal * (discountPercent / 100);
    const total = Math.max(0, subtotal - discountAmount);

    summarySubtotal.textContent = formatCurrency(subtotal);
    summaryDiscount.textContent = `-${formatCurrency(discountAmount)}`;
    summaryTotal.textContent = formatCurrency(total);

    if (promo) {
        promotionHelp.textContent = `${promo.titulo}: ${promo.descuento}% de descuento aplicado`;
    } else {
        promotionHelp.textContent = "Se aplicara automaticamente al total final.";
    }

    return {
        totalDays,
        subtotal,
        discountAmount,
        total,
        promotion: promo,
    };
}

function buildPaymentMetadata(method) {
    if (method === "tarjeta") {
        const digits = cardNumberInput.value.replace(/\D/g, "");
        const last4 = digits.slice(-4) || "0000";
        return {
            reference: `CARD-${last4}`,
            detail: `Pago con tarjeta terminacion ${last4}`,
        };
    }

    if (method === "cheque") {
        const checkRef = checkNumberInput.value.trim();
        return {
            reference: checkRef || null,
            detail: `Pago con cheque ${checkRef} banco ${checkBankInput.value.trim()}`,
        };
    }

    if (method === "deposito") {
        const depositRef = depositRefInput.value.trim();
        return {
            reference: depositRef || null,
            detail: `Pago por deposito ref ${depositRef} banco ${depositBankInput.value.trim()}`,
        };
    }

    return {
        reference: null,
        detail: "Pago en efectivo",
    };
}

function validateMethodFields(method) {
    if (method === "tarjeta") {
        const digits = cardNumberInput.value.replace(/\D/g, "");
        if (digits.length < 13 || digits.length > 19) {
            return "Numero de tarjeta invalido.";
        }
        if (String(cardCvvInput.value || "").trim().length < 3) {
            return "CVV invalido.";
        }
    }

    if (method === "cheque") {
        if (!checkNumberInput.value.trim() || !checkBankInput.value.trim() || !checkHolderInput.value.trim()) {
            return "Completa los datos del cheque.";
        }
    }

    if (method === "deposito") {
        if (!depositBankInput.value.trim() || !depositRefInput.value.trim() || !depositDateInput.value) {
            return "Completa los datos del deposito.";
        }
    }

    return "";
}

function initPendingReservation() {
    const raw = localStorage.getItem("pending_reservation");
    if (!raw) return false;

    try {
        pendingReservation = JSON.parse(raw);
    } catch (error) {
        return false;
    }

    if (!pendingReservation?.vehicle_id || !pendingReservation?.price_per_day) {
        return false;
    }

    summaryVehicle.textContent = pendingReservation.vehicle_name || "Vehiculo";
    summaryOrigin.textContent = pendingReservation.origin || "-";
    summaryDestination.textContent = pendingReservation.destination || "-";
    summaryPassengers.textContent = pendingReservation.passengers || "-";
    summaryPricePerDay.textContent = formatCurrency(pendingReservation.price_per_day);

    const today = new Date().toISOString().split("T")[0];
    const selectedStart = pendingReservation.start_date || today;
    const minEnd = plusDays(selectedStart, 1) || today;

    startDateInput.min = today;
    startDateInput.value = selectedStart;
    endDateInput.min = minEnd;
    endDateInput.value = minEnd;

    pickupLocationInput.value = pendingReservation.origin || "";
    returnLocationInput.value = pendingReservation.destination || pendingReservation.origin || "";

    return true;
}

function syncDateConstraints() {
    if (!startDateInput.value) return;
    const minEnd = plusDays(startDateInput.value, 1);
    if (!minEnd) return;
    endDateInput.min = minEnd;
    if (!endDateInput.value || endDateInput.value < minEnd) {
        endDateInput.value = minEnd;
    }
}

async function loadPromotions() {
    try {
        const response = await fetch(`${API_BASE_URL}/promotions`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar promociones.");
        }

        activePromotions = await response.json();
        const options = ['<option value="">Sin promocion</option>'];
        activePromotions.forEach((promo) => {
            options.push(`<option value="${promo.id}">${promo.titulo} (${promo.descuento}% OFF)</option>`);
        });
        promotionSelect.innerHTML = options.join("");
    } catch (error) {
        activePromotions = [];
        promotionSelect.innerHTML = '<option value="">Sin promocion</option>';
        promotionHelp.textContent = "No se pudieron cargar promociones vigentes.";
    }
}

async function loadCurrentUserProfile() {
    const token = getAuthToken();
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        if (!response.ok) return;

        const user = await response.json();
        payerName.value = user.full_name || "";
        payerEmail.value = user.email || "";
        payerPhone.value = user.phone || "";
    } catch (error) {
        // Silencioso: no bloquea la reserva.
    }
}

function lockForm(disabled) {
    confirmPaymentBtn.disabled = disabled;
    confirmPaymentBtn.textContent = disabled ? "Procesando..." : "Confirmar pago y reservar";
}

async function submitPayment(event) {
    event.preventDefault();
    clearPaymentMessage();

    const token = getAuthToken();
    if (!token) {
        showPaymentMessage("Debes iniciar sesion para completar la reservacion.", "error");
        setTimeout(() => {
            window.location.href = "/login";
        }, 800);
        return;
    }

    const method = getSelectedPaymentMethod();
    const methodValidationError = validateMethodFields(method);
    if (methodValidationError) {
        showPaymentMessage(methodValidationError, "error");
        return;
    }

    syncDateConstraints();
    const pricing = calculatePricing();
    if (pricing.totalDays <= 0) {
        showPaymentMessage("La fecha de regreso debe ser posterior a la fecha de salida.", "error");
        return;
    }

    const startIso = toIsoAtUtcMorning(startDateInput.value, false);
    const endIso = toIsoAtUtcMorning(endDateInput.value, true);
    if (!startIso || !endIso) {
        showPaymentMessage("Fechas invalidas para crear la reservacion.", "error");
        return;
    }

    const paymentMeta = buildPaymentMetadata(method);
    const userNotes = notesInput.value.trim();

    const payload = {
        vehicle_id: Number(pendingReservation.vehicle_id),
        start_date: startIso,
        end_date: endIso,
        pickup_location: pickupLocationInput.value.trim(),
        return_location: returnLocationInput.value.trim(),
        notes: userNotes || null,
        payment_method: method,
        payment_notes: paymentMeta.detail,
    };

    if (paymentMeta.reference) {
        payload.payment_reference = paymentMeta.reference;
    }

    if (pricing.promotion) {
        payload.promotion_id = pricing.promotion.id;
    }

    lockForm(true);
    try {
        const response = await fetch(`${API_BASE_URL}/reservations`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
        });

        const body = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(body.detail || "No fue posible registrar la reservacion.");
        }

        localStorage.removeItem("pending_reservation");
        showPaymentMessage(
            `Pago registrado y reservacion #${body.id} creada. Total final: ${formatCurrency(body.total_price)}.`,
            "success"
        );

        setTimeout(() => {
            window.location.href = "/";
        }, 1800);
    } catch (error) {
        showPaymentMessage(error.message || "Error procesando el pago.", "error");
    } finally {
        lockForm(false);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    cancelPaymentBtn.addEventListener("click", () => {
        window.location.href = "/";
    });

    const ready = initPendingReservation();
    if (!ready) {
        showPaymentMessage("No hay una reservacion pendiente. Selecciona un vehiculo primero.", "error");
        paymentForm.querySelectorAll("input, select, textarea, button").forEach((node) => {
            if (node.id !== "cancelPaymentBtn") {
                node.disabled = true;
            }
        });
        return;
    }

    await Promise.all([loadPromotions(), loadCurrentUserProfile()]);

    togglePaymentMethodFields();
    syncDateConstraints();
    calculatePricing();

    document.querySelectorAll('input[name="payment_method"]').forEach((radio) => {
        radio.addEventListener("change", () => {
            togglePaymentMethodFields();
            calculatePricing();
        });
    });

    startDateInput.addEventListener("change", () => {
        syncDateConstraints();
        calculatePricing();
    });
    endDateInput.addEventListener("change", calculatePricing);
    promotionSelect.addEventListener("change", calculatePricing);
    paymentForm.addEventListener("submit", submitPayment);
});
