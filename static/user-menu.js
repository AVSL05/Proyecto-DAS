// Sistema de menú de usuario
class UserMenu {
    constructor() {
        console.log("🏗️ Construyendo UserMenu...");
        this.token = localStorage.getItem('access_token');
        this.userInfo = null;
        this.init();
    }

    async init() {
        console.log("⚙️ Inicializando UserMenu...");
        await this.checkAuthStatus();
        this.setupEventListeners();
        console.log("✅ UserMenu inicializado correctamente");
    }

    async checkAuthStatus() {
        console.log("🔍 Verificando estado de autenticación...");
        console.log("🎫 Token:", this.token ? "Existe" : "No existe");
        
        const loginBtn = document.getElementById('loginBtn');
        const userMenuContainer = document.getElementById('userMenuContainer');
        
        console.log("🔘 loginBtn:", loginBtn ? "Encontrado" : "NO encontrado");
        console.log("📦 userMenuContainer:", userMenuContainer ? "Encontrado" : "NO encontrado");

        if (!this.token) {
            // No hay sesión - mostrar botón de login
            console.log("❌ No hay token - mostrando botón de login");
            if (loginBtn) loginBtn.style.display = 'inline-block';
            if (userMenuContainer) userMenuContainer.style.display = 'none';
            return;
        }

        // Hay token - verificar y obtener info del usuario
        console.log("✅ Token encontrado - verificando con API...");
        try {
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                console.error("❌ API respondió con error:", response.status);
                throw new Error('Token inválido');
            }

            this.userInfo = await response.json();
            console.log("👤 Usuario obtenido:", this.userInfo);
            
            // Guardar info del usuario
            localStorage.setItem('user_email', this.userInfo.email || '');
            localStorage.setItem('user_name', this.userInfo.full_name || this.userInfo.email || 'Usuario');
            localStorage.setItem('user_role', this.userInfo.role || 'cliente');

            // Mostrar menú de usuario
            console.log("✅ Mostrando menú de usuario");
            if (loginBtn) {
                loginBtn.style.display = 'none';
                console.log("🔘 Botón login ocultado");
            }
            if (userMenuContainer) {
                userMenuContainer.style.display = 'flex';
                console.log("📦 Menu de usuario mostrado");
                this.updateUserInfo();
                this.updateAdminAccess();
            }
        } catch (error) {
            console.error('❌ Error al verificar sesión:', error);
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

    updateAdminAccess() {
        const userRole = localStorage.getItem('user_role') || 'cliente';
        const adminPanelItem = document.getElementById('adminPanelItem');
        const adminDivider = document.getElementById('adminDivider');
        
        // Mostrar botón de panel admin solo si el usuario es administrador
        if (userRole === 'administrativo') {
            if (adminPanelItem) adminPanelItem.style.display = 'block';
            if (adminDivider) adminDivider.style.display = 'block';
        } else {
            if (adminPanelItem) adminPanelItem.style.display = 'none';
            if (adminDivider) adminDivider.style.display = 'none';
        }
    }

    setupEventListeners() {
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        const logoutBtn = document.getElementById('logoutBtn');
        const profileLink = document.getElementById('profileLink');
        const reservationsLink = document.getElementById('reservationsLink');
        const paymentMethodsLink = document.getElementById('paymentMethodsLink');
        const adminPanelLink = document.getElementById('adminPanelLink');

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

        if (adminPanelLink) {
            adminPanelLink.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/admin';
            });
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }
    }

    logout() {
        console.log("🚪 Cerrando sesión...");
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
console.log("📜 user-menu.js cargado");
if (document.readyState === 'loading') {
    console.log("⏳ DOM aún cargando, esperando DOMContentLoaded...");
    document.addEventListener('DOMContentLoaded', () => {
        console.log("✅ DOMContentLoaded - Inicializando UserMenu");
        new UserMenu();
    });
} else {
    console.log("✅ DOM ya listo - Inicializando UserMenu");
    new UserMenu();
}
