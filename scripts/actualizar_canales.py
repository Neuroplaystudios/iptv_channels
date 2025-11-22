#!/usr/bin/env python3
import json
import asyncio
from playwright.async_api import async_playwright

async def obtener_url_willax():
    print("→ Abriendo Willax para capturar .m3u8...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        page = await browser.new_page()

        page._m3u8_urls = []

        # Capturar requests a .m3u8
        def capturar(request):
            if ".m3u8" in request.url:
                print("✔ Detectado:", request.url)
                page._m3u8_urls.append(request.url)

        page.on("request", capturar)

        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        # Intentar hacer clic en el botón Play si aparece
        try:
            await page.click("button", timeout=5000)
        except:
            pass

        # Esperar 10 segundos por si el player tarda en cargar
        await page.wait_for_timeout(10000)

        await browser.close()

        if page._m3u8_urls:
            return page._m3u8_urls[-1]
        else:
            print("✖ No apareció ningún .m3u8")
            return "N/A"


def main():
    print("Iniciando actualización...")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    nueva = asyncio.run(obtener_url_willax())

    data["canales"][1]["url"] = nueva

    with open("canales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✔ Guardado en canales.json:", nueva)


if __name__ == "__main__":
    main()

