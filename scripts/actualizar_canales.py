#!/usr/bin/env python3
import json
import asyncio
from playwright.async_api import async_playwright

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ===========================
#   NUEVA FUNCIÓN CORREGIDA
# ===========================
async def obtener_url_willax():

    print("→ Abriendo Willax para capturar .m3u8...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        ultimo_m3u8 = None

        # Capturar requests
        page.on("request", lambda req: (
            print("Detectado:", req.url) or None,
            setattr(page, "_m3u8", req.url)
        ) if ".m3u8" in req.url else None)

        await page.goto("https://willax.pe/en-vivo")

        # Esperar para que cargue el reproductor y streaming
        await page.wait_for_timeout(8000)

        # Obtener el último m3u8 capturado
        ultimo_m3u8 = getattr(page, "_m3u8", None)

        await browser.close()

        if ultimo_m3u8:
            print("✔ Último .m3u8 encontrado:", ultimo_m3u8)
            return ultimo_m3u8
        else:
            print("✖ No se pudo obtener .m3u8.")
            return None


# ===========================
#   MAIN SIN CAMBIOS
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
