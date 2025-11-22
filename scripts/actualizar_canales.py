#!/usr/bin/env python3
import json
import asyncio
from playwright.async_api import async_playwright


async def cerrar_publicidad(page):
    """Cierra popups, anuncios y overlays que bloquean el video."""
    print("→ Buscando publicidad para cerrar...")

    posibles_cierres = [
        "button[aria-label='Close']",
        "button.close",
        "button[title='Close']",
        ".close-btn",
        ".ad-close",
        ".adm-close",
        ".vjs-modal-dialog-close-button",
        "div[role='dialog'] button",
        "text='Cerrar'",
        "text='Close'",
        "text='X'",
        "text='×'"
    ]

    # Intentar cerrar varios tipos de anuncios
    for selector in posibles_cierres:
        try:
            await page.locator(selector).first.click(timeout=1500)
            print(f"   ✔ Cerré publicidad: {selector}")
            await page.wait_for_timeout(300)
        except:
            pass

    # Eliminar overlays gigantes con z-index alto
    try:
        await page.evaluate("""
            document.querySelectorAll('*').forEach(el => {
                const z = window.getComputedStyle(el).zIndex;
                if (z !== 'auto' && parseInt(z) > 1000) {
                    el.remove();
                }
            });
        """)
        print("   ✔ Eliminé overlays molestos")
    except:
        pass


async def obtener_url_willax():
    print("→ Abriendo Willax para capturar .m3u8...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        page = await browser.new_page()

        # Lista donde se guardarán los .m3u8
        page._m3u8_urls = []

        # Escuchar todas las requests
        def capturar(request):
            if ".m3u8" in request.url:
                print("✔ Detectado stream:", request.url)
                page._m3u8_urls.append(request.url)

        page.on("request", capturar)

        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        # Cerrar publicidad antes de buscar el player
        await cerrar_publicidad(page)

        # Intentar darle Play al video
        try:
            await page.click("button", timeout=5000)
            print("→ Hice clic en el botón Play")
        except:
            print("→ No encontré botón Play (quizá se auto-reproduce)")

        print("→ Esperando a que cargue el .m3u8...")

        # Espera dinámica de hasta 30 segundos
        for _ in range(30):
            if page._m3u8_urls:
                break
            await asyncio.sleep(1)

        await browser.close()

        if page._m3u8_urls:
            return page._m3u8_urls[-1]

        print("✖ No apareció ningún .m3u8")
        return "N/A"


def main():
    print("Iniciando actualización...")

    # Leer canales.json
    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Obtener nueva URL de Willax
    nueva = asyncio.run(obtener_url_willax())
    print("→ Resultado final:", nueva)

    # Actualizar JSON
    data["canales"][1]["url"] = nueva

    # Guardar archivo actualizado
    with open("canales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✔ Guardado en canales.json:", nueva)


if __name__ == "__main__":
    main()
