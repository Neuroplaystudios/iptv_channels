#!/usr/bin/env python3
import json
import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def obtener_url_willax():
    try:
        print("→ Buscando URL dinámica de Willax...")

        # URL oficial del video Dailymotion
        embed_url = "https://www.dailymotion.com/embed/video/x9s3ad6"

        r = requests.get(embed_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print("✖ No se pudo acceder al embed.")
            return None

        # Buscar TODAS las m3u8 presentes
        m3u8_urls = re.findall(r'https?://[^"\']+\.m3u8', r.text)

        if not m3u8_urls:
            print("✖ No se encontró ninguna .m3u8.")
            return None

        # Elegir la de mayor calidad
        prioridades = ["live-720.m3u8", "live-480.m3u8", "live-240.m3u8"]
        for calidad in prioridades:
            for url in m3u8_urls:
                if calidad in url:
                    print(f"✔ Willax actualizado: {url}")
                    return url

        print("✔ Se encontró URL .m3u8, pero no calidad específica.")
        return m3u8_urls[0]

    except Exception as e:
        print("Error al obtener Willax:", e)
        return None


def main():
    print("Iniciando actualización...")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cambios = False

    # Actualizar Willax
    nueva = obtener_url_willax()
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
