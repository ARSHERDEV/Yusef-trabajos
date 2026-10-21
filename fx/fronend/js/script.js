const API_BASE = "http://127.0.0.1:5000/api";
let modalYaMostrado = false;

// 1. CARGAR CARDS DE FRUTAS
async function cargarInventarioCards() {
  try {
    const res = await fetch(`${API_BASE}/inventario`);
    const frutas = await res.json();
    const container = document.getElementById('cards-container');
    container.innerHTML = "";

    frutas.forEach(f => {
      container.innerHTML += `
        <div class="fruit-card" id="card-fruit-${f.id}" onclick="seleccionarCardFruta(${f.id})">
          <span class="emoji">${f.emoji || '🍎'}</span>
          <div class="name">${f.nombre}</div>
          <div class="calories">${f.calorias} kcal</div>
        </div>
      `;
    });
  } catch (err) {
    console.error("Error al cargar inventario:", err);
  }
}

// 2. SELECCIÓN DE FRUTA (Máximo 3 y control de límite)
async function seleccionarCardFruta(id) {
  try {
    const resActual = await fetch(`${API_BASE}/frutas`);
    const listaActual = await resActual.json();

    if (listaActual.length >= 3) {
      alert("¡Ya has seleccionado el máximo de 3 frutas! Elimina una si deseas cambiar tu selección.");
      return;
    }

    await fetch(`${API_BASE}/frutas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id })
    });

    actualizarListaVisual();
  } catch (err) {
    console.error("Error al seleccionar fruta:", err);
  }
}

// 3. ACTUALIZAR LISTA, HIGHLIGHT PERMANENTE Y POPUP
async function actualizarListaVisual() {
  try {
    const res = await fetch(`${API_BASE}/frutas`);
    const lista = await res.json();
    const ul = document.getElementById('lista-seleccion');
    const counter = document.getElementById('status-counter');

    // Limpiar iluminación de todas las cards
    document.querySelectorAll('.fruit-card').forEach(card => card.classList.remove('selected'));

    // Iluminar permanentemente las cards de las frutas seleccionadas
    lista.forEach(fruta => {
      const cardElegida = document.getElementById(`card-fruit-${fruta.id}`);
      if (cardElegida) {
        cardElegida.classList.add('selected');
      }
    });

    ul.innerHTML = "";
    let totalCalorias = 0;

    if (lista.length === 0) {
      ul.innerHTML = "<li style='color: #a0aec0;'>No has seleccionado frutas.</li>";
      modalYaMostrado = false;
    } else {
      lista.forEach((fruta, i) => {
        totalCalorias += fruta.calorias || 0;
        ul.innerHTML += `
          <li>
            <span><b>${i + 1}.</b> ${fruta.nombre} (${fruta.calorias} kcal)</span>
            <div class="actions">
              <button class="btn-edit" onclick="editarFruta(${i})">Editar</button>
              <button class="btn-delete" onclick="eliminarFruta(${i})">Quitar</button>
            </div>
          </li>`;
      });
    }

    if (lista.length >= 3) {
      counter.className = "status-box success";
      counter.innerText = `¡Meta cumplida! Llevas 3/3 frutas. Total: ${totalCalorias} kcal.`;

      if (!modalYaMostrado) {
        mostrarModalRecomendacion(totalCalorias, lista);
        modalYaMostrado = true;
      }
    } else {
      counter.className = "status-box alert";
      counter.innerText = `Llevas ${lista.length}/3 frutas. Agrega ${3 - lista.length} más.`;
      if (lista.length < 3) modalYaMostrado = false;
    }

  } catch (err) {
    console.error("Error al leer frutas:", err);
  }
}

// 4. MOSTRAR POPUP MODAL CON RECOMENDACIONES
function mostrarModalRecomendacion(calorias, listaFrutas) {
  document.getElementById('modal-calorias').innerText = `Aporte nutricional total: ${calorias} kcal`;
  
  const nombres = listaFrutas.map(f => f.nombre).join(', ');
  let consejo = "";

  if (calorias < 150) {
    consejo = `Tu combinación (${nombres}) es de muy bajo aporte calórico. Es ideal como snack a media mañana o media tarde para mantener tus niveles de energía estables.`;
  } else if (calorias <= 250) {
    consejo = `Tu combinación (${nombres}) ofrece un balance ideal de azúcares naturales y fibra. Se recomienda ingerirlas entre 30 a 45 minutos antes de entrenar o realizar actividad física.`;
  } else {
    consejo = `Esta selección (${nombres}) aporta una excelente recarga energética. Te sugerimos consumirla acompañada de un vaso de agua o en ensalada de frutas durante el desayuno.`;
  }

  document.getElementById('modal-recomendacion').innerText = consejo;
  document.getElementById('modal-popup').classList.remove('hidden');
}

function cerrarModal() {
  document.getElementById('modal-popup').classList.add('hidden');
}

// EDITAR Y ELIMINAR FRUTAS
async function editarFruta(index) {
  const nuevoId = prompt("Nuevo ID (1: Manzana, 2: Banano, 3: Fresa, 4: Naranja, 5: Uva):");
  if (!nuevoId) return;

  const res = await fetch(`${API_BASE}/frutas/${index}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: parseInt(nuevoId) })
  });

  if (res.ok) actualizarListaVisual();
  else alert("No se pudo actualizar la fruta.");
}

// ELIMINAR FRUTA (Directo, sin prompt de confirmación)
async function eliminarFruta(index) {
  await fetch(`${API_BASE}/frutas/${index}`, { method: 'DELETE' });
  actualizarListaVisual();
}

// INICIO DE SESIÓN Y NAVEGACIÓN
async function iniciarSesion() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const feedback = document.getElementById('login-feedback');

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error de login");

    feedback.className = "status-box success";
    feedback.innerText = data.mensaje;

    setTimeout(() => {
      document.getElementById('login-section').classList.add('hidden');
      document.getElementById('crud-section').classList.remove('hidden');
      document.getElementById('user-greeting').innerText = `Hola, ${username}`;
      cargarInventarioCards();
      actualizarListaVisual();
    }, 500);

  } catch (err) {
    feedback.className = "status-box alert";
    feedback.innerText = err.message;
  }
}

async function cargarYMostrarEjercicios() {
  try {
    const res = await fetch(`${API_BASE}/ejercicios`);
    if (!res.ok) throw new Error("No se pudo obtener la lista de ejercicios.");
    
    const data = await res.json();

    document.getElementById('contenido-js').innerHTML = data.javascript.map(e => `
      <div class="exercise-box">
        <div class="exercise-title">${e.titulo}</div>
        <pre><code>${e.codigo}</code></pre>
      </div>
    `).join('');

    document.getElementById('contenido-py').innerHTML = data.python.map(e => `
      <div class="exercise-box">
        <div class="exercise-title">${e.titulo}</div>
        <pre><code>${e.codigo}</code></pre>
      </div>
    `).join('');

    document.getElementById('crud-section').classList.add('hidden');
    document.getElementById('ejercicios-section').classList.remove('hidden');

  } catch (err) {
    alert("Error al cargar ejercicios: " + err.message);
  }
}

function volverAlCrud() {
  document.getElementById('ejercicios-section').classList.add('hidden');
  document.getElementById('crud-section').classList.remove('hidden');
}

function cambiarTab(lang) {
  document.getElementById('tab-js').classList.toggle('active', lang === 'js');
  document.getElementById('tab-py').classList.toggle('active', lang === 'py');
  document.getElementById('contenido-js').classList.toggle('hidden', lang !== 'js');
  document.getElementById('contenido-py').classList.toggle('hidden', lang !== 'py');
}