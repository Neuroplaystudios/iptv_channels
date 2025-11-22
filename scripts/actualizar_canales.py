#!/usr/bin/env python3
import json
import asyncio
import os
from playwright.async_api import async_playwright

# ============================================================
#   FUNCIÓN: LIMPIAR PUBLICIDAD, GOOGLE VIGNETTE Y OVERLAYS
# ============================================================
async def limpiar_publicidad(page):

    print("\n========================================")
    print(" 🧹 INICIO → LIMPIEZA DE PUBLICIDAD")
    print("========================================\n")

    await page.wait_for_timeout(3000)

    print("[LOG] → Buscando elementos de publicidad para cerrar...")

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
        "div[role='dialog'] >> text=Cerrar",
        "iframe[src*='google_vignette']",
        "#google_vignette",
        "div[id*='google'] button"
    ]

    for selector in posibles_cierres:
        try:
            loc = page.locator(selector).first
            if await loc.is_visible(timeout=1500):
                print(f"[LOG] → Intentando cerrar popup con selector: {selector}")
                await loc.click()
                print(f"   ✔ Popup cerrado: {selector}")
                await page.wait_for_timeout(500)
        except Exception as e:
            print(f"[LOG] No se encontró/cerro: {selector} (OK)")

    print("[LOG] → Eliminando overlays con z-index alto...")

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
        print("   ✖ No fue posible eliminar overlays")

    print("\n========================================")
    print(" 🧹 FIN → PUBLICIDAD LIMPIADA")
    print("========================================\n")


# ============================================================
#   OBTENER STREAM M3U8 DE WILLAX
# ============================================================
async def obtener_url_willax():

    print("\n========================================")
    print(" 🚀 INICIO → OBTENER URL DE WILLAX")
    print("========================================\n")

    async with async_playwright() as p:
        print("[LOG] → Iniciando navegador Chromium...")
        esta_en_github = os.environ.get("GITHUB_ACTIONS") == "true"

        browser = await p.chromium.launch(
            headless=True if esta_en_github else False,
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        print("[LOG] → Creando contexto...")

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
        )

        print("[LOG] → Abriendo pestaña...")

        page = await context.new_page()
        page._m3u8_urls = []

        # Captura de peticiones
        def capturar(request):
            if ".m3u8" in request.url:
                print(f"🔥 DETECTADO M3U8 → {request.url}")
                page._m3u8_urls.append(request.url)

        print("[LOG] → Activando escucha de peticiones...")
        page.on("request", capturar)

        print("[LOG] → Cargando página de Willax...")
        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        # LIMPIAR BASURA
        await limpiar_publicidad(page)

        # PRESIONAR PLAY SI ES NECESARIO
        try:
            print("[LOG] → Buscando botón PLAY...")
            await page.click("button", timeout=4000)
            print("   ✔ Botón Play presionado")
        except:
            print("   ⚠ No encontré botón Play (probablemente ya está reproduciendo)")

        print("[LOG] → Esperando detección de .m3u8...")

        for i in range(30):
            print(f"   • Esperando... {i+1}/30")
            if page._m3u8_urls:
                break
            await asyncio.sleep(1)

        print("[LOG] → Cerrando navegador...")
        await browser.close()

        # RESULTADO
        if page._m3u8_urls:
            url = page._m3u8_urls[-1]
            print("✔ URL FINAL OBTENIDA:", url)
            return url

        print("✖ No se detectó ninguna URL .m3u8")
        return "N/A"


# ============================================================
#   PROGRAMA PRINCIPAL
# ============================================================
def main():

    print("\n========================================")
    print(" 🟦 INICIO → ACTUALIZACIÓN DE CANALES")
    print("========================================\n")

    print("[LOG] → Leyendo archivo canales.json...")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print("[LOG] → Obteniendo nueva URL para Willax...")

    nueva = asyncio.run(obtener_url_willax())

    print("[LOG] → Resultado capturado:", nueva)

    data["canales"][1]["url"] = nueva

    print("[LOG] → Guardando cambios en canales.json...")

    with open("canales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n========================================")
    print(" ✔ PROCESO COMPLETADO — Archivo actualizado")
    print("========================================\n")


if __name__ == "__main__":
    main()
