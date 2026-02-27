// Sistema de menú de usuario
class UserMenu {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.userInfo = null;
        this.init();
    }

    async init() {
        await this.checkAuthStatus();
        this.setupEventListeners();
    }

    async checkAuthStatus() {
        const loginBtn = document.getElementById('loginBtn');
        const userMenuContainer = document.getElementById('userMenuContainer');

        if (!this.token) {
            // No hay sesión - mostrar botón de login
            if (loginBtn) loginBtn.style.display = 'inline-block';
            if (userMenuContainer) userMenuContainer.style.display = 'none';
            return;
        }

        // Hay token - verificar y obtener info del usuario
        try {
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Token inválido');
            }

            this.userInfo = await response.json();
            
            // Guardar info del usuario
            localStorage.setItem('user_email', this.userInfo.email || '');
            localStorage.setItem('user_name', this.userInfo.full_name || this.userInfo.email || 'Usuario');

            // Mostrar menú de usuario
            if (loginBtn) loginBtn.style.display = 'none';
            if (userMenuContainer) {
                userMenuContainer.style.display = 'flex';
                this.updateUserInfo();
            }
        } catch (error) {
            console.error('Error al verificar sesión:', error);
            this.logout();
        }
    }

    updateUserInfo() {
        const userNameElement = document.getElementById('userName');
        const userDropdownName = document.getElementById('userDropdownName');
        const userDropdownEmail = document.getElementById('userDropdownEmail');
        
        const userName = localStorage.getItem('user_name') || 'Usuario';
        const userEmail = localStorage.getItem('user_email') || 'usuario@email.com';
        
        if (userNameElement) {
            // Mostrar solo el primer nombre si es muy largo
            const firstName = userName.split(' ')[0];
            userNameElement.textContent = firstName.length > 12 ? firstName.substring(0, 12) + '...' : firstName;
        }

        if (userDropdownName) {
            userDropdownName.textContent = userName;
        }

        if (userDropdownEmail) {
            userDropdownEmail.textContent = userEmail;
        }
    }

    setupEventListeners() {
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        const logoutBtn = document.getElementById('logoutBtn');

        // Toggle menú desplegable
        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('show');
            });

            // Cerrar menú al hacer clic fuera
            document.addEventListener('click', (e) => {
                if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
                    userDropdown.classList.remove('show');
                }
            });
        }

        // Logout
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.logout();
            });
        }

        // Enlaces del menú
        this.setupMenuLinks();
    }

    setupMenuLinks() {
        const profileLink = document.getElementById('profileLink');
        const reservationsLink = document.getElementById('reservationsLink');
        const paymentMethodsLink = document.getElementById('paymentMethodsLink');

        if (profileLink) {
            profileLink.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/perfil';
            });
        }

        if (reservationsLink) {
            reservationsLink.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/mis-reservas';
            });
        }

        if (paymentMethodsLink) {
            paymentMethodsLink.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/metodos-pago';
            });
        }
    }

    logout() {
        // Limpiar localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_type');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_email');
        localStorage.removeItem('user_name');
        localStorage.removeItem('pending_reservation');

        // Redirigir al home
        window.location.href = '/';
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new UserMenu();
    });
} else {
    new UserMenu();
}
