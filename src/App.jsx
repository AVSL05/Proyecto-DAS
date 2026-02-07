import React, { useState } from 'react';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ForgotPassword from './components/auth/ForgotPassword';
import AdminHome from './components/admin/AdminHome';
import Vehiculos from './components/admin/Vehiculos';

function App() {
  const [view, setView] = useState('login');
  // eslint-disable-next-line no-unused-vars
  const [userType, setUserType] = useState(null);

  // Esta función maneja la lógica de autenticación mock
  const handleLogin = (email, password) => {
    const mockUsers = {
      'user@test.com': { type: 'user', password: '123' },
      'admin@test.com': { type: 'admin', password: '123' }
    };

    const user = mockUsers[email];
    
    if (user && user.password === password) {
      setUserType(user.type);
      setView(user.type === 'admin' ? 'adminHome' : 'userDashboard');
    } else {
      alert('Credenciales incorrectas');
    }
  };

  const handleLogout = () => {
    setUserType(null);
    setView('login');
  };

  const handleAdminNavigate = (section) => {
    setView(section);
  };

  const handleBackToAdminHome = () => {
    setView('adminHome');
  };

  const handleRegisterClick = () => setView('register');
  const handleLoginClick = () => setView('login');
  const handleForgotPasswordClick = () => setView('forgotPassword');

  return (
    <div className="App">
      {view === 'login' && (
        <Login 
          onRegisterClick={handleRegisterClick}
          onForgotPasswordClick={handleForgotPasswordClick}
          onLogin={handleLogin}
        />
      )}
      
      {view === 'register' && (
        <Register onLoginClick={handleLoginClick} />
      )}

      {view === 'forgotPassword' && (
        <ForgotPassword onLoginClick={handleLoginClick} />
      )}

      {view === 'userDashboard' && (
        <div>
          <h1>Dashboard de Usuario</h1>
          <p>Tipo de usuario: {userType}</p>
          <button onClick={handleLogout}>Cerrar Sesión</button>
        </div>
      )}

      {view === 'adminHome' && (
        <AdminHome 
          onLogout={handleLogout}
          onNavigate={handleAdminNavigate}
        />
      )}

      {view === 'vehiculos' && (
        <Vehiculos onBack={handleBackToAdminHome} />
      )}
    </div>
  );
}

export default App;