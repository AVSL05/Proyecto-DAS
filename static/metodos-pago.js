// Métodos de Pago - Gestión de tarjetas guardadas

class PaymentMethodsManager {
    constructor() {
        this.paymentMethods = [];
        this.init();
    }

    init() {
        this.checkAuthentication();
        this.loadPaymentMethods();
        this.setupEventListeners();
    }

    checkAuthentication() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/login';
        }
    }

    setupEventListeners() {
        // Botón para mostrar formulario de agregar tarjeta
        document.getElementById('addCardBtn').addEventListener('click', () => {
            this.showAddCardForm();
        });

        // Cancelar formulario
        document.getElementById('cancelAddCard').addEventListener('click', () => {
            this.hideAddCardForm();
        });

        // Enviar formulario
        document.getElementById('addCardForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addPaymentMethod();
        });

        // Formatear número de tarjeta automáticamente
        document.getElementById('cardNumber').addEventListener('input', (e) => {
            this.formatCardNumber(e.target);
        });

        // Detectar tipo de tarjeta
        document.getElementById('cardNumber').addEventListener('input', (e) => {
            this.detectCardType(e.target.value);
        });

        // Formatear fecha de expiración
        document.getElementById('expiryDate').addEventListener('input', (e) => {
            this.formatExpiryDate(e.target);
        });
    }

    showAddCardForm() {
        document.getElementById('addCardFormContainer').style.display = 'block';
        document.getElementById('addCardBtn').style.display = 'none';
    }

    hideAddCardForm() {
        document.getElementById('addCardFormContainer').style.display = 'none';
        document.getElementById('addCardBtn').style.display = 'block';
        document.getElementById('addCardForm').reset();
    }

    formatCardNumber(input) {
        let value = input.value.replace(/\s/g, '');
        let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
        input.value = formatted;
    }

    detectCardType(cardNumber) {
        const cleaned = cardNumber.replace(/\s/g, '');
        let cardType = '';

        if (/^4/.test(cleaned)) {
            cardType = 'visa';
        } else if (/^5[1-5]/.test(cleaned)) {
            cardType = 'mastercard';
        } else if (/^3[47]/.test(cleaned)) {
            cardType = 'amex';
        }

        // Actualizar icono visual si existe
        const cardTypeIndicator = document.getElementById('cardTypeIndicator');
        if (cardTypeIndicator) {
            if (cardType) {
                cardTypeIndicator.textContent = this.getCardIcon(cardType);
                cardTypeIndicator.style.display = 'inline';
            } else {
                cardTypeIndicator.style.display = 'none';
            }
        }
    }

    formatExpiryDate(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        input.value = value;
    }

    getCardIcon(cardType) {
        const icons = {
            'visa': '💳 Visa',
            'mastercard': '💳 Mastercard',
            'amex': '💳 American Express'
        };
        return icons[cardType] || '💳';
    }

    async loadPaymentMethods() {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('/api/payment-methods/', {
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
                throw new Error('Error al cargar métodos de pago');
            }

            const data = await response.json();
            this.paymentMethods = data.payment_methods;
            this.displayPaymentMethods();
        } catch (error) {
            console.error('Error loading payment methods:', error);
            this.showMessage('Error al cargar métodos de pago', 'error');
        }
    }

    displayPaymentMethods() {
        const container = document.getElementById('paymentMethodsList');
        
        if (this.paymentMethods.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <h3 style="color: #666;">💳</h3>
                    <p style="color: #666;">No tienes métodos de pago guardados</p>
                    <p style="color: #999; font-size: 0.9em; margin-top: 10px;">
                        Agrega una tarjeta para hacer tus pagos más rápido
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.paymentMethods.map(method => 
            this.renderPaymentMethodCard(method)
        ).join('');

        // Agregar event listeners
        document.querySelectorAll('.set-default-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.target.dataset.id);
                this.setDefaultPaymentMethod(id);
            });
        });

        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.target.dataset.id);
                this.deletePaymentMethod(id);
            });
        });
    }

    renderPaymentMethodCard(method) {
        const cardIcon = this.getCardIcon(method.card_type);
        const isDefault = method.is_default;

        return `
            <div class="payment-method-card ${isDefault ? 'default' : ''}">
                <div class="payment-method-header">
                    <div class="card-info">
                        <span class="card-icon">${cardIcon}</span>
                        <div class="card-details">
                            <div class="card-number">•••• •••• •••• ${method.card_last4}</div>
                            <div class="card-holder">${method.card_holder}</div>
                        </div>
                    </div>
                    ${isDefault ? `
                        <span class="default-badge">Predeterminada</span>
                    ` : ''}
                </div>
                
                <div class="payment-method-body">
                    <div class="expiry-info">
                        Vence: ${method.expiry_month}/${method.expiry_year}
                    </div>
                </div>
                
                <div class="payment-method-actions">
                    ${!isDefault ? `
                        <button class="btn btn-secondary set-default-btn" data-id="${method.id}">
                            Predeterminada
                        </button>
                    ` : ''}
                    <button class="btn btn-danger delete-btn" data-id="${method.id}">
                        Eliminar
                    </button>
                </div>
            </div>
        `;
    }

    async addPaymentMethod() {
        try {
            const cardNumber = document.getElementById('cardNumber').value.replace(/\s/g, '');
            const cardHolder = document.getElementById('cardHolder').value.trim();
            const expiryDate = document.getElementById('expiryDate').value;
            const isDefault = document.getElementById('isDefault').checked;

            // Validaciones
            if (cardNumber.length < 15 || cardNumber.length > 16) {
                this.showMessage('Número de tarjeta inválido', 'error');
                return;
            }

            if (!cardHolder) {
                this.showMessage('Ingresa el nombre del titular', 'error');
                return;
            }

            const [month, year] = expiryDate.split('/');
            if (!month || !year || month.length !== 2 || year.length !== 2) {
                this.showMessage('Fecha de expiración inválida (MM/YY)', 'error');
                return;
            }

            // Detectar tipo de tarjeta
            let cardType = 'visa';
            if (/^5[1-5]/.test(cardNumber)) {
                cardType = 'mastercard';
            } else if (/^3[47]/.test(cardNumber)) {
                cardType = 'amex';
            }

            const currentYear = new Date().getFullYear() % 100; // Últimos 2 dígitos
            const fullYear = parseInt(year) + 2000;

            const payload = {
                card_type: cardType,
                card_holder: cardHolder,
                card_last4: cardNumber.slice(-4),
                expiry_month: month,
                expiry_year: fullYear.toString(),
                is_default: isDefault
            };

            const token = localStorage.getItem('access_token');
            const response = await fetch('/api/payment-methods/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return;
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al agregar método de pago');
            }

            this.showMessage('Método de pago agregado exitosamente', 'success');
            this.hideAddCardForm();
            await this.loadPaymentMethods();
        } catch (error) {
            console.error('Error adding payment method:', error);
            this.showMessage(error.message || 'Error al agregar método de pago', 'error');
        }
    }

    async setDefaultPaymentMethod(id) {
        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`/api/payment-methods/${id}/set-default`, {
                method: 'PUT',
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
                throw new Error('Error al establecer método predeterminado');
            }

            this.showMessage('Método de pago predeterminado actualizado', 'success');
            await this.loadPaymentMethods();
        } catch (error) {
            console.error('Error setting default:', error);
            this.showMessage(error.message || 'Error al establecer método predeterminado', 'error');
        }
    }

    async deletePaymentMethod(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este método de pago?')) {
            return;
        }

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`/api/payment-methods/${id}`, {
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
                throw new Error('Error al eliminar método de pago');
            }

            this.showMessage('Método de pago eliminado exitosamente', 'success');
            await this.loadPaymentMethods();
        } catch (error) {
            console.error('Error deleting payment method:', error);
            this.showMessage(error.message || 'Error al eliminar método de pago', 'error');
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
    new PaymentMethodsManager();
});
