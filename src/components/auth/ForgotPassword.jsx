import React, { useState, useEffect } from 'react';

const ForgotPassword = ({ onLoginClick }) => {
  const [identifier, setIdentifier] = useState('');

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

  //Conectar con endpoint de recuperación de contraseña
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Solicitud de recuperación para:', identifier);
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
      height: '100vh',
      width: '100vw',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: "'Abhaya Libre', serif",
      letterSpacing: '0.005em',
      margin: 0,
      padding: 0,
      overflow: 'hidden'
    },
    card: {
      backgroundColor: '#ffffff',
      borderRadius: '10px',
      padding: '3rem',
      width: '450px',
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
      color: '#000000'
    },
    btnSubmit: {
      background: `linear-gradient(to right, ${themeColors.primary}, ${themeColors.secondary})`,
      border: 'none',
      borderRadius: '10px',
      padding: '0.8rem',
      color: 'white',
      fontWeight: 'bold',
      fontSize: '1.1rem',
      marginTop: '1.5rem',
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
        <h1 style={{ fontWeight: '800', marginBottom: '2rem', fontSize: '2.2rem' }}>
          Recuperar contraseña
        </h1>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="mb-3" style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '0.85rem', color: '#6c757d', marginBottom: '0.4rem' }}>
              Email o número de teléfono
            </label>
            <input
              type="text"
              name="identifier"
              placeholder="tu@correo.com o +52 555 000 0000"
              style={styles.inputField}
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn-hover" style={styles.btnSubmit}>
            Enviar código
          </button>

          <button 
            type="button" 
            className="btn-hover" 
            style={styles.btnLink}
            onClick={onLoginClick}
          >
            Volver a iniciar sesión
          </button>
        </form>

        <div style={{ marginTop: '2.5rem', textAlign: 'center', fontSize: '0.75rem', color: '#000000' }}>
          Derechos reservados 2026 | Cuidado con el pug
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;