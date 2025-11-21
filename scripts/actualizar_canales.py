import requests
import json

def obtener_url_willax():
    try:
        print("→ Obteniendo URL dinámica de Willax desde metadata JSON...")

        meta_url = "https://www.dailymotion.com/player/metadata/video/x9s3ad6"
        headers = { "User-Agent": "Mozilla/5.0" }

        r = requests.get(meta_url, headers=headers, timeout=10)

        if r.status_code != 200:
            print("✖ No se pudo acceder al metadata de Willax.")
            return None

        data = r.json()

        # Navegar hasta encontrar streams HLS
        streams = data.get("qualities", {})

        # Buscar la mejor calidad disponible
        for quality in ["720", "480", "380", "240", "144"]:
            if quality in streams:
                for entry in streams[quality]:
                    if entry.get("type") == "application/x-mpegURL":
                        url = entry.get("url")
                        print(f"✔ Willax actualizado: {url}")
                        return url

        print("✖ No se encontró un stream HLS en la metadata.")
        return None

    except Exception as e:
        print("Error obteniendo Willax:", e)
        return None
