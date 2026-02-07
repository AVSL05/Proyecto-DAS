import React, { useState, useEffect } from 'react';

const Register = ({ onLoginClick }) => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: ''
  });

  useEffect(() => {
    window.history.pushState(null, null, window.location.pathname);
    const handleBackButton = (e) => {
      e.preventDefault();
      onLoginClick();
    };
    window.addEventListener('popstate', handleBackButton);
    return () => {
      window.removeEventListener('popstate', handleBackButton);
    };
  }, [onLoginClick]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // TODO: Conectar con endpoint de registro
  const handleRegister = (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      alert("Las contraseñas no coinciden");
      return;
    }
    
    console.log('Datos de registro para backend:', formData);
  };

  const themeColors = {
    primary: '#5715EB',
    secondary: '#3575F6',
    accent: '#9D15EB',
    textLink: '#4547B2',
    border: '#6366EB'
  };

  const styles = {
    wrapper: {
      background: `linear-gradient(135deg, ${themeColors.secondary} 0%, ${themeColors.primary} 50%, ${themeColors.accent} 100%)`,
      minHeight: '100vh',
      width: '100vw',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: "'Abhaya Libre', serif",
      letterSpacing: '0.005em',
      margin: 0,
      padding: '20px',
      boxSizing: 'border-box',
      overflow: 'hidden'
    },
    card: {
      backgroundColor: '#ffffff',
      borderRadius: '10px',
      padding: '2rem 2.5rem',
      width: '100%',
      maxWidth: '450px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.25)',
      display: 'flex',
      flexDirection: 'column'
    },
    inputField: {
      borderRadius: '10px',
      padding: '0.75rem',
      border: '1px solid #ced4da',
      fontSize: '1rem',
      backgroundColor: '#f0f5ff',
      color: '#000000',
      width: '100%',
      boxSizing: 'border-box'
    },
    btnSubmit: {
      background: `linear-gradient(to right, ${themeColors.primary}, ${themeColors.secondary})`,
      border: 'none',
      borderRadius: '10px',
      padding: '0.8rem',
      color: 'white',
      fontWeight: 'bold',
      fontSize: '1.1rem',
      marginTop: '1rem',
      cursor: 'pointer'
    },
    btnLink: {
      backgroundColor: 'transparent',
      border: `2px solid ${themeColors.border}`,
      color: themeColors.border,
      borderRadius: '10px',
      padding: '0.8rem',
      fontWeight: 'bold',
      marginTop: '1rem',
      cursor: 'pointer'
    }
  };

  return (
    <div style={styles.wrapper}>
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Abhaya+Libre:wght@800&display=swap');
          
          * {
            box-sizing: border-box;
          }
          
          body {
            overflow-x: hidden;
          }
          
          input, input:focus {
            color: #000000 !important;
            background-color: #f0f5ff !important;
            outline: none;
            border-color: #ced4da;
          }
          
          input::placeholder {
            color: #6c757d !important;
            opacity: 1 !important;
          }

          input:-webkit-autofill,
          input:-webkit-autofill:hover,
          input:-webkit-autofill:focus {
            -webkit-text-fill-color: #000000 !important;
            -webkit-box-shadow: 0 0 0px 1000px #f0f5ff inset !important;
          }

          .btn-hover:hover {
            opacity: 0.9;
            transform: scale(1.02);
            transition: all 0.2s ease;
          }
        `}
      </style>

      <div style={styles.card}>
        <span style={{ color: '#6c757d', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
          Cuidado con el pug
        </span>
        <h1 style={{ fontWeight: '800', marginBottom: '1rem', fontSize: '2rem' }}>
          Crear cuenta
        </h1>

        <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="mb-2 d-flex flex-column">
            <label style={{ fontSize: '0.85rem', color: '#6c757d', marginBottom: '0.3rem' }}>Ingresar nombre</label>
            <input
              type="text"
              name="fullName"
              placeholder="Nombre"
              style={styles.inputField}
              value={formData.fullName}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-2 d-flex flex-column">
            <label style={{ fontSize: '0.85rem', color: '#6c757d', marginBottom: '0.3rem' }}>Email</label>
            <input
              type="email"
              name="email"
              placeholder="tu@correo.com"
              style={styles.inputField}
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-2 d-flex flex-column">
            <label style={{ fontSize: '0.85rem', color: '#6c757d', marginBottom: '0.3rem' }}>Num. de teléfono</label>
            <input
              type="tel"
              name="phone"
              placeholder="+52 (555) 000-0000"
              style={styles.inputField}
              value={formData.phone}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-2 d-flex flex-column">
            <label style={{ fontSize: '0.85rem', color: '#6c757d', marginBottom: '0.3rem' }}>Contraseña</label>
            <input
              type="password"
              name="password"
              placeholder="........"
              style={styles.inputField}
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-3 d-flex flex-column">
            <label style={{ fontSize: '0.85rem', color: '#6c757d', marginBottom: '0.3rem' }}>Confirmar contraseña</label>
            <input
              type="password"
              name="confirmPassword"
              placeholder="........"
              style={styles.inputField}
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className="btn-hover" style={styles.btnSubmit}>
            Registrarse
          </button>

          <button 
            type="button" 
            className="btn-hover" 
            style={styles.btnLink}
            onClick={onLoginClick}
          >
            ¿Ya tienes una cuenta? Iniciar sesión
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.75rem', color: '#000000' }}>
          Derechos reservados 2026 | Cuidado con el pug
        </div>
      </div>
    </div>
  );
};

export default Register;