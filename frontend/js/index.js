const etiquetas = { vias: "Vías", alumbrado: "Alumbrado", agua: "Agua", espacios_publicos: "Espacios públicos" };

async function cargar() {
  const estado = document.getElementById("estado");
  const lista = document.getElementById("lista");
  try {
    const reportes = await api("/reportes");
    if (reportes.length === 0) { mostrarMensaje(estado, "Todavía no hay reportes."); return; }
    reportes.forEach(r => {
      const tarjeta = document.createElement("article");
      tarjeta.className = "tarjeta";
      const titulo = document.createElement("h2");
      titulo.textContent = etiquetas[r.categoria] || r.categoria;
      const texto = document.createElement("p");
      texto.textContent = r.descripcion;
      const meta = document.createElement("p");
      meta.className = "suave";
      meta.textContent = "Estado: " + r.estado + " · " + r.latitud.toFixed(4) + ", " + r.longitud.toFixed(4);
      tarjeta.append(titulo, texto, meta);
      lista.append(tarjeta);
    });
  } catch (e) {
    mostrarMensaje(estado, e.message, "error");
  }
}
cargar();
