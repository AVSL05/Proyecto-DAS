import React, { useState } from 'react';

const AdminHome = ({ onLogout, onNavigate }) => {
  const [activeSection, setActiveSection] = useState('home');

  const themeColors = {
    primary: '#5715EB',
    secondary: '#3575F6',
    accent: '#9D15EB',
    textLink: '#4547B2',
    lightBlue: '#15A0EB',
    border: '#6366EB'
  };

  const styles = {
    container: {
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f5f5f5',
      fontFamily: "'Abhaya Libre', serif",
      letterSpacing: '0.005em',
      overflow: 'hidden',
      margin: 0,
      padding: 0
    },
    header: {
      background: `linear-gradient(to right, ${themeColors.secondary}, ${themeColors.primary})`,
      color: 'white',
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      width: '100%',
      boxSizing: 'border-box'
    },
    logo: {
      fontSize: '1.5rem',
      fontWeight: '800'
    },
    nav: {
      display: 'flex',
      gap: '1.5rem'
    },
    navButton: {
      backgroundColor: 'transparent',
      border: 'none',
      color: 'white',
      fontSize: '1rem',
      fontWeight: '800',
      cursor: 'pointer',
      padding: '0.5rem 1rem',
      borderRadius: '10px',
      transition: 'all 0.3s ease'
    },
    navButtonActive: {
      backgroundColor: 'rgba(255, 255, 255, 0.2)',
      transform: 'scale(1.05)'
    },
    content: {
      flex: 1,
      padding: '2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: '100%',
      boxSizing: 'border-box'
    },
    welcomeCard: {
      backgroundColor: 'white',
      borderRadius: '15px',
      padding: '4rem',
      width: '90%', 
      maxWidth: '1400px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
      textAlign: 'center'
    },
    menuGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)', 
      gap: '2rem',
      marginTop: '3rem'
    },
    menuCard: {
      background: `linear-gradient(135deg, ${themeColors.secondary}, ${themeColors.primary})`,
      borderRadius: '12px',
      padding: '3rem 1rem',
      color: 'white',
      cursor: 'pointer',
      transition: 'all 0.3s ease'
    },
    footer: {
      padding: '1rem',
      textAlign: 'center',
      backgroundColor: 'white',
      borderTop: '1px solid #e0e0e0',
      width: '100%'
    }
  };

  const menuItems = [
    { id: 'vehiculos', title: 'Vehículos', icon: '🚐' },
    { id: 'calendario', title: 'Calendario', icon: '📅' },
    { id: 'cotizaciones', title: 'Cotizaciones', icon: '📝' },
    { id: 'finanzas', title: 'Finanzas', icon: '💰' }
  ];

  const handleMenuClick = (sectionId) => {
    setActiveSection(sectionId);
    if (onNavigate) onNavigate(sectionId);
  };

  return (
    <div style={styles.container}>
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Abhaya+Libre:wght@800&display=swap');
          .menu-card:hover { transform: translateY(-10px); shadow: 0 8px 30px rgba(0,0,0,0.2); }
        `}
      </style>
      <header style={styles.header}>
        <div style={styles.logo}>Cuidado con el Pug</div>
        <nav style={styles.nav}>
          {menuItems.map(item => (
            <button 
              key={item.id} 
              style={{...styles.navButton, ...(activeSection === item.id ? styles.navButtonActive : {})}}
              onClick={() => handleMenuClick(item.id)}
            >
              {item.title}
            </button>
          ))}
        </nav>
        <div onClick={onLogout} style={{cursor: 'pointer'}}>Cerrar Sesión</div>
      </header>
      <main style={styles.content}>
        <div style={styles.welcomeCard}>
          <h1 style={{fontSize: '3rem', color: themeColors.primary}}>Panel de Administración</h1>
          <div style={styles.menuGrid}>
            {menuItems.map(item => (
              <div key={item.id} className="menu-card" style={styles.menuCard} onClick={() => handleMenuClick(item.id)}>
                <div style={{fontSize: '3.5rem'}}>{item.icon}</div>
                <div style={{fontSize: '1.5rem', fontWeight: '800'}}>{item.title}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
      <footer style={styles.footer}>Derechos reservados Cuidado con el pug 2026</footer>
    </div>
  );
};

export default AdminHome;