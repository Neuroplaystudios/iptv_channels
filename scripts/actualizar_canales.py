import requests
import json
import re

URL_M3U8_WILLAX = "https://willax.tv/senal-en-vivo/"
RUTA_JSON = "canales.json"

def obtener_url_willax():
    try:
        html = requests.get(URL_M3U8_WILLAX, timeout=10).text
        urls = re.findall(r'https://[^"]+\.m3u8', html)
        # De todos los .m3u8 escogemos el más largo (suele ser el válido)
        mejor_url = max(urls, key=len)
        return mejor_url
    except:
        return None

def actualizar_json():
    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        nueva_url = obtener_url_willax()

        if nueva_url:
            for canal in data["canales"]:
                if canal["nombre"] == "Willax":
                    canal["url"] = nueva_url

            with open(RUTA_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print("✔ Willax actualizado correctamente:", nueva_url)
        else:
            print("✖ No se pudo obtener la URL de Willax.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    actualizar_json()
