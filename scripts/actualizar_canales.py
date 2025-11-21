#!/usr/bin/env python3
import json
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def obtener_url_willax():
    try:
        print("→ Buscando URL dinámica de Willax...")

        meta_url = "https://www.dailymotion.com/player/metadata/video/x9s3ad6"
        r = requests.get(meta_url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            print("✖ No se pudo obtener metadata de Dailymotion")
            return None

        data = r.json()

        streams = data.get("qualities", {})
        if not streams:
            print("✖ Dailymotion no devolvió calidades")
            return None

        # Prioridad
        prioridades = ["720", "480", "380", "240", "144"]

        for calidad in prioridades:
            if calidad in streams:
                for item in streams[calidad]:
                    if item.get("type") == "application/x-mpegURL":
                        print(f"✔ Willax ({calidad}p): {item['url']}")
                        return item["url"]

        print("✖ No se encontró ninguna URL .m3u8 válida en metadata.")
        return None

    except Exception as e:
        print("Error:", e)
        return None


def main():
    print("Iniciando actualización de canales...")

    with open("canales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cambios = False

    for canal in data["canales"]:
        nombre = canal["nombre"]

        if nombre.lower() == "willax":
            nueva_url = obtener_url_willax()

            if nueva_url and nueva_url != canal["url"]:
                canal["url"] = nueva_url
                cambios = True
            continue

        print(f"→ Canal sin actualización automática: {nombre}")

    if cambios:
        with open("canales.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("✔ canales.json actualizado con nuevas URLs.")
    else:
        print("No hubo cambios.")


if __name__ == "__main__":
    main()
