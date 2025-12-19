let html5QrCode;
let isScanning = false;

function activarCamara() {
    const readerDiv = document.getElementById('reader');
    if (!readerDiv) return;

    if (isScanning) {
        detenerCamara();
        return;
    }

    readerDiv.style.display = 'block';

    // Configuración para leer códigos de barra (EAN) y QR
    html5QrCode = new Html5Qrcode("reader", {
        formatsToSupport: [Html5QrcodeSupportedFormats.EAN_13, Html5QrcodeSupportedFormats.CODE_128],
        verbose: false
    });

    isScanning = true;

    const config = {
        fps: 20,
        qrbox: { width: 300, height: 150 }, // Rectángulo horizontal para códigos de barra
        aspectRatio: 1.0
    };

    html5QrCode.start(
        { facingMode: "environment" },
        config,
        (decodedText) => {
            // Pausar para procesar
            html5QrCode.pause();

            // Sonido/Vibración
            if (navigator.vibrate) navigator.vibrate(100);

            // 3. Enviar a Django
            agregarProductoAjax(decodedText);
        }
    ).catch(err => {
        console.error(err);
        alert("Error al iniciar cámara. Verifica permisos y HTTPS.");
    });
}

function agregarProductoAjax(codigo) {
    fetch(`/carrito/agregar-ajax/${codigo}/`, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(response => {
            if (response.status === 404) throw new Error('Producto no encontrado');
            if (response.status === 400) throw new Error('Sin stock');
            if (!response.ok) throw new Error('Error en el servidor');
            return response.json();
        })
        .then(data => {
            if (data.status === 'ok') {
                // Notificación rápida de éxito
                mostrarNotificacion(`Producto agregado al carrito`, "success");

                // Actualizar el carrito dinámicamente recargando solo esa sección
                fetch(window.location.href)
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const nuevoCarrito = doc.getElementById('carrito-container').innerHTML;
                        document.getElementById('carrito-container').innerHTML = nuevoCarrito;
                    });

                // Reanudar escaneo rápido
                setTimeout(() => html5QrCode.resume(), 1000);
            }
        })
        .catch(error => {
            mostrarNotificacion(error.message, "danger");
            setTimeout(() => html5QrCode.resume(), 2000); // Reanuda tras error
        });
}

function detenerCamara() {
    if (html5QrCode) {
        html5QrCode.stop().then(() => {
            document.getElementById('reader').style.display = 'none';
            isScanning = false;
        });
    }
}

function mostrarNotificacion(mensaje, tipo) {
    const notyf = new Notyf({
        duration: 3000,
        position: { x: "center", y: "top" }
    });

    if (tipo === 'success') {
        notyf.success(mensaje);
    } else if (tipo === 'danger' || tipo === 'error') {
        notyf.error(mensaje);
    } else {
        notyf.open({ type: 'info', message: mensaje });
    }
}