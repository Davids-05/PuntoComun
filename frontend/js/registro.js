document.getElementById("form").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const mensaje = document.getElementById("mensaje");
  const boton = evento.target.querySelector("button");
  boton.disabled = true;
  try {
    await api("/auth/register", { metodo: "POST", cuerpo: {
      nombre: document.getElementById("nombre").value,
      email: document.getElementById("email").value,
      password: document.getElementById("password").value,
    }});
    mostrarMensaje(mensaje, "Cuenta creada. Te llevamos a ingresar…", "ok");
    setTimeout(() => { window.location.href = "ingreso.html"; }, 1200);
  } catch (e) {
    mostrarMensaje(mensaje, e.message, "error");
    boton.disabled = false;
  }
});
