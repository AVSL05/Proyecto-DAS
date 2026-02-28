// Manejo de la página de perfil
class ProfileManager {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.profileForm = document.getElementById('profileForm');
        this.passwordForm = document.getElementById('passwordForm');
        this.isGoogleUser = false;
        
        if (!this.token) {
            // Redirigir al login si no hay sesión
            window.location.href = '/login';
            return;
        }
        
        this.init();
    }

    async init() {
        await this.loadUserData();
        this.setupEventListeners();
    }

    async loadUserData() {
        try {
            const response = await fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('No se pudo cargar el perfil');
            }

            const user = await response.json();
            this.populateForm(user);
            
            // Detectar si es usuario de Google (no tiene password_hash)
            // Para esto, necesitamos verificar si es Google user
            // Por ahora asumimos que si no hay contraseña guardada en backend
            
        } catch (error) {
            console.error('Error cargando perfil:', error);
            this.showMessage('profileMessage', 'No se pudo cargar tu perfil. Por favor, intenta de nuevo.', 'error');
            
            // Si hay error de autenticación, redirigir al login
            if (error.message.includes('401') || error.message.includes('autenticación')) {
                setTimeout(() => {
                    localStorage.clear();
                    window.location.href = '/login';
                }, 2000);
            }
        }
    }

    populateForm(user) {
        document.getElementById('fullName').value = user.full_name || '';
        document.getElementById('email').value = user.email || '';
        document.getElementById('phone').value = user.phone || '';
        document.getElementById('role').value = user.role === 'administrativo' ? 'Administrativo' : 'Cliente';
        
        // Guardar email para uso posterior
        localStorage.setItem('user_email', user.email || '');
        localStorage.setItem('user_name', user.full_name || user.email || 'Usuario');
    }

    setupEventListeners() {
        // Formulario de perfil
        if (this.profileForm) {
            this.profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateProfile();
            });
        }

        // Formulario de cambio de contraseña
        if (this.passwordForm) {
            this.passwordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.changePassword();
            });
        }
    }

    async updateProfile() {
        const saveBtn = document.getElementById('saveProfileBtn');
        const originalText = saveBtn.textContent;
        
        try {
            saveBtn.disabled = true;
            saveBtn.textContent = 'Guardando...';
            
            const formData = new FormData(this.profileForm);
            const data = {
                full_name: formData.get('full_name'),
                phone: formData.get('phone')
            };

            const response = await fetch('/api/auth/me', {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Error al actualizar el perfil');
            }

            // Actualizar localStorage
            localStorage.setItem('user_name', result.full_name || 'Usuario');
            
            this.showMessage('profileMessage', '✅ Perfil actualizado correctamente', 'success');
            
            // Actualizar la interfaz del menú de usuario
            if (window.location.reload) {
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
            
        } catch (error) {
            console.error('Error actualizando perfil:', error);
            this.showMessage('profileMessage', `❌ ${error.message}`, 'error');
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = originalText;
        }
    }

    async changePassword() {
        const changeBtn = document.getElementById('changePasswordBtn');
        const originalText = changeBtn.textContent;
        
        try {
            changeBtn.disabled = true;
            changeBtn.textContent = 'Cambiando...';
            
            const formData = new FormData(this.passwordForm);
            const newPassword = formData.get('new_password');
            const confirmPassword = formData.get('confirm_password');
            
            // Validación frontend
            if (newPassword !== confirmPassword) {
                throw new Error('Las contraseñas nuevas no coinciden');
            }
            
            if (newPassword.length < 8) {
                throw new Error('La contraseña debe tener al menos 8 caracteres');
            }
            
            if (newPassword.match(/^[a-zA-Z]+$/) || newPassword.match(/^[0-9]+$/)) {
                throw new Error('La contraseña debe incluir letras y números');
            }

            const data = {
                current_password: formData.get('current_password'),
                new_password: newPassword,
                confirm_password: confirmPassword
            };

            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Error al cambiar la contraseña');
            }

            this.showMessage('passwordMessage', '✅ Contraseña actualizada correctamente', 'success');
            
            // Limpiar el formulario
            this.passwordForm.reset();
            
        } catch (error) {
            console.error('Error cambiando contraseña:', error);
            this.showMessage('passwordMessage', `❌ ${error.message}`, 'error');
        } finally {
            changeBtn.disabled = false;
            changeBtn.textContent = originalText;
        }
    }

    showMessage(elementId, message, type) {
        const messageEl = document.getElementById(elementId);
        if (!messageEl) return;
        
        messageEl.textContent = message;
        messageEl.className = `payment-message ${type}`;
        messageEl.hidden = false;
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            messageEl.hidden = true;
        }, 5000);
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ProfileManager();
    });
} else {
    new ProfileManager();
}
