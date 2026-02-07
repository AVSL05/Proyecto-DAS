import React, { useState, useEffect } from 'react';

const Vehiculos = ({ onBack }) => {

  useEffect(() => {
    window.history.pushState(null, null, window.location.pathname);
    const handlePopState = () => onBack();
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [onBack]);

  const [vehiculos] = useState([
    { id: 1, nombre: 'Mercedez Sprint', imagen: '/src/images/mer.jpg', kmRestantes: 850 },
    { id: 2, nombre: 'Chevrolet Silverado', imagen: '/src/images/silverado.jpg', kmRestantes: 250 }
  ]);

  const [selectedVehicle, setSelectedVehicle] = useState(vehiculos[0]);
  const [showCalendar, setShowCalendar] = useState(false);

  const themeColors = { primary: '#5715EB', secondary: '#3575F6' };

  const styles = {
    container: {
      width: '100vw',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f5f5f5',
      fontFamily: "'Abhaya Libre', serif",
      overflow: 'hidden'
    },
    header: {
      background: `linear-gradient(to right, ${themeColors.secondary}, ${themeColors.primary})`,
      color: 'white',
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      position: 'sticky',
      top: 0,
      zIndex: 1000
    },
    content: {
      flex: 1,
      display: 'flex',
      padding: '2rem',
      gap: '2rem',
      overflowY: 'auto'
    },
    leftSection: {
      flex: '0 0 30%',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    },
    rightSection: {
      flex: 1,
      backgroundColor: 'white',
      borderRadius: '15px',
      padding: '3rem',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
    },
    vehicleCard: {
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '1rem',
      cursor: 'pointer',
      transition: '0.3s'
    },
    kmCircle: {
      width: '250px',
      height: '250px',
      borderRadius: '50%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '2rem',
      fontWeight: '800',
      marginBottom: '2rem'
    },
    statusIcons: {
      display: 'flex',
      gap: '3rem',
      marginTop: '2rem'
    },
    buttonCalendarContainer: {
      position: 'relative',
      width: '100%',
      maxWidth: '400px',
      marginTop: '3rem'
    },
    calendarPopup: {
      position: 'absolute',
      left: '100%',
      top: 0,
      marginLeft: '20px',
      backgroundColor: 'white',
      borderRadius: '10px',
      padding: '20px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
      width: '260px',
      zIndex: 999
    },
    agendarButton: {
      padding: '1.2rem 3rem',
      background: `linear-gradient(to right, ${themeColors.secondary}, ${themeColors.primary})`,
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      fontWeight: '800',
      cursor: 'pointer',
      fontSize: '1.2rem',
      width: '100%'
    }
  };

  const handleAgendarClick = () => {
    setShowCalendar(true);
  };

  const handleDateChange = (e) => {
    alert(`Cita agendada para: ${e.target.value}`);
    setShowCalendar(false);
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={{ fontSize: '1.5rem', fontWeight: '800' }}>Cuidado con el Pug</div>
        <div onClick={onBack} style={{ cursor: 'pointer', background: 'white', borderRadius: '50%', padding: '8px' }}>
          👤
        </div>
      </header>

      <div style={styles.content}>
        <div style={styles.leftSection}>
          <h2>Vehículos</h2>
          {vehiculos.map(v => (
            <div
              key={v.id}
              onClick={() => setSelectedVehicle(v)}
              style={{
                ...styles.vehicleCard,
                border: selectedVehicle.id === v.id
                  ? `4px solid ${themeColors.primary}`
                  : '1px solid #ddd'
              }}
            >
              <img src={v.imagen} alt={v.nombre} style={{ width: '100%', borderRadius: '8px' }} />
              <p style={{ fontWeight: '800' }}>{v.nombre}</p>
            </div>
          ))}
        </div>

        <div style={styles.rightSection}>
          <h2>{selectedVehicle.nombre}</h2>

          <div
            style={{
              ...styles.kmCircle,
              border: `12px solid ${selectedVehicle.kmRestantes > 500 ? '#4CAF50' : '#FF9800'}`
            }}
          >
            {selectedVehicle.kmRestantes} km
            <div style={{ fontSize: '1rem', color: '#666' }}>restantes</div>
          </div>

          <div style={styles.statusIcons}>
            {['🔋', '⚙️', '⛽'].map(icon => (
              <div key={icon} style={{ fontSize: '2.5rem' }}>{icon}</div>
            ))}
          </div>

          <div style={styles.buttonCalendarContainer}>
            <button onClick={handleAgendarClick} style={styles.agendarButton}>
              Agendar mantenimiento
            </button>

            {showCalendar && (
              <div style={styles.calendarPopup}>
                <p style={{ fontWeight: 'bold', color: themeColors.primary, marginBottom: '10px' }}>
                  Selecciona la fecha
                </p>

                <input
                  type="date"
                  onChange={handleDateChange}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '6px',
                    border: '1px solid #ccc',
                    fontSize: '1rem',
                    marginBottom: '15px'
                  }}
                />

                <button
                  onClick={() => setShowCalendar(false)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: themeColors.primary,
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  Cerrar
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <footer style={{ padding: '1rem', textAlign: 'center', backgroundColor: 'white' }}>
        Derechos reservados 2026
      </footer>
    </div>
  );
};

export default Vehiculos;
