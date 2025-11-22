#!/usr/bin/env python3
import json
import asyncio
from playwright.async_api import async_playwright

HEADERS = { "User-Agent": "Mozilla/5.0" }

# ===========================
#   FUNCIÓN PARA CAPTURAR .m3u8
# ===========================
async def obtener_url_willax():

    print("→ Abriendo Willax para capturar .m3u8...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        page = await browser.new_page()

        page._m3u8_urls = []

        # Capturar cualquier request con .m3u8
        def capturar(req):
            if ".m3u8" in req.url:
                print("Detectado:", req.url)
                page._m3u8_urls.append(req.url)

        page.on("request", capturar)

        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        await page.wait_for_timeout(8000)
        await browser.close()

        # Devolver último .m3u8
        if page._m3u8_urls:
            return page._m3u8_urls[-1]

        return None


# ===========================
#             MAIN
# ===========================
def main():
    print("Iniciando actualización...")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    nueva = asyncio.run(obtener_url_willax())

    # ====================================================
    # 🔥 SIEMPRE llenar el campo, aunque no haya cambios
    # ====================================================
    if nueva:
        data["canales"][1]["url"] = nueva
        print("✔ Actualizado con nueva URL:", nueva)
    else:
        data["canales"][1]["url"] = "N/A"
        print("✖ No se encontró .m3u8, se guardó 'N/A'.")

    # Guardar SIEMPRE el archivo
    with open("canales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✔ canales.json guardado correctamente.")


if __name__ == "__main__":
    main()
