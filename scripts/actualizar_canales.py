#!/usr/bin/env python3
import json
import asyncio
from playwright.async_api import async_playwright

# ============================================================
#   FUNCIÓN: LIMPIAR PUBLICIDAD, GOOGLE VIGNETTE Y OVERLAYS
# ============================================================
async def limpiar_publicidad(page):

    print("\n==============================")
    print(" LIMPIEZA DE PUBLICIDAD")
    print("==============================\n")

    await page.wait_for_timeout(3000)

    print("→ Buscando anuncios para cerrar...")

    # Selectores típicos + popup de Google Vignette
    posibles_cierres = [
        "button[aria-label='Close']",
        "button.close",
        "button[title='Close']",
        ".close-btn",
        ".ad-close",
        ".adm-close",
        ".vjs-modal-dialog-close-button",
        "div[role='dialog'] button",
        "text=Cerrar",
        "text=Close",
        "text=X",
        "text=×",

        # ESPECÍFICO GOOGLE VIGNETTE
        "div[role='dialog'] >> text=Cerrar",
        "iframe[src*='google_vignette']",
        "#google_vignette",
        "div[id*='google'] button"
    ]

    # Intentar cerrar todos los tipos de publicidad
    for selector in posibles_cierres:
        try:
            loc = page.locator(selector).first
            if await loc.is_visible(timeout=1500):
                await loc.click()
                print(f"   ✔ Cerré popup: {selector}")
                await page.wait_for_timeout(500)
        except:
            pass

    print("→ Eliminando overlays con z-index elevado...")

    try:
        await page.evaluate("""
            document.querySelectorAll('*').forEach(el => {
                const z = window.getComputedStyle(el).zIndex;
                if (z !== 'auto' && parseInt(z) > 999) {
                    el.remove();
                }
            });
        """)
        print("   ✔ Overlays eliminados")
    except:
        print("   ✖ No se pudo eliminar overlays")

    print("\n==============================")
    print(" PUBLICIDAD LIMPIADA")
    print("==============================\n")


# ============================================================
#   OBTENER STREAM M3U8 DE WILLAX
# ============================================================
async def obtener_url_willax():

    print("→ Abriendo Willax...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,   # <<<<<<<<<<<<<< VERÁS LA PÁGINA
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        page = await context.new_page()

        # Donde guardaremos los m3u8 detectados
        page._m3u8_urls = []

        # Escuchar peticiones
        def capturar(request):
            if ".m3u8" in request.url:
                print("✔ Detectado stream:", request.url)
                page._m3u8_urls.append(request.url)

        page.on("request", capturar)

        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        # Limpiar toda la basura visual
        await limpiar_publicidad(page)

        # Presionar play si fuese necesario
        try:
            await page.click("button", timeout=4000)
            print("→ Intenté presionar Play")
        except:
            print("→ No encontré botón Play")

        print("→ Esperando el .m3u8...")

        for i in range(30):
            print(f"   • Esperando... {i+1}/30")
            if page._m3u8_urls:
                break
            await asyncio.sleep(1)

        await browser.close()

        if page._m3u8_urls:
            url = page._m3u8_urls[-1]
            print("✔ URL capturada:", url)
            return url

        print("✖ No se detectó .m3u8")
        return "N/A"


# ============================================================
#   PRINCIPAL
# ============================================================
def main():

    print("Iniciando actualización...")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    nueva = asyncio.run(obtener_url_willax())

    print("→ Resultado:", nueva)

    data["canales"][1]["url"] = nueva

    with open("canales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✔ Guardado correctamente")


if __name__ == "__main__":
    main()
