document.addEventListener('DOMContentLoaded', function () {
    const documentoContainers = document.querySelectorAll('.documento-container');

    documentoContainers.forEach(container => {
        // --- Referencias a elementos ---
        const abrirIcon = container.querySelector('.container-abri .icon');
        const fileInputContainer = container.querySelector('.file-input-container');
        const uploadArea = container.querySelector('.custom-upload-area');

        // Si no hay área de carga (ej. documento ya aceptado), saltamos este ciclo
        if (!uploadArea) {
            // Aún así, permitimos abrir/cerrar el acordeón si existe el icono
            if (abrirIcon && fileInputContainer) {
                fileInputContainer.classList.remove('show');
                abrirIcon.addEventListener('click', function () {
                    fileInputContainer.classList.toggle('show');
                    this.classList.toggle('rotated');
                });
            }
            return;
        }

        const uploadContent = container.querySelector('.upload-content');
        const fileInfo = container.querySelector('.file-info');
        const fileName = container.querySelector('.file-name');
        const fileSize = container.querySelector('.file-size');
        const fileRemove = container.querySelector('.file-remove');
        const fileInput = container.querySelector('input[type="file"]');

        let currentFile = null;

        // --- 1. Lógica del Acordeón ---
        if (abrirIcon && fileInputContainer) {
            fileInputContainer.style.display = 'block';
            fileInputContainer.classList.remove('show');

            abrirIcon.addEventListener('click', function () {
                fileInputContainer.classList.toggle('show');
                this.classList.toggle('rotated');
            });
        }

        // --- 2. Funciones Drag & Drop (Arrastrar y Soltar) ---

        // Prevenir comportamiento por defecto
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Efectos visuales (Highlight)
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            uploadArea.classList.add('dragover');
        }

        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }

        // --- MANEJO DEL DROP (AQUÍ ESTÁ LA CORRECCIÓN) ---
        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length === 0) return;

            const file = files[0];

            // Validar PDF antes de procesar
            if (file.type !== 'application/pdf') {
                alert('Por favor, sube solo archivos PDF.');
                return;
            }

            // *** LA LÍNEA MÁGICA ***
            // Asignamos el archivo arrastrado al input real del formulario
            if (fileInput) {
                fileInput.files = files;
            }

            // Actualizamos la vista
            processFile(file);
        }

        // --- MANEJO DEL CLIC (Selección manual) ---
        if (fileInput) {
            fileInput.addEventListener('change', handleFileSelect, false);
        }

        function handleFileSelect(e) {
            const files = e.target.files;
            if (files.length === 0) return;

            const file = files[0];

            // Si el usuario selecciona algo que no es PDF manualmente
            if (file.type !== 'application/pdf') {
                alert('Por favor, sube solo archivos PDF.');
                fileInput.value = ''; // Limpiar input
                return;
            }

            processFile(file);
        }

        // --- Procesar y Mostrar Info ---
        function processFile(file) {
            currentFile = file;
            displayFileInfo(file);
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        function displayFileInfo(file) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);

            uploadContent.style.display = 'none';
            fileInfo.style.display = 'flex';
            uploadArea.classList.add('has-file');
        }

        // --- Eliminar Archivo ---
        if (fileRemove) {
            fileRemove.addEventListener('click', (e) => {
                e.preventDefault(); // Evita que se abra el selector de archivos
                e.stopPropagation();

                currentFile = null;
                if (fileInput) fileInput.value = ''; // Limpia el input real

                fileInfo.style.display = 'none';
                uploadContent.style.display = 'flex';
                uploadArea.classList.remove('has-file');
            });
        }
    });
});
function toggleAll(source) {
    checkboxes = document.getElementsByClassName('egresado-checkbox');
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
}