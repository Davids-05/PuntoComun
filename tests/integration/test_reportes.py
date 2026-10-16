REPORTE = {"categoria": "vias", "descripcion": "Hueco grande en la calzada", "latitud": 10.96, "longitud": -74.78}


def test_crear_reporte_sin_sesion_da_401(client):
    assert client.post("/reportes", json=REPORTE).status_code == 401


def test_crear_y_listar_reporte_con_sesion(client, sesion_iniciada):
    r = client.post("/reportes", json=REPORTE, headers={"Authorization": f"Bearer {sesion_iniciada}"})
    assert r.status_code == 201 and r.json()["estado"] == "reportado"
    client.cookies.clear()
    lista = client.get("/reportes")  # lectura pública
    assert lista.status_code == 200 and len(lista.json()) == 1


def test_reporte_invalido_da_422(client, sesion_iniciada):
    cabecera = {"Authorization": f"Bearer {sesion_iniciada}"}
    for cambio in ({"categoria": "otra"}, {"latitud": 200}, {"descripcion": "no"}):
        assert client.post("/reportes", json={**REPORTE, **cambio}, headers=cabecera).status_code == 422
