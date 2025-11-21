def obtener_url_willax():
    try:
        print("→ Buscando URL dinámica de Willax...")

        # URL fija del reproductor Dailymotion
        embed_url = "https://www.dailymotion.com/embed/video/x9s3ad6"

        headers = { "User-Agent": "Mozilla/5.0" }
        r = requests.get(embed_url, headers=headers, timeout=10)

        if r.status_code != 200:
            print("✖ No se pudo acceder al embed de Willax.")
            return None

        # Buscar cualquier .m3u8 que aparezca en el HTML
        m3u8_urls = re.findall(r'https?://[^"\']+\.m3u8', r.text)

        if not m3u8_urls:
            print("✖ No se encontró ningún .m3u8 en Dailymotion.")
            return None

        # Priorizar la de mayor calidad
        for calidad in ["live-720.m3u8", "live-480.m3u8", "live-240.m3u8"]:
            for url in m3u8_urls:
                if calidad in url:
                    print(f"✔ Willax actualizado: {url}")
                    return url

        print("✔ Se encontró una URL .m3u8, pero sin calidad específica.")
        return m3u8_urls[0]

    except Exception as e:
        print("Error:", e)
        return None
