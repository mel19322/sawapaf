import requests
import xml.etree.ElementTree as ET
from datetime import datetime

API_URL = "https://epg.tbxapis.com/v0/epg/external/entries"

# AQUÍ DEFINES TUS NOMBRES PERSONALIZADOS
# A la izquierda el número de la API original, a la derecha el nombre que quieres usar en tu M3U
MIS_IDS_CUSTOM = {
    "1610": "dsports.ar",
    "1612": "dsports2.ar",
    "1613": "dsports_plus.ar",
    "1614": "dsports_motors.ar" # Agrega o modifica los que necesites
}

def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()
    return response.json()

def format_xmltv_date(iso_date_str):
    dt = datetime.fromisoformat(iso_date_str)
    return dt.strftime('%Y%m%d%H%M%S %z')

def generate_xmltv():
    print("Obteniendo datos de la API...")
    payload = fetch_data()
    
    if not payload.get("ok") or "data" not in payload:
        print("Error: La API no devolvió los datos esperados.")
        return

    data = payload["data"]
    tv = ET.Element("tv", {"generator-info-name": "Mi EPG Custom"})

    print("Procesando canales...")
    for ch in data.get("channels", []):
        numero_original = ch["ChannelNumber"]
        
        # MAGIA AQUÍ: Si el número está en tu diccionario, usa tu nombre custom. 
        # Si no está, usa el número original por defecto para evitar errores.
        mi_id_final = MIS_IDS_CUSTOM.get(numero_original, numero_original)
        
        channel_el = ET.SubElement(tv, "channel", {"id": mi_id_final})
        
        display_name = ET.SubElement(channel_el, "display-name")
        display_name.text = ch["ChannelName"]
        
        if "ChannelLogo" in ch and ch["ChannelLogo"]:
            ET.SubElement(channel_el, "icon", {"src": ch["ChannelLogo"]})

    print("Procesando programas...")
    for prog in data.get("programs", []):
        numero_original = prog["ChannelNum"]
        
        # MAGIA AQUÍ: Convierte también el ID de los programas para que coincida perfectamente
        mi_id_final = MIS_IDS_CUSTOM.get(numero_original, numero_original)
        
        start_time = format_xmltv_date(prog["StartDate"])
        end_time = format_xmltv_date(prog["EndDate"])
        
        programme_el = ET.SubElement(tv, "programme", {
            "start": start_time,
            "stop": end_time,
            "channel": mi_id_final  # Usamos el nombre customizado
        })
        
        title_el = ET.SubElement(programme_el, "title")
        title_el.text = prog["Title"].strip()
        
        if "Category" in prog and prog["Category"]:
            category_el = ET.SubElement(programme_el, "category")
            category_el.text = prog["Category"]
            
        if "SubCategory" in prog and prog["SubCategory"]:
            subcategory_el = ET.SubElement(programme_el, "category")
            subcategory_el.text = prog["SubCategory"]
            
        if "ImageURL" in prog and prog["ImageURL"]:
            ET.SubElement(programme_el, "icon", {"src": prog["ImageURL"]})

    output_filename = "dsports_guia.xml"
    tree = ET.ElementTree(tv)
    ET.indent(tree, space="  ", level=0)
    
    with open(output_filename, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)
        
    print(f"¡Éxito! Archivo guardado como {output_filename}")

if __name__ == "__main__":
    generate_xmltv()
