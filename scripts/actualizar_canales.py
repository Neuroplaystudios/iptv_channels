#!/usr/bin/env python3
import json
import asyncio
from playwright.async_api import async_playwright

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ===========================
#   FUNCIÓN CORREGIDA
# ===========================
async def obtener_url_willax():

    print("→ Abriendo Willax para capturar .m3u8...")

    async with async_playwright() as p:
        # MODO COMPATIBLE CON GITHUB ACTIONS
        browser = await p.chromium.launch(headless="new", args=["--no-sandbox", "--disable-gpu"])
        page = await browser.new_page()

        # lista para almacenar todas las URLs .m3u8 detectadas
        page._m3u8_urls = []

        # Capturar requests a .m3u8
        def capturar(req):
            if ".m3u8" in req.url:
                print("Detectado:", req.url)
                page._m3u8_urls.append(req.url)

        page.on("request", capturar)

        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        # Esperar a que cargue el streaming
        await page.wait_for_timeout(8000)

        await browser.close()

        # Obtener solo el último m3u8 capturado
        if page._m3u8_urls:
            ultimo = page._m3u8_urls[-1]
            print("✔ Último .m3u8 encontrado:", ultimo)
            return ultimo
        else:
            print("✖ No se pudo obtener .m3u8.")
            return None


# ===========================
#           MAIN
# ===========================
def main():
    print("Iniciando actualización...")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Obtener la URL .m3u8 usando Playwright
    nueva = asyncio.run(obtener_url_willax())

    cambios = False

    if nueva and nueva != data["canales"][1]["url"]:
        data["canales"][1]["url"] = nueva
        cambios = True

    if cambios:
        with open("canales.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✔ canales.json actualizado.")
    else:
        print("No hubo cambios.")


if __name__ == "__main__":
    main()
