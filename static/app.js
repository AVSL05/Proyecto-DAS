// Configuración de la API
const API_BASE_URL = 'http://localhost:8000/api';

// Variables para el carrusel
let currentReviewIndex = 0;
let reviewsData = [];
let autoRotateInterval;

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

// Búsqueda de Transportes
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        origen: document.getElementById('origen').value,
        destino: document.getElementById('destino').value,
        fecha_salida: document.getElementById('fecha').value,
        num_pasajeros: parseInt(document.getElementById('pasajeros').value)
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/search/transport`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        displaySearchResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al buscar transportes. Verifica que el servidor esté corriendo.');
    }
});

// Mostrar resultados de búsqueda
function displaySearchResults(data) {
    const container = document.getElementById('searchResults');
    
    if (data.total === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">No se encontraron transportes disponibles para esta búsqueda.</p>';
        return;
    }
    
    let html = `<h3>Resultados de búsqueda (${data.total} encontrados)</h3>`;
    
    data.resultados.forEach(transport => {
        html += `
            <div class="transport-card">
                <div class="transport-info">
                    <div>
                        <h4>${transport.empresa}</h4>
                        <p><strong>${transport.origen}</strong> → <strong>${transport.destino}</strong></p>
                        <p>🚌 ${transport.tipo.toUpperCase()} | 👥 Capacidad: ${transport.capacidad}</p>
                        <p>📅 ${transport.fecha_salida} a las ${transport.hora_salida}</p>
                    </div>
                    <div>
                        <div class="transport-price">$${transport.precio.toFixed(2)}</div>
                        <button class="btn btn-primary" onclick="alert('Función de reserva en desarrollo')">
                            Reservar
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
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
