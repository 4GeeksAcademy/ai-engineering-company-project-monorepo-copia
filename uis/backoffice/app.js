const API_URL = `https://${window.location.hostname.replace('3000', '8000')}/suppliers`;
// Elementos del DOM
const tableBody = document.getElementById("suppliers-body");
const filterCountry = document.getElementById("filter-country");
const filterCategory = document.getElementById("filter-category");
const form = document.getElementById("supplier-form");
const formMessage = document.getElementById("form-message");

// 1. Función para obtener y mostrar proveedores
async function fetchSuppliers() {
    let url = API_URL;
    const params = new URLSearchParams();
    
    if (filterCountry.value) params.append("country", filterCountry.value);
    if (filterCategory.value) params.append("category", filterCategory.value);

    if (params.toString()) {
        url += `?${params.toString()}`;
    }

    try {
        const response = await fetch(url);
        const suppliers = await response.json();
        renderTable(suppliers);
    } catch (error) {
        console.error("Error cargando proveedores:", error);
    }
}

// 2. Función para dibujar la tabla
function renderTable(suppliers) {
    tableBody.innerHTML = ""; // Limpiar tabla

    suppliers.forEach(supplier => {
        const tr = document.createElement("tr");
        
        // Formatear categorías
        const categories = supplier.product_categories.join(", ");
        
        // Clase CSS según el estado
        const statusClass = supplier.status === "active" ? "status-active" : "status-suspended";
        const statusText = supplier.status === "active" ? "Activo" : "Suspendido";

        // Botón de acción (Activar/Suspender)
        const actionText = supplier.status === "active" ? "Suspender" : "Activar";
        const actionClass = supplier.status === "active" ? "btn-suspend" : "btn-activate";

        tr.innerHTML = `
            <td>${supplier.name}</td>
            <td>${supplier.country}</td>
            <td>${categories}</td>
            <td>$${supplier.rate.toFixed(2)}</td>
            <td><span class="${statusClass}">${statusText}</span></td>
            <td>
                <button class="${actionClass}" onclick="toggleStatus('${supplier.id}', '${supplier.status}')">
                    ${actionText}
                </button>
                <button onclick="editRate('${supplier.id}', ${supplier.rate})">Editar Tarifa</button>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

// 3. Eventos de los filtros
filterCountry.addEventListener("change", fetchSuppliers);
filterCategory.addEventListener("change", fetchSuppliers);

// 4. Función para cambiar estado (PATCH)
async function toggleStatus(id, currentStatus) {
    const newStatus = currentStatus === "active" ? "suspended" : "active";
    
    try {
        const response = await fetch(`${API_URL}/${id}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            fetchSuppliers(); // Recargar la tabla
        } else {
            alert("Error al cambiar el estado");
        }
    } catch (error) {
        console.error(error);
    }
}

// 5. Función para editar tarifa (PATCH)
async function editRate(id, currentRate) {
    const newRate = prompt("Introduce la nueva tarifa:", currentRate);
    if (newRate === null || newRate === "") return;

    const rateValue = parseFloat(newRate);
    if (isNaN(rateValue) || rateValue <= 0) {
        alert("La tarifa debe ser un número mayor a 0");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}/rate`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rate: rateValue })
        });

        if (response.ok) {
            fetchSuppliers(); // Recargar la tabla
        } else {
            alert("Error al actualizar la tarifa");
        }
    } catch (error) {
        console.error(error);
    }
}

// 6. Manejar el formulario de creación (POST)
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    formMessage.textContent = "";

    const newSupplier = {
        name: document.getElementById("name").value,
        country: document.getElementById("country").value,
        product_categories: [document.getElementById("category").value],
        rate: parseFloat(document.getElementById("rate").value),
        status: "active"
    };

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newSupplier)
        });

        if (response.ok) {
            form.reset();
            formMessage.textContent = "✅ Proveedor añadido correctamente.";
            formMessage.style.color = "green";
            fetchSuppliers(); // Recargar la tabla
        } else {
            const errorData = await response.json();
            formMessage.textContent = "❌ Error: " + (errorData.detail[0]?.msg || "Datos inválidos");
            formMessage.style.color = "red";
        }
    } catch (error) {
        console.error(error);
        formMessage.textContent = "❌ Error de conexión con el servidor.";
        formMessage.style.color = "red";
    }
});

// Cargar los datos al iniciar la página
fetchSuppliers();