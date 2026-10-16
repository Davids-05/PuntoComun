// Ruta protegida: si no hay sesión válida, el servidor responde 401 y volvemos a ingresar.
async function iniciar() {
  try {
    const yo = await api("/auth/me");
    document.getElementById("usuario").textContent = yo.nombre;
  } catch (e) {
    window.location.href = "ingreso.html";
  }
}

document.getElementById("ubicacion").addEventListener("click", () => {
  const mensaje = document.getElementById("mensaje");
  if (!navigator.geolocation) { mostrarMensaje(mensaje, "Tu navegador no permite obtener la ubicación.", "error"); return; }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      document.getElementById("latitud").value = pos.coords.latitude.toFixed(6);
      document.getElementById("longitud").value = pos.coords.longitude.toFixed(6);
      mostrarMensaje(mensaje, "Ubicación cargada.", "ok");
    },
    () => mostrarMensaje(mensaje, "No pudimos obtener tu ubicación. Escríbela a mano.", "error")
  );
});

document.getElementById("form").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const mensaje = document.getElementById("mensaje");
  try {
    await api("/reportes", { metodo: "POST", cuerpo: {
      categoria: document.getElementById("categoria").value,
      descripcion: document.getElementById("descripcion").value,
      latitud: Number(document.getElementById("latitud").value),
      longitud: Number(document.getElementById("longitud").value),
    }});
    mostrarMensaje(mensaje, "Reporte enviado. ¡Gracias por avisar!", "ok");
    evento.target.reset();
  } catch (e) {
    if (e.status === 401) { window.location.href = "ingreso.html"; return; }
    mostrarMensaje(mensaje, e.message, "error");
  }
});

document.getElementById("salir").addEventListener("click", async () => {
  try { await api("/auth/logout", { metodo: "POST" }); } catch (e) { /* ya estaba cerrada */ }
  window.location.href = "ingreso.html";
});

iniciar();
