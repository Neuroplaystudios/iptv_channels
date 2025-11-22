#!/usr/bin/env python3
import json
import asyncio
import os
from playwright.async_api import async_playwright

# ============================================================
#   FILTRO DE URLS: SOLO STREAM REAL, NO PUBLICIDAD
# ============================================================
def es_stream_real(url: str) -> bool:
    if ".m3u8" not in url:
        return False

    # ❌ Filtrar publicidad
    if any(x in url.lower() for x in [
        "vmap", "vast", "ad", "ads", "doubleclick", "pub", "dmxleo"
    ]):
        return False

    # ✔ Streams reales
    return any(x in url for x in [
        "live-480.m3u8",
        "live-720.m3u8",
        "master.m3u8",
        "/live/",
    ])


# ============================================================
#   FUNCIÓN LIMPIAR PUBLICIDAD
# ============================================================
async def limpiar_publicidad(page):

    print("\n========================================")
    print(" 🧹 INICIO → LIMPIEZA DE PUBLICIDAD")
    print("========================================\n")

    await page.wait_for_timeout(3000)

    posibles_cierres = [
        "text=X",
        "text=×",
        "text=Cerrar",
        "button[aria-label='Close']",
        ".close-btn",
        ".ad-close",
        ".adm-close",
        "iframe[src*='google']"
    ]

    for selector in posibles_cierres:
        try:
            loc = page.locator(selector).first
            if await loc.is_visible(timeout=1500):
                print(f"[LOG] → Cerrando popup: {selector}")
                await loc.click()
                await page.wait_for_timeout(500)
        except:
            pass

    # Eliminar overlays con z-index alto
    try:
        await page.evaluate("""
            document.querySelectorAll('*').forEach(el => {
                const z = window.getComputedStyle(el).zIndex;
                if (z !== 'auto' && parseInt(z) > 999) el.remove();
            });
        """)
        print(" ✔ Overlays eliminados")
    except:
        print(" ✖ No fue posible eliminar overlays")

    print("\n========================================")
    print(" 🧹 FIN → PUBLICIDAD LIMPIADA")
    print("========================================\n")


# ============================================================
#   OBTENER STREAM REAL DE WILLAX
# ============================================================
async def obtener_url_willax():

    print("\n========================================")
    print(" 🚀 INICIO → OBTENER STREAM DE WILLAX")
    print("========================================\n")

    async with async_playwright() as p:
        esta_en_github = os.environ.get("GITHUB_ACTIONS") == "true"

        browser = await p.chromium.launch(
            headless=False,  # 👈 SIEMPRE EN MODO NORMAL (NO HEADLESS)
            slow_mo=0,
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
        )

        page = await context.new_page()
        page._streams_reales = []

        # 💥 LOG: Registrar TODAS las peticiones
        def registrar_todo(request):
            print(f"[REQ] → {request.url}")
        page.on("request", registrar_todo)

        # Captura de peticiones filtradas
        def capturar(request):
            url = request.url

            if ".m3u8" in url:
                print(f"[M3U8] Detectado: {url}")

            if es_stream_real(url):
                print(f"🔥 STREAM REAL DETECTADO → {url}")
                page._streams_reales.append(url)

        page.on("request", capturar)

        # Cargar página
        print("[LOG] → Cargando Willax...")
        await page.goto("https://willax.pe/en-vivo", timeout=60000)

        # Screenshots de debugging en GitHub
        if esta_en_github:
            try:
                await page.screenshot(path="debug_inicial.png")
                print("📸 Screenshot: debug_inicial.png guardado")
            except:
                pass

        # LIMPIEZA DE PUBLICIDAD
        await limpiar_publicidad(page)

        if esta_en_github:
            try:
                await page.screenshot(path="debug_post_ads.png")
                print("📸 Screenshot: debug_post_ads.png guardado")
            except:
                pass

        # LOG extra: ¿existe un video tag?
        try:
            video_count = await page.locator("video").count()
            print(f"[LOG] → Cantidad de <video>: {video_count}")
        except:
            print("[LOG] → No se pudo verificar <video>")

        # LOG extra: iframes
        try:
            frames = page.frames
            print(f"[LOG] → Cantidad de iframes detectados: {len(frames)}")
            for f in frames:
                print("   - Frame:", f.url)
        except:
            pass

        # Intentar presionar PLAY
        try:
            print("[LOG] → Intentando presionar Play...")
            await page.click("button", timeout=4000)
        except:
            print("[LOG] → No se necesitó Play")

        # Esperar streaming
        print("[LOG] → Esperando URLs reales...")
        for i in range(30):
            if page._streams_reales:
                break
            await asyncio.sleep(1)

        await browser.close()

        # Resultado
        if page._streams_reales:
            final = page._streams_reales[-1]
            print("✔ STREAM FINAL:", final)
            return final

        print("✖ No se encontró stream real")
        return "N/A"


# ============================================================
#   PROGRAMA PRINCIPAL
# ============================================================
def main():

    print("\n========================================")
    print(" 🟦 INICIO → ACTUALIZACIÓN DE CANALES")
    print("========================================\n")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    nueva = asyncio.run(obtener_url_willax())

    print("[LOG] → Nueva URL capturada:", nueva)

    data["canales"][1]["url"] = nueva

    with open("canales.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n========================================")
    print(" ✔ PROCESO COMPLETADO — Archivo actualizado")
    print("========================================\n")


if __name__ == "__main__":
    main()
