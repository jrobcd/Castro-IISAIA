"""Recorrido de la interfaz en Chromium contra un servidor ya levantado, con la base vacía.

    uv run --group e2e playwright install chromium   # una vez
    uv run --group e2e python scripts/recorrido_navegador.py http://127.0.0.1:8000/

Repite los casos que rompieron el TP 1 y suma los que aparecen al tener servidor.
"""

import sys

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/"


def esperar(page):
    page.wait_for_function("!document.body.classList.contains('ocupado')")


def pila(page, i):
    return page.eval_on_selector_all(f".torre:nth-child({i + 1}) .disco", "ds => ds.map(d => d.textContent)")


def agregar(page, titulo, prioridad, torre):
    page.fill("#nueva-titulo", titulo)
    page.select_option("#nueva-prioridad", str(prioridad))
    page.select_option("#nueva-proyecto", index=torre)
    page.click("form.nueva button[type=submit]")
    esperar(page)


def levantar(page, i):
    page.locator(f".torre:nth-child({i + 1}) .disco").last.click()


def poner(page, i):
    page.locator(f".torre:nth-child({i + 1}) button.aca").click()
    esperar(page)


def abrir(nav):
    page = nav.new_page()
    page.goto(URL)
    page.wait_for_selector(".torre:nth-child(3)")
    esperar(page)
    return page


def main():
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        page = abrir(nav)
        mensaje = lambda: page.text_content("#mensaje")
        assert pila(page, 0) == pila(page, 1) == pila(page, 2) == [], "la base tiene que estar vacía"

        # Bug de desempate del TP 1: la tarea recién apilada queda arriba de la de igual prioridad.
        agregar(page, "A", 3, 0)
        agregar(page, "B", 3, 1)
        levantar(page, 0); poner(page, 1)
        assert pila(page, 1) == ["B", "A"]

        # No entra una más prioritaria sobre una menos prioritaria.
        agregar(page, "D", 1, 0)
        levantar(page, 1); poner(page, 0)
        assert "No entra" in mensaje() and pila(page, 1) == ["B", "A"]
        page.click("#btn-soltar")

        # Una enterrada no se toca.
        agregar(page, "E", 2, 1)
        page.locator(".torre:nth-child(2) .disco").first.click()
        assert "2 tareas encima" in mensaje()

        # El 422 del servidor llega en castellano y la pantalla vuelve al estado aceptado.
        nombre = page.locator(".torre:nth-child(3) input.nombre")
        nombre.fill(""); nombre.press("Enter"); esperar(page); page.wait_for_timeout(200)
        assert mensaje() == "name no puede estar vacío." and nombre.input_value() == "Casa"

        # Dos pestañas: si otra mueve la tarea que esta tiene levantada, esta la suelta.
        otra = abrir(nav)
        levantar(otra, 1)
        levantar(page, 1); poner(page, 2)
        otra.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); esperar(otra)
        assert pila(otra, 2) == ["E"] and otra.locator(".disco.elegido").count() == 0

        # Persistencia en el servidor.
        antes = [pila(page, i) for i in range(3)]
        page.reload(); page.wait_for_selector(".disco"); esperar(page)
        assert [pila(page, i) for i in range(3)] == antes

        nav.close()
    print("Recorrido OK")


if __name__ == "__main__":
    main()
