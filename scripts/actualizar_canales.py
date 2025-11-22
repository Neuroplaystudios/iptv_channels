#!/usr/bin/env python3
import json
import asyncio
from playwright.async_api import async_playwright


# ============================================================
#   FUNCIÓN: LIMPIEZA DE PUBLICIDAD Y OVERLAYS
# ============================================================
async def limpiar_publicidad(page):

    print("\n==============================")
    print(" INICIANDO LIMPIEZA DE PUBLICIDAD")
    print("==============================\n")

    # Espera inicial para que aparezcan anuncios
    print("→ Esperando 2 segundos para que cargue la publicidad...")
    await page.wait_for_timeout(2000)

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

    # Intentar cerrar anuncios
    for selector in posibles_cierres:
        try:
            loc = page.locator(selector).first
            if await loc.is_visible(timeout=1500):
                await loc.click()
                print(f"   ✔ Cerré publicidad: {selector}")
                await page.wait_for_timeout(300)
        except Exception as e:
            print(f"   ✖ No pude cerrar: {selector} ({type(e).__name__})")

    print("→ Intentando eliminar overlays con z-index alto...")

    # Intentar borrar overlays molestos
    try:
        await page.evaluate("""
            document.querySelectorAll('*').forEach(el => {
                const z = window.getComputedStyle(el).zIndex;
                if (z !== 'auto' && parseInt(z) > 1000) {
                    el.remove();
                }
            });
        """)
        print("   ✔ Overlays eliminados")
    except Exception as e:
        print(f"   ✖ Error eliminando overlays: {type(e).__name__}")

    print("\n==============================")
    print(" PUBLICIDAD LIMPIADA")
    print("==============================\n")


# ============================================================
#   FUNCIÓN: CAPTURAR STREAM M3U8 DE WILLAX
# ============================================================
async def obtener_url_willax():

    print("→ Abriendo Willax para capturar .m3u8...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        page = await browser.new_page()

        # Donde se acumularán los streams detectados
        page._m3u8_urls = []

        # Escuchar todas las peticiones
        def capturar(request):
            if ".m3u8" in request.url:
                print("✔ Detectado stream:", request.url)
                page._m3u8_urls.append(request.url)

        page.on("request", capturar)

        # Abrir página
        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        # Cerrar publicidad
        await limpiar_publicidad(page)

        # Intentar presionar Play
        try:
            await page.click("button", timeout=5000)
            print("→ Hice clic en Play")
        except:
            print("→ No encontré Play, quizá se auto-reproduce")

        print("→ Esperando que aparezca el .m3u8...")

        # Esperar dinamicamente hasta 30 segundos
        for segundos in range(30):
            print(f"   • Esperando... {segundos+1}/30")
            if page._m3u8_urls:
                break
            await asyncio.sleep(1)

        await browser.close()

        # Retornar resultado
        if page._m3u8_urls:
            url_final = page._m3u8_urls[-1]
            print("✔ URL final detectada:", url_final)
            return url_final

        print("✖ No apareció ningún .m3u8")
        return "N/A"


# ============================================================
#   FUNCIÓN PRINCIPAL
# ============================================================
def main():

    print("Iniciando actualización...")

    # Leer JSON existente
    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ejecutar scrapper
    nueva = asyncio.run(obtener_url_willax())

    print("→ Resultado final:", nueva)

    # Guardar en JSON
    data["canales"][1]["url"] = nueva

    with open("canales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✔ Guardado en canales.json:", nueva)


# ============================================================
#   EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    main()
