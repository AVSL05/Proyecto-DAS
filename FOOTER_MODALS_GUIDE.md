# Guía para Editar el Contenido de los Modales del Footer

Los enlaces del footer ("Términos y Condiciones", "Información Legal" y "Aviso de Privacidad") ahora abren un modal con contenido personalizable.

## Cómo Editar el Contenido

El contenido de los tres modales se encuentra en el archivo: **`static/footer-modals.js`**

### Estructura del archivo

El archivo contiene un objeto llamado `footerModalContent` con tres secciones:

```javascript
const footerModalContent = {
  terminos: {
    title: "Términos y Condiciones",
    content: `...tu contenido aquí...`,
  },
  legal: {
    title: "Información Legal",
    content: `...tu contenido aquí...`,
  },
  privacidad: {
    title: "Aviso de Privacidad",
    content: `...tu contenido aquí...`,
  },
};
```

### Para Editar el Contenido

1. Abre el archivo `static/footer-modals.js`
2. Busca la sección que quieres editar (`terminos`, `legal` o `privacidad`)
3. Reemplaza el contenido dentro de las comillas invertidas (` `` `)
4. Guarda el archivo

### Formato del Contenido

Puedes usar HTML básico dentro del contenido:

- **Párrafos**: `<p>Tu texto aquí</p>`
- **Títulos**: `<h3>Título de sección</h3>`
- **Listas**:
  ```html
  <ul>
    <li>Punto 1</li>
    <li>Punto 2</li>
  </ul>
  ```
- **Negritas**: `<strong>Texto en negrita</strong>`
- **Enlaces**: `<a href="url">Texto del enlace</a>`

### Ejemplo de Contenido

```javascript
'terminos': {
    title: 'Términos y Condiciones',
    content: `
        <p><strong>Última actualización: 27 de febrero de 2026</strong></p>

        <h3>1. Aceptación de los Términos</h3>
        <p>Al acceder y utilizar este servicio, usted acepta estar sujeto a estos términos y condiciones.</p>

        <h3>2. Uso del Servicio</h3>
        <p>El servicio de renta de vehículos está disponible para:</p>
        <ul>
            <li>Personas mayores de 18 años</li>
            <li>Con licencia de conducir vigente</li>
            <li>Que cumplan con los requisitos establecidos</li>
        </ul>

        <h3>3. Responsabilidades</h3>
        <p>El usuario es responsable de...</p>
    `
}
```

### Archivos Modificados

Los siguientes archivos fueron actualizados con el sistema de modales:

- `static/index.html`
- `static/perfil.html`
- `static/mis-reservas.html`
- `static/metodos-pago.html`
- `static/payment.html`
- `static/styles.css` (estilos del modal)
- `static/footer-modals.js` (contenido y funcionalidad)

### Características del Modal

- ✅ Se abre al hacer clic en los enlaces del footer
- ✅ Se puede cerrar con:
  - El botón X
  - Haciendo clic fuera del modal
  - Presionando la tecla ESC
- ✅ Diseño responsive (se adapta a móviles)
- ✅ Scroll interno si el contenido es muy largo
- ✅ Los tres enlaces usan el mismo modal pero con diferente contenido

## Notas Importantes

- No elimines las comillas invertidas (` `` `) que rodean el contenido
- Mantén la estructura del objeto JavaScript
- Si usas comillas dentro del contenido, usa comillas dobles (`"`) o escapa las comillas simples (`\'`)
- Guarda el archivo después de hacer cambios
