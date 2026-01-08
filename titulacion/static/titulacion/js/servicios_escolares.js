function toggleAll(source) {
    checkboxes = document.getElementsByClassName('egresado-checkbox');
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
};
function toggleNotes(docId, isAccepting) {
    // Buscamos todos los checkboxes que tengan el nombre relacionado a ese docId
    const checkboxes = document.querySelectorAll(`input[name="notas_${docId}"]`);

    checkboxes.forEach(cb => {
        if (isAccepting) {
            // 1. Desmarcar el checkbox
            cb.checked = false;
            // 2. Bloquear el checkbox
            cb.disabled = true;
            // 3. (Opcional) Cambiar apariencia para que se vea bloqueado
            cb.parentElement.style.opacity = "0.5";
            cb.parentElement.style.cursor = "not-allowed";
        } else {
            // Si es rechazar, habilitamos todo de nuevo
            cb.disabled = false;
            cb.parentElement.style.opacity = "1";
            cb.parentElement.style.cursor = "pointer";
        }
    });
}

// Opcional: Ejecutar al cargar la página por si ya hay selecciones previas
document.addEventListener("DOMContentLoaded", function () {
    // Esto es por si la página se recarga y Django dejó marcados los radios
    const radios = document.querySelectorAll('input[type="radio"]:checked');
    radios.forEach(radio => {
        const docId = radio.name.split('_')[1];
        const isAccepting = (radio.value !== 'rechazado');
        toggleNotes(docId, isAccepting);
    });
});