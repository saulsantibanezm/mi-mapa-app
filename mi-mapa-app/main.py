from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import folium
import json

app = FastAPI(title="Mapa de México - Todos los Estados")

# Configurar templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# TODOS LOS ESTADOS DE MÉXICO con sus capitales y coordenadas
estados_mexico = {
    "aguascalientes": {"nombre": "Aguascalientes", "capital": "Aguascalientes", "lat": 21.885, "lon": -102.292, "region": "Centro-Norte"},
    "baja california": {"nombre": "Baja California", "capital": "Mexicali", "lat": 32.640, "lon": -115.478, "region": "Noroeste"},
    "baja california sur": {"nombre": "Baja California Sur", "capital": "La Paz", "lat": 24.144, "lon": -110.312, "region": "Noroeste"},
    "campeche": {"nombre": "Campeche", "capital": "San Francisco de Campeche", "lat": 19.830, "lon": -90.535, "region": "Sureste"},
    "chiapas": {"nombre": "Chiapas", "capital": "Tuxtla Gutiérrez", "lat": 16.750, "lon": -93.117, "region": "Sureste"},
    "chihuahua": {"nombre": "Chihuahua", "capital": "Chihuahua", "lat": 28.635, "lon": -106.089, "region": "Norte"},
    "ciudad de méxico": {"nombre": "Ciudad de México", "capital": "CDMX", "lat": 19.433, "lon": -99.133, "region": "Centro"},
    "coahuila": {"nombre": "Coahuila", "capital": "Saltillo", "lat": 25.426, "lon": -101.000, "region": "Noreste"},
    "colima": {"nombre": "Colima", "capital": "Colima", "lat": 19.243, "lon": -103.726, "region": "Pacífico"},
    "durango": {"nombre": "Durango", "capital": "Victoria de Durango", "lat": 24.027, "lon": -104.653, "region": "Noroeste"},
    "guanajuato": {"nombre": "Guanajuato", "capital": "Guanajuato", "lat": 21.019, "lon": -101.257, "region": "Centro"},
    "guerrero": {"nombre": "Guerrero", "capital": "Chilpancingo", "lat": 17.550, "lon": -99.500, "region": "Pacífico"},
    "hidalgo": {"nombre": "Hidalgo", "capital": "Pachuca", "lat": 20.122, "lon": -98.736, "region": "Centro"},
    "jalisco": {"nombre": "Jalisco", "capital": "Guadalajara", "lat": 20.659, "lon": -103.349, "region": "Pacífico"},
    "méxico": {"nombre": "Estado de México", "capital": "Toluca", "lat": 19.292, "lon": -99.657, "region": "Centro"},
    "michoacán": {"nombre": "Michoacán", "capital": "Morelia", "lat": 19.702, "lon": -101.192, "region": "Centro"},
    "morelos": {"nombre": "Morelos", "capital": "Cuernavaca", "lat": 18.924, "lon": -99.230, "region": "Centro"},
    "nayarit": {"nombre": "Nayarit", "capital": "Tepic", "lat": 21.500, "lon": -104.900, "region": "Pacífico"},
    "nuevo león": {"nombre": "Nuevo León", "capital": "Monterrey", "lat": 25.686, "lon": -100.316, "region": "Noreste"},
    "oaxaca": {"nombre": "Oaxaca", "capital": "Oaxaca de Juárez", "lat": 17.072, "lon": -96.719, "region": "Sureste"},
    "puebla": {"nombre": "Puebla", "capital": "Puebla", "lat": 19.041, "lon": -98.206, "region": "Centro"},
    "querétaro": {"nombre": "Querétaro", "capital": "Santiago de Querétaro", "lat": 20.588, "lon": -100.388, "region": "Centro"},
    "quintana roo": {"nombre": "Quintana Roo", "capital": "Chetumal", "lat": 21.161, "lon": -86.851, "region": "Sureste"},
    "san luis potosí": {"nombre": "San Luis Potosí", "capital": "San Luis Potosí", "lat": 22.156, "lon": -100.985, "region": "Centro"},
    "sinaloa": {"nombre": "Sinaloa", "capital": "Culiacán", "lat": 24.809, "lon": -107.394, "region": "Noroeste"},
    "sonora": {"nombre": "Sonora", "capital": "Hermosillo", "lat": 29.073, "lon": -110.956, "region": "Noroeste"},
    "tabasco": {"nombre": "Tabasco", "capital": "Villahermosa", "lat": 17.989, "lon": -92.947, "region": "Sureste"},
    "tamaulipas": {"nombre": "Tamaulipas", "capital": "Ciudad Victoria", "lat": 23.736, "lon": -99.141, "region": "Noreste"},
    "tlaxcala": {"nombre": "Tlaxcala", "capital": "Tlaxcala", "lat": 19.314, "lon": -98.237, "region": "Centro"},
    "veracruz": {"nombre": "Veracruz", "capital": "Xalapa", "lat": 19.173, "lon": -96.134, "region": "Golfo"},
    "yucatán": {"nombre": "Yucatán", "capital": "Mérida", "lat": 20.967, "lon": -89.623, "region": "Sureste"},
    "zacatecas": {"nombre": "Zacatecas", "capital": "Zacatecas", "lat": 22.770, "lon": -102.583, "region": "Centro-Norte"}
}

# Almacenar estados marcados por el usuario
estados_marcados = []
ultimas_busquedas = []

@app.get("/", response_class=HTMLResponse)
async def mostrar_mapa(request: Request):
    """Página principal con el mapa de México"""
    
    # Crear mapa centrado en México
    mapa = folium.Map(
        location=[23.634501, -102.552784],
        zoom_start=5,
        control_scale=True
    )
    
    mapa_html = mapa._repr_html_()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mapa_html": mapa_html,
        "estados_marcados": estados_marcados,
        "ultimas_busquedas": ultimas_busquedas,
        "total_estados": len(estados_mexico)
    })

@app.post("/buscar")
async def buscar_estado(request: Request, estado: str = Form(...)):
    """Buscar un estado de México y marcarlo en el mapa"""
    
    estado_busqueda = estado.lower().strip()
    mensaje = ""
    estado_encontrado = None
    
    # Buscar en todos los estados
    for key, info in estados_mexico.items():
        if estado_busqueda == key or estado_busqueda == info["nombre"].lower():
            estado_encontrado = info
            break
    
    if estado_encontrado:
        # Agregar a últimas búsquedas
        ultimas_busquedas.insert(0, {
            "nombre": estado_encontrado["nombre"],
            "capital": estado_encontrado["capital"],
            "lat": estado_encontrado["lat"],
            "lon": estado_encontrado["lon"],
            "region": estado_encontrado["region"]
        })
        # Mantener solo últimas 10 búsquedas
        if len(ultimas_busquedas) > 10:
            ultimas_busquedas.pop()
        
        # Verificar si ya está marcado
        ya_marcado = False
        for marcado in estados_marcados:
            if marcado["nombre"] == estado_encontrado["nombre"]:
                ya_marcado = True
                break
        
        if not ya_marcado:
            estados_marcados.append({
                "nombre": estado_encontrado["nombre"],
                "capital": estado_encontrado["capital"],
                "lat": estado_encontrado["lat"],
                "lon": estado_encontrado["lon"],
                "region": estado_encontrado["region"]
            })
            mensaje = f"✅ {estado_encontrado['nombre']} agregado al mapa"
        else:
            mensaje = f"ℹ️ {estado_encontrado['nombre']} ya está en el mapa"
        
        # Crear mapa centrado en el estado encontrado
        mapa = folium.Map(
            location=[estado_encontrado["lat"], estado_encontrado["lon"]],
            zoom_start=7,
            control_scale=True
        )
        
        # Agregar todos los estados marcados
        for marcado in estados_marcados:
            popup_html = f"""
            <div style="font-family: Arial; min-width: 250px;">
                <b>🏛️ {marcado['nombre']}</b><br>
                <i>Capital: {marcado['capital']}</i><br>
                <i>Región: {marcado['region']}</i><br>
                <hr>
                📍 Latitud: {marcado['lat']:.4f}<br>
                📍 Longitud: {marcado['lon']:.4f}
            </div>
            """
            
            folium.Marker(
                location=[marcado["lat"], marcado["lon"]],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{marcado['nombre']} - {marcado['region']}",
                icon=folium.Icon(color="red", icon="flag", prefix='glyphicon')
            ).add_to(mapa)
        
        # Resaltar el estado recién agregado con un círculo
        folium.Circle(
            radius=50000,  # 50 km de radio
            location=[estado_encontrado["lat"], estado_encontrado["lon"]],
            color='green',
            fill=True,
            fill_opacity=0.2,
            popup=f"✨ {estado_encontrado['nombre']} (recién agregado)"
        ).add_to(mapa)
        
    else:
        # No se encontró el estado
        mapa = folium.Map(
            location=[23.634501, -102.552784],
            zoom_start=5,
            control_scale=True
        )
        
        # Mostrar lista de estados disponibles
        lista_estados = ", ".join([e["nombre"] for e in list(estados_mexico.values())[:10]])
        mensaje = f"❌ '{estado}' no es un estado mexicano válido. Ejemplos: {lista_estados}..."
        
        # Agregar marcadores existentes
        for marcado in estados_marcados:
            folium.Marker(
                location=[marcado["lat"], marcado["lon"]],
                popup=marcado["nombre"],
                tooltip=marcado["nombre"],
                icon=folium.Icon(color="red", icon="flag", prefix='glyphicon')
            ).add_to(mapa)
    
    mapa_html = mapa._repr_html_()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mapa_html": mapa_html,
        "estados_marcados": estados_marcados,
        "ultimas_busquedas": ultimas_busquedas,
        "mensaje": mensaje,
        "ultima_busqueda": estado,
        "total_estados": len(estados_mexico)
    })

@app.post("/limpiar")
async def limpiar_mapa(request: Request):
    """Limpiar todos los estados del mapa"""
    global estados_marcados, ultimas_busquedas
    estados_marcados = []
    ultimas_busquedas = []
    
    mapa = folium.Map(
        location=[23.634501, -102.552784],
        zoom_start=5,
        control_scale=True
    )
    mapa_html = mapa._repr_html_()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mapa_html": mapa_html,
        "estados_marcados": estados_marcados,
        "ultimas_busquedas": ultimas_busquedas,
        "mensaje": "🧹 Mapa limpio. Puedes buscar nuevos estados de México.",
        "total_estados": len(estados_mexico)
    })

@app.post("/eliminar_estado")
async def eliminar_estado(request: Request, nombre: str = Form(...)):
    """Eliminar un estado específico del mapa"""
    global estados_marcados
    
    estados_marcados = [e for e in estados_marcados if e["nombre"] != nombre]
    
    # Reconstruir el mapa
    mapa = folium.Map(
        location=[23.634501, -102.552784],
        zoom_start=5,
        control_scale=True
    )
    
    for marcado in estados_marcados:
        folium.Marker(
            location=[marcado["lat"], marcado["lon"]],
            popup=marcado["nombre"],
            tooltip=marcado["nombre"],
            icon=folium.Icon(color="red", icon="flag", prefix='glyphicon')
        ).add_to(mapa)
    
    mapa_html = mapa._repr_html_()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mapa_html": mapa_html,
        "estados_marcados": estados_marcados,
        "ultimas_busquedas": ultimas_busquedas,
        "mensaje": f"🗑️ {nombre} eliminado del mapa",
        "total_estados": len(estados_mexico)
    })

@app.get("/api/estados")
async def obtener_estados():
    """API para obtener todos los estados de México"""
    return {"total": len(estados_mexico), "estados": list(estados_mexico.keys())}

@app.get("/api/estados_marcados")
async def obtener_estados_marcados():
    """API para obtener los estados marcados"""
    return {"total": len(estados_marcados), "estados": estados_marcados}