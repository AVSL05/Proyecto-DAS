// Configuración de la API
const API_BASE_URL = 'http://localhost:8000/api';

// Variables para el carrusel
let currentReviewIndex = 0;
let reviewsData = [];
let autoRotateInterval;

// Variables para autocomplete
let ciudades = [];
let selectedOrigin = '';
let selectedDestination = '';

// Función para mostrar mensajes
function showMessage(elementId, message, type = 'success') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = type;
    element.style.display = 'block';

    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// ===== AUTOCOMPLETE DE CIUDADES =====

// Cargar ciudades al inicio
async function loadCities() {
    try {
        const response = await fetch(`${API_BASE_URL}/search/cities`);
        const data = await response.json();
        ciudades = data.cities;
    } catch (error) {
        console.error('Error al cargar ciudades:', error);
    }
}

// Configurar autocomplete para un input
function setupAutocomplete(inputId, suggestionsId, onSelectCallback) {
    const input = document.getElementById(inputId);
    const suggestionsDiv = document.getElementById(suggestionsId);

    input.addEventListener('input', async (e) => {
        const query = e.target.value.trim();

        if (query.length < 2) {
            suggestionsDiv.innerHTML = '';
            suggestionsDiv.style.display = 'none';
            return;
        }

        // Filtrar ciudades localmente
        const filtered = ciudades.filter(city =>
            city.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 8); // Limitar a 8 sugerencias

        if (filtered.length === 0) {
            suggestionsDiv.innerHTML = '<div class="suggestion-item">No se encontraron ciudades</div>';
            suggestionsDiv.style.display = 'block';
            return;
        }

        // Mostrar sugerencias
        suggestionsDiv.innerHTML = filtered.map(city =>
            `<div class="suggestion-item" data-city="${city}">${city}</div>`
        ).join('');

        suggestionsDiv.style.display = 'block';

        // Agregar eventos click a las sugerencias
        suggestionsDiv.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const city = item.getAttribute('data-city');
                input.value = city;
                suggestionsDiv.innerHTML = '';
                suggestionsDiv.style.display = 'none';
                if (onSelectCallback) onSelectCallback(city);
            });
        });
    });

    // Cerrar sugerencias al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.style.display = 'none';
        }
    });
}

// Inicializar autocomplete cuando cargue la página
document.addEventListener('DOMContentLoaded', async () => {
    await loadCities();

    // Configurar autocomplete para origen
    setupAutocomplete('origen', 'origenSuggestions', (city) => {
        selectedOrigin = city;
    });

    // Configurar autocomplete para destino
    setupAutocomplete('destino', 'destinoSuggestions', (city) => {
        selectedDestination = city;
    });

    // Configurar búsqueda de transportes
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const origen = document.getElementById('origen').value.trim();
            const destino = document.getElementById('destino').value.trim();
            const fecha = document.getElementById('fecha').value;
            const pasajeros = parseInt(document.getElementById('pasajeros').value);

            // Validar que haya datos
            if (!origen || !destino || !fecha || !pasajeros) {
                alert('Por favor completa todos los campos');
                return;
            }

            // Validar que sean ciudades válidas (solo si hay ciudades cargadas)
            if (ciudades.length > 0 && !ciudades.includes(origen)) {
                alert('Por favor selecciona una ciudad válida de origen');
                return;
            }

            if (ciudades.length > 0 && !ciudades.includes(destino)) {
                alert('Por favor selecciona una ciudad válida de destino');
                return;
            }

            if (origen === destino) {
                alert('El origen y destino deben ser diferentes');
                return;
            }

            try {
                // Construir query params
                const params = new URLSearchParams({
                    origin: origen,
                    destination: destino,
                    start_date: fecha,
                    capacity: pasajeros
                });

                const response = await fetch(`${API_BASE_URL}/search/vehicles?${params}`);
                const data = await response.json();

                displaySearchResults(data, origen, destino, fecha, pasajeros);
            } catch (error) {
                console.error('Error:', error);
                alert('Error al buscar transportes. Verifica que el servidor esté corriendo.');
            }
        });
    }

    // Cargar promociones y reviews
    loadPromotions();
    loadReviews();
});

// Mostrar resultados de búsqueda
function displaySearchResults(data, origen, destino, fecha, pasajeros) {
    const container = document.getElementById('searchResults');

    if (data.total === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <h3>😔 No se encontraron vehículos disponibles</h3>
                <p>Intenta con diferentes fechas o criterios de búsqueda</p>
            </div>
        `;
        return;
    }

    let html = `
        <div style="margin: 30px 0 20px;">
            <h3 style="color: white;">Vehículos disponibles (${data.total} encontrados)</h3>
            <p style="color: white; font-size: 1.05em;">
                📍 ${origen} → ${destino} | 📅 ${fecha} | 👥 ${pasajeros} pasajero(s)
            </p>
        </div>
    `;

    data.vehicles.forEach(vehicle => {
        const typeEmoji = {
            'van': '🚐',
            'pickup': '🛻',
            'truck': '🚚',
            'suv': '🚙',
            'minibus': '🚌'
        };

        const emoji = typeEmoji[vehicle.vehicle_type] || '🚗';

        html += `
            <div class="vehicle-card">
                <div class="vehicle-image">
                    ${vehicle.image_url
                ? `<img src="${vehicle.image_url}" alt="${vehicle.brand} ${vehicle.model}" onerror="this.src='https://via.placeholder.com/300x200?text=Vehículo'">`
                : `<div class="vehicle-placeholder">${emoji}</div>`
            }
                </div>
                <div class="vehicle-details">
                    <div class="vehicle-header">
                        <h4>${vehicle.brand} ${vehicle.model} ${vehicle.year}</h4>
                        <span class="vehicle-type">${emoji} ${vehicle.vehicle_type.toUpperCase()}</span>
                    </div>
                    
                    <div class="vehicle-specs">
                        <span>👥 ${vehicle.capacity} pasajeros</span>
                        <span>🎨 ${vehicle.color || 'N/A'}</span>
                        <span>🔖 ${vehicle.plate}</span>
                    </div>
                    
                    ${vehicle.description ? `<p class="vehicle-description">${vehicle.description}</p>` : ''}
                    
                    <div class="vehicle-footer">
                        <div class="vehicle-pricing">
                            <div class="price-main">$${vehicle.price_per_day.toFixed(2)} <span class="price-unit">/ día</span></div>
                            ${vehicle.price_per_hour ? `<div class="price-secondary">$${vehicle.price_per_hour.toFixed(2)} / hora</div>` : ''}
                        </div>
                        <button class="btn btn-primary" onclick="selectVehicle('${vehicle.id}', '${vehicle.brand} ${vehicle.model}', ${vehicle.price_per_day})">
                            Seleccionar
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;

    // Scroll suave a los resultados
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Seleccionar vehículo
function selectVehicle(vehicleId, vehicleName, pricePerDay) {
    const token = localStorage.getItem('access_token');

    if (!token) {
        if (confirm('Debes iniciar sesión para hacer una reservación. ¿Deseas ir al login?')) {
            window.location.href = '/login';
        }
        return;
    }

    // Guardar información para la reservación
    const reservationData = {
        vehicle_id: vehicleId,
        vehicle_name: vehicleName,
        price_per_day: Number(pricePerDay || 0),
        origin: document.getElementById('origen').value,
        destination: document.getElementById('destino').value,
        start_date: document.getElementById('fecha').value,
        passengers: document.getElementById('pasajeros').value
    };

    localStorage.setItem('pending_reservation', JSON.stringify(reservationData));

    window.location.href = '/payment';
}

// Cargar Promociones
async function loadPromotions() {
    try {
        const response = await fetch(`${API_BASE_URL}/promotions`);
        const promotions = await response.json();
        displayPromotions(promotions);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar promociones');
    }
}

// Mostrar Promociones
function displayPromotions(promotions) {
    const container = document.getElementById('promotionsContainer');

    if (promotions.length === 0) {
        container.innerHTML = '<p>No hay promociones disponibles en este momento.</p>';
        return;
    }

    let html = '';
    promotions.forEach(promo => {
        html += `
            <div class="promotion-card">
                <h3>${promo.titulo}</h3>
                <div class="promotion-discount">${promo.descuento}% OFF</div>
                <p>${promo.descripcion}</p>
                <p style="font-size: 0.9em; margin-top: 15px;">
                    Válido del ${promo.fecha_inicio} al ${promo.fecha_fin}
                </p>
                <button class="btn btn-primary" style="margin-top: 15px;" 
                        onclick="alert('Código de promoción: PROMO${promo.id}')">
                    Usar Promoción
                </button>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Cargar Reviews para el carrusel
async function loadReviewsCarousel() {
    try {
        const response = await fetch(`${API_BASE_URL}/reviews`);
        const data = await response.json();
        reviewsData = data.reviews;
        displayCarousel();
        startAutoRotate();
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('reviewCarousel').innerHTML =
            '<div class="carousel-loading">Error al cargar calificaciones</div>';
    }
}

// Mostrar carrusel de reviews
function displayCarousel() {
    if (reviewsData.length === 0) {
        document.getElementById('reviewCarousel').innerHTML =
            '<div class="carousel-loading">No hay calificaciones disponibles</div>';
        return;
    }

    const review = reviewsData[currentReviewIndex];
    const carousel = document.getElementById('reviewCarousel');

    carousel.innerHTML = `
        <div class="review-carousel-item">
            <div class="review-stars">${getStars(review.calificacion)}</div>
            <p class="review-text">"${review.comentario}"</p>
            <p class="review-author">- ${review.usuario}</p>
            <p class="review-date">${review.fecha}</p>
        </div>
    `;

    // Actualizar dots
    updateDots();
}

// Actualizar indicadores (dots) del carrusel
function updateDots() {
    const dotsContainer = document.getElementById('carouselDots');
    let dotsHtml = '';

    for (let i = 0; i < reviewsData.length; i++) {
        dotsHtml += `<span class="dot ${i === currentReviewIndex ? 'active' : ''}" onclick="goToReview(${i})"></span>`;
    }

    dotsContainer.innerHTML = dotsHtml;
}

// Navegación del carrusel
function nextReview() {
    if (reviewsData.length === 0) return;
    currentReviewIndex = (currentReviewIndex + 1) % reviewsData.length;
    displayCarousel();
    resetAutoRotate();
}

function previousReview() {
    if (reviewsData.length === 0) return;
    currentReviewIndex = (currentReviewIndex - 1 + reviewsData.length) % reviewsData.length;
    displayCarousel();
    resetAutoRotate();
}

function goToReview(index) {
    currentReviewIndex = index;
    displayCarousel();
    resetAutoRotate();
}

// Auto-rotación del carrusel
function startAutoRotate() {
    autoRotateInterval = setInterval(() => {
        nextReview();
    }, 5000); // Cambiar cada 5 segundos
}

function resetAutoRotate() {
    clearInterval(autoRotateInterval);
    startAutoRotate();
}

// Generar estrellas
function getStars(rating) {
    return '⭐'.repeat(rating);
}

// Suscripción a Newsletter
document.getElementById('newsletterForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;

    try {
        const response = await fetch(`${API_BASE_URL}/newsletter/subscribe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('newsletterMessage', data.message, 'success');
            document.getElementById('newsletterForm').reset();
        } else {
            showMessage('newsletterMessage', data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('newsletterMessage', 'Error al suscribirse', 'error');
    }
});

// Cargar contenido al cargar la página
window.addEventListener('load', () => {
    // Establecer fecha mínima como hoy
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('fecha').setAttribute('min', today);
    document.getElementById('fecha').value = today;

    // Cargar promociones automáticamente
    loadPromotions();

    // Cargar reviews en el carrusel
    loadReviewsCarousel();
});
