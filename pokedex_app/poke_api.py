"""
Módulo para consultar y procesar información desde PokeAPI.
"""

import io
import requests
from typing import Optional, Dict, Any

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

# Mapeo de tipos Pokémon a español y colores distintivos
TYPE_TRANSLATIONS = {
    "normal": ("Normal", "#9FA19F"),
    "fire": ("Fuego", "#E62829"),
    "water": ("Agua", "#2980EF"),
    "electric": ("Eléctrico", "#FAC000"),
    "grass": ("Planta", "#3FA129"),
    "ice": ("Hielo", "#3DCEF3"),
    "fighting": ("Lucha", "#FF8000"),
    "poison": ("Veneno", "#8F41CB"),
    "ground": ("Tierra", "#915121"),
    "flying": ("Volador", "#81B9EF"),
    "psychic": ("Psíquico", "#EF4179"),
    "bug": ("Bicho", "#91A119"),
    "rock": ("Roca", "#AFA981"),
    "ghost": ("Fantasma", "#704170"),
    "dragon": ("Dragón", "#5060E1"),
    "dark": ("Siniestro", "#50413F"),
    "steel": ("Acero", "#60A1B8"),
    "fairy": ("Hada", "#EF70EF")
}

class PokemonNotFoundError(Exception):
    """Excepción cuando el Pokémon no existe en la base de datos."""
    pass

class PokeAPIConnectionError(Exception):
    """Excepción cuando ocurre un error de red o timeout."""
    pass


def fetch_pokemon(query: str | int, timeout: int = 8) -> Dict[str, Any]:
    """
    Obtiene la información detallada de un Pokémon por nombre o ID.
    
    Args:
        query: Nombre o ID del Pokémon.
        timeout: Tiempo máximo de espera en segundos.
        
    Returns:
        Diccionario con datos organizados del Pokémon.
    """
    clean_query = str(query).strip().lower().replace(" ", "-")
    if not clean_query:
        raise PokemonNotFoundError("Por favor ingresa un nombre o número de Pokédex válido.")

    pokemon_url = f"{POKEAPI_BASE_URL}/pokemon/{clean_query}"
    
    try:
        response = requests.get(pokemon_url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise PokeAPIConnectionError("No se pudo conectar con PokeAPI. Revisa tu conexión a internet.") from e

    if response.status_code == 404:
        raise PokemonNotFoundError(f"No se encontró ningún Pokémon con el identificador '{query}'.")
    elif response.status_code != 200:
        raise PokeAPIConnectionError(f"Error en el servidor de PokeAPI (Código {response.status_code}).")

    data = response.json()
    pokemon_id = data.get("id")

    # Obtener tipos formateados con color
    types = []
    for t_entry in data.get("types", []):
        t_name = t_entry.get("type", {}).get("name", "").lower()
        display_name, color = TYPE_TRANSLATIONS.get(t_name, (t_name.capitalize(), "#777777"))
        types.append({
            "name": t_name,
            "display_name": display_name,
            "color": color
        })

    # Estadísticas base
    stats = {}
    stat_mapping = {
        "hp": "PS",
        "attack": "Ataque",
        "defense": "Defensa",
        "special-attack": "Atq. Esp.",
        "special-defense": "Def. Esp.",
        "speed": "Velocidad"
    }
    for s_entry in data.get("stats", []):
        s_name = s_entry.get("stat", {}).get("name", "")
        base_val = s_entry.get("base_stat", 0)
        if s_name in stat_mapping:
            stats[stat_mapping[s_name]] = base_val

    # Habilidades
    abilities = [
        ab.get("ability", {}).get("name", "").replace("-", " ").capitalize()
        for ab in data.get("abilities", [])
    ]

    # Imagen / Sprite oficial preferida
    sprites = data.get("sprites", {})
    artwork_url = (
        sprites.get("other", {}).get("official-artwork", {}).get("front_default")
        or sprites.get("other", {}).get("home", {}).get("front_default")
        or sprites.get("front_default")
    )

    # Intentar obtener descripción desde pokemon-species
    description = "Descripción no disponible en este momento."
    try:
        species_url = f"{POKEAPI_BASE_URL}/pokemon-species/{pokemon_id}"
        species_resp = requests.get(species_url, timeout=5)
        if species_resp.status_code == 200:
            species_data = species_resp.json()
            flavor_entries = species_data.get("flavor_text_entries", [])
            
            # Buscar en español primero
            es_entry = next((e.get("flavor_text", "") for e in flavor_entries if e.get("language", {}).get("name") == "es"), None)
            if not es_entry:
                # Si no hay en español, buscar en inglés
                es_entry = next((e.get("flavor_text", "") for e in flavor_entries if e.get("language", {}).get("name") == "en"), None)
            
            if es_entry:
                # Limpiar saltos de línea molestos de los juegos clásicos
                description = " ".join(es_entry.replace("\n", " ").replace("\f", " ").replace("\r", " ").split())
    except Exception:
        # Si falla species, no detenemos el resto de la Pokédex
        pass

    return {
        "id": pokemon_id,
        "name": data.get("name", "").replace("-", " ").title(),
        "height_m": data.get("height", 0) / 10.0,
        "weight_kg": data.get("weight", 0) / 10.0,
        "types": types,
        "stats": stats,
        "abilities": abilities,
        "image_url": artwork_url,
        "description": description
    }


def download_image_bytes(url: Optional[str], timeout: int = 6) -> Optional[bytes]:
    """Descarga los bytes de una imagen desde una URL."""
    if not url:
        return None
    try:
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200:
            return res.content
    except Exception:
        return None
    return None
