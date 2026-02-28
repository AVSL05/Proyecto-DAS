// Mis Reservas - Gestión de reservaciones del usuario

class ReservationsManager {
    constructor() {
        this.reservations = [];
        this.stats = null;
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.checkAuthentication();
        this.loadStats();
        this.loadReservations();
        this.setupEventListeners();
    }

    checkAuthentication() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/login';
        }
    }

    setupEventListeners() {
        // Filtros de estado
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.setFilter(filter);
            });
        });
    }

    setFilter(filter) {
        this.currentFilter = filter;
        
        // Actualizar botones de filtro
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        // Recargar reservaciones con filtro
        this.loadReservations();
    }

    async loadStats() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('/api/reservations/stats', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return;
            }

            if (!response.ok) {
                throw new Error('Error al cargar estadísticas');
            }

            this.stats = await response.json();
            this.displayStats();
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    displayStats() {
        if (!this.stats) return;

        document.getElementById('totalReservations').textContent = this.stats.total_reservations;
        document.getElementById('activeReservations').textContent = this.stats.active_reservations;
        document.getElementById('completedReservations').textContent = this.stats.completed_reservations;
        document.getElementById('totalSpent').textContent = `$${parseFloat(this.stats.total_spent).toFixed(2)}`;
    }

    async loadReservations() {
        try {
            const token = localStorage.getItem('access_token');
            
            let url = '/api/reservations/';
            if (this.currentFilter !== 'all') {
                url += `?status_filter=${this.currentFilter}`;
            }

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return;
            }

            if (!response.ok) {
                throw new Error('Error al cargar reservaciones');
            }

            const data = await response.json();
            this.reservations = data.reservations;
            this.displayReservations();
        } catch (error) {
            console.error('Error loading reservations:', error);
            this.showMessage('Error al cargar las reservaciones', 'error');
        }
    }

    displayReservations() {
        const container = document.getElementById('reservationsList');
        
        if (this.reservations.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3 style="color: #666;">📋</h3>
                    <p style="color: #666;">No tienes reservaciones ${this.getFilterText()}</p>
                    <a href="/" class="btn btn-primary" style="margin-top: 15px; display: inline-block;">
                        Buscar Vehículos
                    </a>
                </div>
            `;
            return;
        }

        container.innerHTML = this.reservations.map(reservation => 
            this.renderReservationCard(reservation)
        ).join('');

        // Agregar event listeners a los botones de cancelar
        document.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const reservationId = parseInt(e.target.dataset.id);
                this.cancelReservation(reservationId);
            });
        });
    }

    renderReservationCard(reservation) {
        const statusInfo = this.getStatusInfo(reservation.status);
        const vehicle = reservation.vehicle || {};
        const startDate = new Date(reservation.start_date);
        const endDate = new Date(reservation.end_date);
        const canCancel = ['pending', 'confirmed'].includes(reservation.status);

        return `
            <div class="reservation-card" data-status="${reservation.status}">
                <div class="reservation-header">
                    <div class="reservation-id">
                        <strong>Reservación #${reservation.id}</strong>
                        <span class="reservation-status status-${reservation.status}">${statusInfo.label}</span>
                    </div>
                    <div class="reservation-price">
                        $${parseFloat(reservation.total_price).toFixed(2)} MXN
                    </div>
                </div>
                
                <div class="reservation-body">
                    <div class="reservation-vehicle">
                        ${vehicle.image_url ? `
                            <img src="${vehicle.image_url}" alt="${vehicle.brand} ${vehicle.model}" class="vehicle-thumbnail">
                        ` : `
                            <div class="vehicle-thumbnail-placeholder">🚐</div>
                        `}
                        <div class="vehicle-info">
                            <h3>${vehicle.brand || ''} ${vehicle.model || ''}</h3>
                            <p>${vehicle.year || ''} - ${this.translateVehicleType(vehicle.vehicle_type || '')} - ${vehicle.capacity || ''} pasajeros</p>
                        </div>
                    </div>
                    
                    <div class="reservation-details">
                        <div class="detail-row">
                            <span class="detail-label">📅 Fecha de inicio:</span>
                            <span class="detail-value">${this.formatDate(startDate)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📅 Fecha de fin:</span>
                            <span class="detail-value">${this.formatDate(endDate)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📍 Lugar de recogida:</span>
                            <span class="detail-value">${reservation.pickup_location}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">📍 Lugar de devolución:</span>
                            <span class="detail-value">${reservation.return_location || reservation.pickup_location}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">⏱️ Duración:</span>
                            <span class="detail-value">${reservation.total_days} ${reservation.total_days === 1 ? 'día' : 'días'}</span>
                        </div>
                        ${reservation.notes ? `
                            <div class="detail-row">
                                <span class="detail-label">📝 Notas:</span>
                                <span class="detail-value">${reservation.notes}</span>
                            </div>
                        ` : ''}
                        ${reservation.invoice_folio ? `
                            <div class="detail-row">
                                <span class="detail-label">📄 Folio:</span>
                                <span class="detail-value">${reservation.invoice_folio}</span>
                            </div>
                        ` : ''}
                        ${reservation.invoice_number ? `
                            <div class="detail-row">
                                <span class="detail-label">🧾 Factura:</span>
                                <span class="detail-value">${reservation.invoice_number}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="reservation-footer">
                    <div class="reservation-date">
                        Creada el ${this.formatDate(new Date(reservation.created_at))}
                    </div>
                    <div class="reservation-actions">
                        ${canCancel ? `
                            <button class="btn btn-danger cancel-btn" data-id="${reservation.id}">
                                Cancelar Reservación
                            </button>
                        ` : ''}
                        ${reservation.status === 'cancelled' && reservation.cancelled_at ? `
                            <span style="color: #999; font-size: 0.9em;">
                                Cancelada el ${this.formatDate(new Date(reservation.cancelled_at))}
                            </span>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    getStatusInfo(status) {
        const statusMap = {
            'pending': { label: 'Pendiente', color: '#FFA500' },
            'confirmed': { label: 'Confirmada', color: '#3575F6' },
            'in_progress': { label: 'En progreso', color: '#6366EB' },
            'completed': { label: 'Completada', color: '#28a745' },
            'cancelled': { label: 'Cancelada', color: '#999' }
        };
        return statusMap[status] || { label: status, color: '#666' };
    }

    getFilterText() {
        const filterTexts = {
            'all': '',
            'pending': 'pendientes',
            'confirmed': 'confirmadas',
            'in_progress': 'en progreso',
            'completed': 'completadas',
            'cancelled': 'canceladas'
        };
        return filterTexts[this.currentFilter] || '';
    }

    translateVehicleType(type) {
        const types = {
            'van': 'Van',
            'pickup': 'Pickup',
            'truck': 'Camión',
            'suv': 'SUV',
            'minibus': 'Minibús'
        };
        return types[type] || type;
    }

    formatDate(date) {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('es-MX', options);
    }

    async cancelReservation(reservationId) {
        if (!confirm('¿Estás seguro de que deseas cancelar esta reservación?')) {
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`/api/reservations/${reservationId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return;
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al cancelar la reservación');
            }

            this.showMessage('Reservación cancelada exitosamente', 'success');
            
            // Recargar datos
            await this.loadStats();
            await this.loadReservations();
        } catch (error) {
            console.error('Error cancelling reservation:', error);
            this.showMessage(error.message || 'Error al cancelar la reservación', 'error');
        }
    }

    showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-weight: 800;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => messageDiv.remove(), 300);
        }, 3000);
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    new ReservationsManager();
});
