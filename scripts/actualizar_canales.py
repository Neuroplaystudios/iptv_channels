import requests
import json

def obtener_url_willax():
    try:
        print("→ Buscando URL dinámica de Willax...")

        # ID fijo del canal Willax en Dailymotion (x9s3ad6)
        video_id = "x9s3ad6"

        # API oficial de Dailymotion
        api_url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(api_url, headers=headers, timeout=10)

        if r.status_code != 200:
            print("✖ Error obteniendo metadata de Dailymotion.")
            return None

        data = r.json()

        # Navegar la estructura para obtener la calidad más alta disponible
        try:
            qualities = data["qualities"]
        except:
            print("✖ No se encontraron calidades en la metadata.")
            return None

        # Orden de calidad prioridad
        prioridad = ["720", "480", "380", "240", "144"]

        for q in prioridad:
            if q in qualities:
                streams = qualities[q]
                # Tomar la primera URL .m3u8 válida
                for stream in streams:
                    if "url" in stream and stream["type"] == "application/x-mpegURL":
                        print(f"✔ Willax actualizado: {stream['url']}")
                        return stream["url"]

        print("✖ No se encontró ninguna URL de stream válida.")
        return None

    except Exception as e:
        print("❌ Error:", e)
        return None
