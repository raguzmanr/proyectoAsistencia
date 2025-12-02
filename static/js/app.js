const app = {
    apiBase: '/api',
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),

    init: async () => {
        if (app.token) {
            await app.loadUserProfile();
        }
        app.setupNavigation();
        app.checkAuth();
    },

    setupNavigation: () => {
        // Initial view based on auth
        if (app.token) {
            app.navigate('dashboard');
        } else {
            app.navigate('home');
        }
    },

    checkAuth: () => {
        const userDisplay = document.getElementById('user-display');
        const authButtons = document.getElementById('auth-buttons');
        const navLinks = document.getElementById('navLinks');

        // Base links
        let linksHtml = `
            <button class="btn btn-text" onclick="app.navigate('home')">Inicio</button>
            <button class="btn btn-text" onclick="app.navigate('catalog')">Servicios</button>
        `;

        if (app.token && app.user) {
            // Logged in
            if (userDisplay) userDisplay.innerHTML = `Hola, ${app.user.username} <span class="badge badge-segment" style="margin-left:5px; font-size:0.8em">${app.user.role}</span> <button onclick="app.logout()" class="btn btn-outline" style="margin-left:10px; padding: 5px 10px; font-size: 0.8em;">Salir</button>`;
            if (authButtons) authButtons.style.display = 'none';

            // Add Dashboard link
            linksHtml += `<button class="btn btn-text" onclick="app.navigate('dashboard')">Mi Panel</button>`;
        } else {
            // Guest
            if (userDisplay) userDisplay.innerHTML = '';
            if (authButtons) authButtons.style.display = 'block';
        }

        if (navLinks) navLinks.innerHTML = linksHtml;
    },

    navigate: (viewId) => {
        // Hide all views
        document.querySelectorAll('.view').forEach(el => el.classList.add('hidden'));

        // Show target view
        const target = document.getElementById(`view-${viewId}`);
        if (target) {
            target.classList.remove('hidden');
            target.classList.add('active');
        }

        // Load data if needed
        if (viewId === 'catalog') app.loadServices();
        if (viewId === 'dashboard') app.loadDashboard();
    },

    // Auth Functions
    handleLogin: async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch(`${app.apiBase}/token/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                localStorage.setItem('token', result.access);
                app.token = result.access;

                // Get user details
                await app.loadUserProfile();
                app.navigate('dashboard');
            } else {
                app.showToast('Credenciales inválidas', 'error');
            }
        } catch (error) {
            app.showToast('Error de conexión', 'error');
        }
    },

    handleRegister: async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch(`${app.apiBase}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                app.showToast('Registro exitoso. Por favor inicia sesión.');
                app.navigate('login');
            } else {
                app.showToast('Error en el registro', 'error');
            }
        } catch (error) {
            app.showToast('Error de conexión', 'error');
        }
    },

    loadUserProfile: async () => {
        try {
            const response = await fetch(`${app.apiBase}/users/me/`, {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });
            if (response.ok) {
                const user = await response.json();
                localStorage.setItem('user', JSON.stringify(user));
                app.user = user;
                app.checkAuth();
            } else {
                throw new Error('Failed to load profile');
            }
        } catch (error) {
            console.error('Error loading profile', error);
            app.logout();
        }
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        app.token = null;
        app.user = null;
        app.checkAuth();
        app.navigate('home');

        // Close all modals
        document.querySelectorAll('.modal').forEach(modal => modal.classList.add('hidden'));
    },

    showToast: (message, type = 'success') => {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    },

    // Service Functions
    loadServices: async () => {
        try {
            const response = await fetch(`${app.apiBase}/servicios/`);
            if (response.ok) {
                const services = await response.json();
                app.renderServices(services);

                // Show admin button if applicable
                const adminActions = document.getElementById('admin-actions-catalog');
                if (app.user && app.user.role === 'admin') {
                    adminActions.innerHTML = `<button class="btn btn-primary" onclick="app.openCreateServiceModal()">+ Crear Nuevo Servicio</button>`;
                } else {
                    adminActions.innerHTML = '';
                }
            }
        } catch (error) {
            console.error(error);
            app.showToast('Error cargando servicios', 'error');
        }
    },

    renderServices: (services) => {
        const grid = document.getElementById('services-grid');
        grid.innerHTML = services.map(s => {
            let actionButtons = '';

            if (app.user && app.user.role === 'admin') {
                // Admin: Edit and Delete buttons
                actionButtons = `
                    <div style="display:flex; gap:5px;">
                        <button class="btn btn-outline" style="flex:1" onclick="app.openEditServiceModal(${s.id})">Editar</button>
                        <button class="btn btn-primary" style="flex:1; background:var(--danger); border-color:var(--danger)" onclick="app.deleteService(${s.id})">Eliminar</button>
                    </div>
                `;
            } else if (app.user && app.user.role === 'cliente') {
                // Cliente: Request button
                actionButtons = `<button class="btn btn-primary btn-block" onclick="app.openRequestModal(${s.id})">Solicitar</button>`;
            } else if (app.user && app.user.role === 'empresa') {
                // Empresa: No action buttons (they only manage existing requests)
                actionButtons = '<p style="text-align:center; color:var(--text-muted); font-size:0.9em;">Solo gestión de solicitudes</p>';
            } else {
                // Guest: Prompt to login
                actionButtons = `<button class="btn btn-primary btn-block" onclick="app.navigate('login')">Iniciar Sesión</button>`;
            }

            return `
            <div class="card service-card" data-segment="${s.segmento || 'all'}">
                <div class="service-icon">
                    <i class="fa-solid fa-briefcase"></i>
                </div>
                <h3>${s.nombre}</h3>
                <p>${s.descripcion}</p>
                <div class="price-tag">$${parseFloat(s.tarifa_base).toLocaleString()}</div>
                <span class="badge badge-segment">${s.segmento || 'General'}</span>
                ${actionButtons}
            </div>
        `}).join('');
    },

    filterServices: (segment, btn) => {
        // Update active button
        document.querySelectorAll('.segment-filters .btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Filter cards
        const cards = document.querySelectorAll('.service-card');
        cards.forEach(card => {
            if (segment === 'all' || card.dataset.segment === segment) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    },

    // Dashboard Functions
    loadDashboard: async () => {
        if (!app.token) return app.navigate('login');

        try {
            const response = await fetch(`${app.apiBase}/dashboard/`, {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });

            if (response.ok) {
                const data = await response.json();

                // Render Stats
                const statsContainer = document.getElementById('dashboard-stats');
                statsContainer.innerHTML = `
                    <div class="stat-card">
                        <h3>${data.total_cotizado || 0}</h3>
                        <p>Total Cotizado</p>
                    </div>
                `;

                // Update Dashboard Actions based on Role
                const actionsContainer = document.getElementById('dashboard-actions');
                if (actionsContainer) {
                    if (app.user && app.user.role === 'admin') {
                        actionsContainer.innerHTML = `<button class="btn btn-primary" onclick="app.navigate('catalog')">Gestionar Servicios</button>`;
                    } else if (app.user && app.user.role === 'cliente') {
                        actionsContainer.innerHTML = `<button class="btn btn-primary" onclick="app.navigate('catalog')">+ Nueva Solicitud</button>`;
                    } else if (app.user && app.user.role === 'empresa') {
                        // Empresa: No button to create new requests
                        actionsContainer.innerHTML = '';
                    }
                }

                // Load Requests Table
                app.loadRequests();
            }
        } catch (error) {
            console.error(error);
        }
    },

    loadRequests: async () => {
        try {
            const response = await fetch(`${app.apiBase}/solicitudes/`, {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });

            if (response.ok) {
                const requests = await response.json();
                const tbody = document.getElementById('requests-table-body');

                tbody.innerHTML = requests.map(req => {
                    let statusCell = `<span class="status-badge status-${req.estado}">${req.estado}</span>`;

                    // If admin, show dropdown
                    if (app.user && (app.user.role === 'admin' || app.user.role === 'empresa')) {
                        statusCell = `
                            <select onchange="app.updateRequestStatus(${req.id}, this.value)" style="padding:5px; border-radius:5px; border:1px solid var(--border); background:var(--bg-dark); color:white;">
                                <option value="pendiente" ${req.estado === 'pendiente' ? 'selected' : ''}>Pendiente</option>
                                <option value="en_proceso" ${req.estado === 'en_proceso' ? 'selected' : ''}>En Proceso</option>
                                <option value="finalizado" ${req.estado === 'finalizado' ? 'selected' : ''}>Finalizado</option>
                                <option value="cancelado" ${req.estado === 'cancelado' ? 'selected' : ''}>Cancelado</option>
                            </select>
                        `;
                    }

                    return `
                    <tr>
                        <td>#${req.id}</td>
                        <td>${req.servicio_nombre || 'Servicio ' + req.servicio}</td>
                        <td>${new Date(req.fecha_creacion).toLocaleDateString()}</td>
                        <td>${statusCell}</td>
                        <td>
                            <button class="btn btn-text" onclick="app.viewRequest(${req.id})"><i class="fa-solid fa-eye"></i></button>
                        </td>
                    </tr>
                `}).join('');
            }

        } catch (error) {
            console.error(error);
            app.showToast('Error cargando datos del dashboard', 'error');
        }
    },

    // Admin Functions
    openModal: (modalId) => {
        document.getElementById(`modal-${modalId}`).classList.remove('hidden');
    },

    closeModal: (modalId) => {
        document.getElementById(`modal-${modalId}`).classList.add('hidden');
    },

    openCreateServiceModal: () => {
        document.getElementById('service-form').reset();
        document.getElementById('service-id').value = '';
        document.getElementById('service-modal-title').textContent = 'Nuevo Servicio';
        app.openModal('create-service');
    },

    openEditServiceModal: async (id) => {
        try {
            const response = await fetch(`${app.apiBase}/servicios/${id}/`);
            if (response.ok) {
                const service = await response.json();

                const form = document.getElementById('service-form');
                form.reset();
                document.getElementById('service-id').value = service.id;
                form.nombre.value = service.nombre;
                form.descripcion.value = service.descripcion;
                form.segmento.value = service.segmento;
                form.tarifa_base.value = service.tarifa_base;

                document.getElementById('service-modal-title').textContent = 'Editar Servicio';
                app.openModal('create-service');
            }
        } catch (error) {
            app.showToast('Error cargando servicio', 'error');
        }
    },

    handleSaveService: async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        const id = data.id;

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${app.apiBase}/servicios/${id}/` : `${app.apiBase}/servicios/`;

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.token}`
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                app.showToast(id ? 'Servicio actualizado' : 'Servicio creado');
                app.closeModal('create-service');
                app.loadServices();
                e.target.reset();
            } else {
                app.showToast('Error guardando servicio', 'error');
            }
        } catch (error) {
            app.showToast('Error de conexión', 'error');
        }
    },

    deleteService: async (id) => {
        if (!confirm('¿Estás seguro de eliminar este servicio?')) return;

        try {
            const response = await fetch(`${app.apiBase}/servicios/${id}/`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${app.token}` }
            });

            if (response.ok) {
                app.showToast('Servicio eliminado');
                app.loadServices();
            } else {
                app.showToast('Error eliminando servicio', 'error');
            }
        } catch (error) {
            app.showToast('Error de conexión', 'error');
        }
    },

    updateRequestStatus: async (id, newStatus) => {
        try {
            const response = await fetch(`${app.apiBase}/solicitudes/${id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.token}`
                },
                body: JSON.stringify({ estado: newStatus })
            });

            if (response.ok) {
                app.showToast('Estado actualizado');
            } else {
                app.showToast('Error actualizando estado', 'error');
            }
        } catch (error) {
            app.showToast('Error de conexión', 'error');
        }
    },

    // Request Handling
    openRequestModal: (serviceId) => {
        if (!app.token) {
            app.showToast('Inicia sesión para solicitar un servicio', 'warning');
            return app.navigate('login');
        }

        app.loadServiceDetails(serviceId);
    },

    loadServiceDetails: async (id) => {
        try {
            const response = await fetch(`${app.apiBase}/servicios/${id}/`);
            if (response.ok) {
                const service = await response.json();

                // Reset form
                document.getElementById('request-form').reset();

                // Populate Modal
                document.getElementById('request-service-title').textContent = `Solicitar: ${service.nombre}`;
                document.getElementById('request-service-desc').textContent = service.descripcion;
                document.getElementById('request-service-id').value = service.id;

                // Render Dynamic Fields
                const container = document.getElementById('dynamic-fields-container');
                container.innerHTML = '';

                if (service.form_schema && service.form_schema.length > 0) {
                    container.innerHTML = '<h4 style="margin-bottom:15px; border-bottom:1px solid var(--border); padding-bottom:5px">Información Específica</h4>';

                    service.form_schema.forEach(field => {
                        const div = document.createElement('div');
                        div.className = 'form-group';

                        let inputHtml = '';
                        if (field.type === 'select') {
                            const options = field.options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
                            inputHtml = `<select name="dynamic_${field.name}" required>${options}</select>`;
                        } else {
                            inputHtml = `<input type="${field.type || 'text'}" name="dynamic_${field.name}" required placeholder="${field.placeholder || ''}">`;
                        }

                        div.innerHTML = `
                            <label>${field.label}</label>
                            ${inputHtml}
                        `;
                        container.appendChild(div);
                    });
                }

                app.openModal('request-service');
            }
        } catch (error) {
            app.showToast('Error cargando detalles del servicio', 'error');
        }
    },

    handleCreateRequest: async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        const servicioId = formData.get('servicio_id');
        const descripcion = formData.get('descripcion');
        const ubicacion = formData.get('ubicacion');

        // Extract dynamic data
        const datosFormulario = {};
        for (let [key, value] of formData.entries()) {
            if (key.startsWith('dynamic_')) {
                const fieldName = key.replace('dynamic_', '');
                datosFormulario[fieldName] = value;
            }
        }

        try {
            const response = await fetch(`${app.apiBase}/solicitudes/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${app.token}`
                },
                body: JSON.stringify({
                    servicio: servicioId,
                    descripcion: descripcion,
                    ubicacion: ubicacion,
                    datos_formulario: datosFormulario
                })
            });

            if (response.ok) {
                app.showToast('Solicitud creada exitosamente');
                app.closeModal('request-service');
                app.navigate('dashboard');
            } else {
                app.showToast('Error creando solicitud', 'error');
            }
        } catch (error) {
            app.showToast('Error de conexión', 'error');
        }
    },

    viewRequest: async (id) => {
        try {
            const response = await fetch(`${app.apiBase}/solicitudes/${id}/`, {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });

            if (response.ok) {
                const req = await response.json();
                const container = document.getElementById('request-detail-content');

                // Build Dynamic Data List
                let dynamicDataHtml = '';
                if (req.datos_formulario && Object.keys(req.datos_formulario).length > 0) {
                    dynamicDataHtml = '<h4>Detalles Específicos</h4><ul style="list-style:none; padding:0">';
                    for (const [key, value] of Object.entries(req.datos_formulario)) {
                        dynamicDataHtml += `<li style="margin-bottom:5px"><strong>${key}:</strong> ${value}</li>`;
                    }
                    dynamicDataHtml += '</ul>';
                }

                // Build Actions (PDF / WhatsApp / Email)
                let actionsHtml = '';
                if (req.cotizacion_id) {
                    const monto = req.cotizacion_monto ? `$${parseFloat(req.cotizacion_monto).toLocaleString('es-CO')}` : 'N/A';
                    // Store message for later use in modal
                    const whatsappMessage = `Hola, adjunto la cotización de mi solicitud #${req.id}.\n\nServicio: ${req.servicio_nombre || 'N/A'}\nMonto: ${monto}\n\nGracias.`;
                    const emailSubject = encodeURIComponent(`Cotización - Solicitud #${req.id}`);
                    const emailBody = encodeURIComponent(`Adjunto encontrarás la cotización de mi solicitud.\n\nServicio: ${req.servicio_nombre || 'N/A'}\nMonto: ${monto}\n\nSaludos.`);

                    // Store message globally to avoid HTML attribute issues
                    app.currentWhatsAppMessage = whatsappMessage;

                    actionsHtml = `
                        <div style="margin-top:20px; padding-top:20px; border-top:1px solid var(--border)">
                            <h4 style="margin-bottom:15px">Opciones de Cotización</h4>
                            <div style="display:flex; gap:10px; flex-wrap:wrap">
                                <button class="btn btn-primary" onclick="app.downloadPDF(${req.cotizacion_id})"><i class="fa-solid fa-download"></i> Descargar PDF</button>
                                <button class="btn" style="background:#25D366; color:white" onclick="app.openWhatsAppModal(${req.id})"><i class="fa-brands fa-whatsapp"></i> Enviar por WhatsApp</button>
                                <a href="mailto:?subject=${emailSubject}&body=${emailBody}" class="btn btn-outline"><i class="fa-solid fa-envelope"></i> Enviar por Email</a>
                            </div>
                        </div>
                        
                        <div style="margin-top:20px; padding-top:20px; border-top:1px solid var(--border)">
                            <h4 style="margin-bottom:15px">Opciones de Pago</h4>
                            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:15px">
                                <div class="card" style="text-align:center; padding:15px">
                                    <h5 style="color:#FC0D1B; margin-bottom:10px"><i class="fa-solid fa-mobile-screen-button"></i> Nequi</h5>
                                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Pago%20Nequi%20-%20Monto:%20$${req.cotizacion_monto || '0'}" alt="QR Nequi" style="width:150px; height:150px; margin:10px auto; border-radius:8px">
                                    <p style="font-size:0.9em; color:var(--text-muted)">Escanea para pagar</p>
                                </div>
                                <div class="card" style="text-align:center; padding:15px">
                                    <h5 style="color:#ED1C27; margin-bottom:10px"><i class="fa-solid fa-building-columns"></i> Daviplata</h5>
                                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Pago%20Daviplata%20-%20Monto:%20$${req.cotizacion_monto || '0'}" alt="QR Daviplata" style="width:150px; height:150px; margin:10px auto; border-radius:8px">
                                    <p style="font-size:0.9em; color:var(--text-muted)">Escanea para pagar</p>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    actionsHtml = `<div style="margin-top:20px; padding:15px; background:var(--bg-dark); border-radius:var(--radius); color:var(--text-muted)">
                        <i class="fa-solid fa-clock"></i> Cotización en proceso...
                    </div>`;
                }

                container.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px">
                        <h2>Solicitud #${req.id}</h2>
                        <span class="status-badge status-${req.estado}">${req.estado}</span>
                    </div>
                    
                    <div class="card" style="margin-bottom:20px">
                        <h3 style="color:var(--primary)">${req.servicio_nombre || 'Servicio'}</h3>
                        <p style="margin-top:10px">${req.descripcion}</p>
                    </div>

                    ${dynamicDataHtml ? `<div class="card" style="margin-bottom:20px">${dynamicDataHtml}</div>` : ''}
                    
                    ${actionsHtml}
                `;

                app.navigate('request-detail');
            } else {
                app.showToast('Error cargando solicitud', 'error');
            }
        } catch (error) {
            console.error(error);
            app.showToast('Error de conexión', 'error');
        }
    },

    openWhatsAppModal: (requestId) => {
        document.getElementById('whatsapp-request-id').value = requestId;
        // Use the globally stored message
        document.getElementById('whatsapp-message-text').value = app.currentWhatsAppMessage || '';
        app.openModal('whatsapp-number');
    },

    sendWhatsApp: (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const phone = formData.get('phone');
        const message = document.getElementById('whatsapp-message-text').value;

        if (phone) {
            const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
            window.open(url, '_blank');
            app.closeModal('whatsapp-number');
        }
    },

    downloadPDF: async (cotizacionId) => {
        try {
            const response = await fetch(`${app.apiBase}/cotizaciones/${cotizacionId}/generar_pdf/`, {
                headers: { 'Authorization': `Bearer ${app.token}` }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `cotizacion_${cotizacionId}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                app.showToast('PDF descargado correctamente');
            } else {
                app.showToast('Error descargando PDF', 'error');
            }
        } catch (error) {
            console.error(error);
            app.showToast('Error de conexión', 'error');
        }
    }
};

// Start
document.addEventListener('DOMContentLoaded', app.init);
