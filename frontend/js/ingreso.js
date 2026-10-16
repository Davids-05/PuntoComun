let correo = "";
const paso1 = document.getElementById("paso1");
const paso2 = document.getElementById("paso2");
const boton_reenviar = document.getElementById("reenviar");

paso1.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const mensaje = document.getElementById("mensaje1");
  correo = document.getElementById("email").value.trim();
  try {
    await api("/auth/login", { metodo: "POST", cuerpo: { email: correo, password: document.getElementById("password").value } });
    paso1.classList.add("oculto");
    paso2.classList.remove("oculto");
    document.getElementById("codigo").focus();
  } catch (e) {
    mostrarMensaje(mensaje, e.message, "error");
  }
});

paso2.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const mensaje = document.getElementById("mensaje2");
  try {
    await api("/auth/verify-otp", { metodo: "POST", cuerpo: { email: correo, codigo: document.getElementById("codigo").value.trim() } });
    window.location.href = "reportar.html"; // la cookie de sesión ya quedó guardada por el servidor
  } catch (e) {
    mostrarMensaje(mensaje, e.message, "error");
  }
});

boton_reenviar.addEventListener("click", async () => {
  const mensaje = document.getElementById("mensaje2");
  boton_reenviar.disabled = true;
  try {
    await api("/auth/resend-otp", { metodo: "POST", cuerpo: { email: correo } });
    mostrarMensaje(mensaje, "Te enviamos un código nuevo.", "ok");
  } catch (e) {
    mostrarMensaje(mensaje, e.message, "error");
  }
  setTimeout(() => { boton_reenviar.disabled = false; }, 30000); // enfriamiento visual; el límite real lo pone el servidor
});
