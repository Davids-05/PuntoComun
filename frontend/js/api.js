// Utilidades compartidas: llamadas a la API y mensajes en pantalla.
async function api(ruta, { metodo = "GET", cuerpo } = {}) {
  const opciones = { method: metodo, headers: {}, credentials: "same-origin" };
  if (cuerpo !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo);
  }
  const respuesta = await fetch(ruta, opciones);
  if (respuesta.status === 204) return null;
  let datos = null;
  try { datos = await respuesta.json(); } catch (e) { /* respuesta sin cuerpo */ }
  if (!respuesta.ok) {
    const error = new Error(textoDeError(datos, respuesta.status));
    error.status = respuesta.status;
    throw error;
  }
  return datos;
}

function textoDeError(datos, estado) {
  if (datos && typeof datos.detail === "string") return datos.detail;
  if (datos && Array.isArray(datos.detail)) {
    return datos.detail.map(d => (d.msg || "").replace("Value error, ", "")).join(". ");
  }
  return "Ocurrió un error (" + estado + ")";
}

// Siempre textContent, nunca innerHTML: así un texto malicioso no puede ejecutarse (XSS).
function mostrarMensaje(elemento, texto, tipo) {
  elemento.textContent = texto;
  elemento.className = "mensaje " + (tipo || "");
}
