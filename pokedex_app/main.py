"""
Aplicación de escritorio con Tkinter y PokeAPI.
Interfaz moderna con diseño inspirado en Pokémon.
"""

import io
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from poke_api import (
    fetch_pokemon,
    download_image_bytes,
    PokemonNotFoundError,
    PokeAPIConnectionError
)


class PokedexApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Pokédex - Pokémon Edition")
        self.root.geometry("920x680")
        self.root.minsize(880, 640)
        self.root.configure(bg="#DC0A2D")

        # Estado interno
        self.current_pokemon_id = 1
        self.is_loading = False
        self.photo_reference = None  # Evita que el recolector de basura elimine la imagen
        self.loading_animation_id = None
        self.loading_step = 0

        # Paleta de colores
        self.colors = {
            "pokedex_red": "#DC0A2D",
            "pokedex_dark_red": "#A8001F",
            "screen_bg": "#1E2024",
            "card_bg": "#2A2D34",
            "card_inner": "#353842",
            "text_primary": "#FFFFFF",
            "text_secondary": "#B0B4BC",
            "accent_blue": "#29B6F6",
            "accent_green": "#4CAF50",
            "accent_yellow": "#FFD54F",
            "accent_red": "#EF5350",
            "border_color": "#18191C"
        }

        self._setup_ui()
        
        # Cargar Pokémon inicial (Pikachu por defecto para una primera vista llamativa)
        self.search_pokemon("pikachu")

    def _setup_ui(self):
        """Configuración general de la interfaz gráfica."""
        # Contenedor principal con márgenes
        main_container = tk.Frame(self.root, bg=self.colors["pokedex_red"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # 1. Cabecera estilo Pokédex
        self._build_header(main_container)

        # 2. Barra de búsqueda y accesos rápidos
        self._build_search_bar(main_container)

        # 3. Contenedor de contenido (Panel Izquierdo: Pantalla/Foto; Panel Derecho: Info/Stats)
        content_frame = tk.Frame(main_container, bg=self.colors["pokedex_red"])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 8))

        # Configurar proporción 50/50 o 45/55
        content_frame.columnconfigure(0, weight=4, uniform="group1")
        content_frame.columnconfigure(1, weight=5, uniform="group1")
        content_frame.rowconfigure(0, weight=1)

        self._build_left_panel(content_frame)
        self._build_right_panel(content_frame)

        # 4. Barra de estado inferior
        self._build_status_bar(main_container)

    def _build_header(self, parent: tk.Frame):
        """Cabecera con las clásicas luces de la Pokédex y título."""
        header_frame = tk.Frame(parent, bg=self.colors["pokedex_red"])
        header_frame.pack(fill=tk.X, pady=(0, 8))

        # Canvas para luces decorativas
        lights_canvas = tk.Canvas(header_frame, width=170, height=52, bg=self.colors["pokedex_red"], highlightthickness=0)
        lights_canvas.pack(side=tk.LEFT)

        # Lente azul grande con borde y brillo
        lights_canvas.create_oval(8, 6, 48, 46, fill="#FFFFFF", outline="#18191C", width=3)
        lights_canvas.create_oval(11, 9, 45, 43, fill=self.colors["accent_blue"], outline="")
        lights_canvas.create_oval(16, 14, 26, 24, fill="#81D4FA", outline="")  # Brillo

        # Pequeños LEDs (Rojo, Amarillo, Verde)
        lights_canvas.create_oval(60, 12, 74, 26, fill=self.colors["accent_red"], outline="#800000", width=1.5)
        lights_canvas.create_oval(82, 12, 96, 26, fill=self.colors["accent_yellow"], outline="#8D6E00", width=1.5)
        lights_canvas.create_oval(104, 12, 118, 26, fill=self.colors["accent_green"], outline="#1B5E20", width=1.5)

        # Título principal
        title_label = tk.Label(
            header_frame,
            text="POKÉDEX",
            font=("Segoe UI", 22, "bold"),
            fg="#FFFFFF",
            bg=self.colors["pokedex_red"]
        )
        title_label.pack(side=tk.LEFT, padx=10)

        subtitle_label = tk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg="#FFCDD2",
            bg=self.colors["pokedex_red"]
        )
        subtitle_label.pack(side=tk.LEFT, pady=(8, 0))

    def _build_search_bar(self, parent: tk.Frame):
        """Barra de búsqueda con entrada, botón y accesos directos."""
        search_card = tk.Frame(parent, bg=self.colors["pokedex_dark_red"], padx=10, pady=8)
        search_card.pack(fill=tk.X)

        search_label = tk.Label(
            search_card,
            text="Buscar:",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg=self.colors["pokedex_dark_red"]
        )
        search_label.pack(side=tk.LEFT, padx=(4, 8))

        # Campo de texto de búsqueda
        self.search_entry = tk.Entry(
            search_card,
            font=("Segoe UI", 11),
            bg="#FFFFFF",
            fg="#1E2024",
            insertbackground="#1E2024",
            relief=tk.FLAT,
            width=22
        )
        self.search_entry.pack(side=tk.LEFT, ipady=4, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._on_search_click())

        # Botón de buscar
        self.search_button = tk.Button(
            search_card,
            text="🔎 Buscar",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent_blue"],
            fg="#FFFFFF",
            activebackground="#0288D1",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=3,
            cursor="hand2",
            command=self._on_search_click
        )
        self.search_button.pack(side=tk.LEFT, padx=(0, 16))

        # Accesos rápidos sugeridos en el requerimiento
        shortcuts_label = tk.Label(
            search_card,
            text="Populares:",
            font=("Segoe UI", 9),
            fg="#FFCDD2",
            bg=self.colors["pokedex_dark_red"]
        )
        shortcuts_label.pack(side=tk.LEFT, padx=(0, 6))

        popular_monsters = ["Pikachu", "Charizard", "Gengar", "Lucario"]
        for p in popular_monsters:
            btn = tk.Button(
                search_card,
                text=p,
                font=("Segoe UI", 9),
                bg="#8A0019",
                fg="#FFFFFF",
                activebackground="#A8001F",
                activeforeground="#FFFFFF",
                relief=tk.FLAT,
                cursor="hand2",
                padx=6,
                pady=1,
                command=lambda name=p: self.search_pokemon(name)
            )
            btn.pack(side=tk.LEFT, padx=3)

    def _build_left_panel(self, parent: tk.Frame):
        """Panel izquierdo: Marco visual de pantalla, sprite del Pokémon, nombre, tipo y navegación."""
        left_frame = tk.Frame(parent, bg=self.colors["card_bg"], bd=0, padx=12, pady=12)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Marco interior que emula una pantalla digital retro/moderna
        screen_frame = tk.Frame(left_frame, bg=self.colors["screen_bg"], bd=2, relief=tk.SOLID)
        screen_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ID y Nombre del Pokémon
        self.pokemon_name_label = tk.Label(
            screen_frame,
            text="---",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors["text_primary"],
            bg=self.colors["screen_bg"]
        )
        self.pokemon_name_label.pack(pady=(12, 4))

        # Canvas para la imagen del Pokémon (o fallback si no carga)
        self.image_canvas = tk.Canvas(
            screen_frame,
            width=230,
            height=230,
            bg="#2B2F38",
            highlightthickness=1,
            highlightbackground="#40444F"
        )
        self.image_canvas.pack(pady=6)
        self._draw_placeholder("Iniciando Pokédex...")

        # Contenedor de tipos (badges coloreados)
        self.types_container = tk.Frame(screen_frame, bg=self.colors["screen_bg"])
        self.types_container.pack(pady=8)

        # Dimensiones físicas (Altura / Peso)
        self.dimensions_label = tk.Label(
            screen_frame,
            text="Altura: -- m  |  Peso: -- kg",
            font=("Segoe UI", 10),
            fg=self.colors["text_secondary"],
            bg=self.colors["screen_bg"]
        )
        self.dimensions_label.pack(pady=(2, 10))

        # Botones de navegación Anterior / Siguiente
        nav_frame = tk.Frame(left_frame, bg=self.colors["card_bg"])
        nav_frame.pack(fill=tk.X, pady=(10, 2))

        self.btn_prev = tk.Button(
            nav_frame,
            text="◀ Anterior",
            font=("Segoe UI", 10, "bold"),
            bg="#3F424E",
            fg="#FFFFFF",
            activebackground="#505463",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._on_prev_click
        )
        self.btn_prev.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.btn_next = tk.Button(
            nav_frame,
            text="Siguiente ▶",
            font=("Segoe UI", 10, "bold"),
            bg="#3F424E",
            fg="#FFFFFF",
            activebackground="#505463",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._on_next_click
        )
        self.btn_next.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(4, 0))

    def _build_right_panel(self, parent: tk.Frame):
        """Panel derecho: Descripción, Habilidades y Estadísticas con barras de progreso."""
        right_frame = tk.Frame(parent, bg=self.colors["card_bg"], padx=16, pady=14)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # 1. Sección Descripción
        desc_title = tk.Label(
            right_frame,
            text="📖 Descripción Pokédex",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["accent_yellow"],
            bg=self.colors["card_bg"]
        )
        desc_title.pack(anchor="w", pady=(0, 4))

        desc_container = tk.Frame(right_frame, bg=self.colors["card_inner"], padx=10, pady=8)
        desc_container.pack(fill=tk.X, pady=(0, 10))

        self.desc_label = tk.Label(
            desc_container,
            text="Cargando descripción...",
            font=("Segoe UI", 9),
            fg=self.colors["text_primary"],
            bg=self.colors["card_inner"],
            wraplength=380,
            justify=tk.LEFT
        )
        self.desc_label.pack(anchor="w", fill=tk.X)

        # 2. Sección Habilidades
        hab_title = tk.Label(
            right_frame,
            text="✨ Habilidades",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["accent_blue"],
            bg=self.colors["card_bg"]
        )
        hab_title.pack(anchor="w", pady=(2, 4))

        hab_container = tk.Frame(right_frame, bg=self.colors["card_inner"], padx=10, pady=6)
        hab_container.pack(fill=tk.X, pady=(0, 12))

        self.abilities_label = tk.Label(
            hab_container,
            text="--",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg=self.colors["card_inner"],
            wraplength=380,
            justify=tk.LEFT
        )
        self.abilities_label.pack(anchor="w")

        # 3. Sección Estadísticas Base
        stats_title = tk.Label(
            right_frame,
            text="📊 Estadísticas Base",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["accent_green"],
            bg=self.colors["card_bg"]
        )
        stats_title.pack(anchor="w", pady=(2, 6))

        stats_container = tk.Frame(right_frame, bg=self.colors["card_inner"], padx=12, pady=10)
        stats_container.pack(fill=tk.BOTH, expand=True)

        self.stat_widgets = {}
        stat_names = ["PS", "Ataque", "Defensa", "Atq. Esp.", "Def. Esp.", "Velocidad"]

        for i, s_name in enumerate(stat_names):
            row_frame = tk.Frame(stats_container, bg=self.colors["card_inner"])
            row_frame.pack(fill=tk.X, pady=3)

            # Nombre de la estadística
            lbl_name = tk.Label(
                row_frame,
                text=s_name,
                font=("Segoe UI", 9, "bold"),
                fg=self.colors["text_secondary"],
                bg=self.colors["card_inner"],
                width=10,
                anchor="w"
            )
            lbl_name.pack(side=tk.LEFT)

            # Valor numérico
            lbl_val = tk.Label(
                row_frame,
                text="0",
                font=("Segoe UI", 9, "bold"),
                fg="#FFFFFF",
                bg=self.colors["card_inner"],
                width=4,
                anchor="e"
            )
            lbl_val.pack(side=tk.LEFT, padx=(0, 8))

            # Barra visual de progreso personalizada
            bar_canvas = tk.Canvas(
                row_frame,
                width=180,
                height=12,
                bg="#23252B",
                highlightthickness=0
            )
            bar_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.stat_widgets[s_name] = {
                "val_lbl": lbl_val,
                "canvas": bar_canvas
            }

        # Resumen de suma total
        total_frame = tk.Frame(stats_container, bg=self.colors["card_inner"])
        total_frame.pack(fill=tk.X, pady=(8, 0))

        self.total_stats_label = tk.Label(
            total_frame,
            text="Total Base: 0",
            font=("Segoe UI", 9, "italic"),
            fg=self.colors["text_secondary"],
            bg=self.colors["card_inner"]
        )
        self.total_stats_label.pack(side=tk.RIGHT)

    def _build_status_bar(self, parent: tk.Frame):
        """Barra de estado para mensajes de carga y errores."""
        status_frame = tk.Frame(parent, bg=self.colors["pokedex_red"], pady=4)
        status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text="Pokédex lista para consultar.",
            font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF",
            bg=self.colors["pokedex_red"],
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _set_loading_state(self, is_loading: bool, message: str = ""):
        """Activa o desactiva el estado de carga para no congelar la UI."""
        self.is_loading = is_loading
        state = tk.DISABLED if is_loading else tk.NORMAL

        self.search_button.config(state=state)
        self.btn_prev.config(state=state)
        self.btn_next.config(state=state)

        if is_loading:
            self._start_loading_animation(message)
        else:
            self._stop_loading_animation(message)

    def _start_loading_animation(self, base_message: str):
        """Efecto visual dinámico de puntos en la barra de estado."""
        self.loading_step = (self.loading_step + 1) % 4
        dots = "." * self.loading_step
        self.status_label.config(text=f"⏳ {base_message}{dots}", fg=self.colors["accent_yellow"])
        self.loading_animation_id = self.root.after(350, lambda: self._start_loading_animation(base_message))

    def _stop_loading_animation(self, final_message: str):
        """Detiene la animación de carga."""
        if self.loading_animation_id:
            self.root.after_cancel(self.loading_animation_id)
            self.loading_animation_id = None
        self.status_label.config(text=final_message, fg="#FFFFFF")

    def search_pokemon(self, query: str | int):
        """Inicia la búsqueda en un hilo secundario para evitar congelamientos."""
        if self.is_loading:
            return

        self._set_loading_state(True, f"Consultando '{query}' en PokeAPI")

        # Ejecutar petición en un hilo daemon
        thread = threading.Thread(
            target=self._fetch_worker,
            args=(query,),
            daemon=True
        )
        thread.start()

    def _fetch_worker(self, query: str | int):
        """Trabajo en segundo plano: descarga datos e imagen."""
        try:
            pokemon_data = fetch_pokemon(query)
            image_bytes = None
            if pokemon_data.get("image_url"):
                image_bytes = download_image_bytes(pokemon_data["image_url"])

            # Enviar actualización segura al hilo principal de Tkinter
            self.root.after(0, self._render_pokemon_data, pokemon_data, image_bytes)
        except PokemonNotFoundError as pne:
            self.root.after(0, self._handle_error, str(pne), "#FFE082")
        except PokeAPIConnectionError as pce:
            self.root.after(0, self._handle_error, str(pce), "#FF8A80")
        except Exception as e:
            self.root.after(0, self._handle_error, f"Error inesperado: {str(e)}", "#FF8A80")

    def _render_pokemon_data(self, data: Dict[str, Any], image_bytes: Optional[bytes]):
        """Actualiza todos los componentes de la interfaz con los nuevos datos."""
        self.current_pokemon_id = data["id"]
        
        # 1. Nombre y Número
        formatted_id = f"#{data['id']:04d}"
        self.pokemon_name_label.config(text=f"{formatted_id} {data['name']}")

        # 2. Renderizar imagen o fallback
        self._display_image(image_bytes, data["name"])

        # 3. Badges de tipo
        for widget in self.types_container.winfo_children():
            widget.destroy()

        for t_info in data.get("types", []):
            badge = tk.Label(
                self.types_container,
                text=f"  {t_info['display_name'].upper()}  ",
                font=("Segoe UI", 9, "bold"),
                bg=t_info["color"],
                fg="#FFFFFF",
                bd=0,
                padx=6,
                pady=2
            )
            badge.pack(side=tk.LEFT, padx=3)

        # 4. Dimensiones
        self.dimensions_label.config(
            text=f"Altura: {data['height_m']} m  |  Peso: {data['weight_kg']} kg"
        )

        # 5. Descripción y Habilidades
        self.desc_label.config(text=data.get("description", "Sin descripción."))
        
        abilities_text = ", ".join(data.get("abilities", [])) or "Ninguna conocida"
        self.abilities_label.config(text=abilities_text)

        # 6. Estadísticas y Barras de progreso
        stats = data.get("stats", {})
        total_sum = 0
        max_stat_cap = 200.0  # Referencia para calcular el ancho de barra

        for s_name, widget_group in self.stat_widgets.items():
            val = stats.get(s_name, 0)
            total_sum += val
            widget_group["val_lbl"].config(text=str(val))

            # Dibujar barra en el Canvas
            canvas = widget_group["canvas"]
            canvas.delete("all")
            canvas_width = canvas.winfo_width()
            if canvas_width <= 1:
                canvas_width = 180  # Valor predeterminado antes del primer render

            # Color según magnitud de la estadística
            if val >= 100:
                bar_color = "#4CAF50"  # Verde fuerte
            elif val >= 65:
                bar_color = "#FFCA28"  # Amarillo / Ámbar
            elif val >= 45:
                bar_color = "#FF9800"  # Naranja
            else:
                bar_color = "#F44336"  # Rojo

            fill_width = max(4, int((val / max_stat_cap) * canvas_width))
            fill_width = min(canvas_width, fill_width)

            # Fondo gris oscuro
            canvas.create_rectangle(0, 0, canvas_width, 12, fill="#23252B", outline="")
            # Relleno de estadística
            canvas.create_rectangle(0, 0, fill_width, 12, fill=bar_color, outline="")

        self.total_stats_label.config(text=f"Total Base: {total_sum}")

        # Finalizar estado de carga
        self._set_loading_state(False, f"✅ Mostrando a {data['name']} (#{data['id']:04d})")

    def _display_image(self, image_bytes: Optional[bytes], pokemon_name: str):
        """Muestra la imagen procesada o dibuja un placeholder si no está disponible."""
        self.image_canvas.delete("all")

        if image_bytes and PIL_AVAILABLE:
            try:
                img_data = io.BytesIO(image_bytes)
                pil_image = Image.open(img_data)
                pil_image = pil_image.resize((210, 210), Image.Resampling.LANCZOS)
                self.photo_reference = ImageTk.PhotoImage(pil_image)
                self.image_canvas.create_image(115, 115, image=self.photo_reference)
                return
            except Exception:
                pass

        # Si no hay imagen o Pillow falló, dibujar placeholder estilo Pokéball
        self._draw_placeholder(f"Sin imagen de\n{pokemon_name}")

    def _draw_placeholder(self, message: str):
        """Dibuja un gráfico alternativo con diseño de Pokéball en el canvas."""
        self.photo_reference = None
        self.image_canvas.delete("all")

        # Círculo base de la Pokéball
        cx, cy, r = 115, 100, 48
        self.image_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#3A3E4A", outline="#505666", width=3)
        self.image_canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=0, extent=180, fill="#E53935", outline="#505666", width=2)
        self.image_canvas.create_line(cx - r, cy, cx + r, cy, fill="#505666", width=4)
        self.image_canvas.create_oval(cx - 12, cy - 12, cx + 12, cy + 12, fill="#FFFFFF", outline="#505666", width=3)
        self.image_canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#3A3E4A", outline="")

        # Mensaje explicativo
        self.image_canvas.create_text(
            115, 180,
            text=message,
            fill=self.colors["text_secondary"],
            font=("Segoe UI", 9, "bold"),
            justify=tk.CENTER
        )

    def _handle_error(self, error_message: str, color_hex: str):
        """Maneja los errores sin bloquear ni cerrar la aplicación."""
        self._set_loading_state(False, f"⚠️ {error_message}")
        self.status_label.config(fg=color_hex)
        
        # Opcional: mostrar notificación visual o mantener la vista actual
        # Dejamos el foco en la barra de búsqueda para reintentar fácilmente
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)

    def _on_search_click(self):
        """Evento al hacer clic en Buscar o presionar Enter."""
        query = self.search_entry.get().strip()
        if not query:
            self._handle_error("Por favor escribe un nombre o número de Pokédex.", "#FFE082")
            return
        self.search_pokemon(query)

    def _on_prev_click(self):
        """Navegar al Pokémon anterior."""
        if self.current_pokemon_id > 1:
            self.search_pokemon(self.current_pokemon_id - 1)
        else:
            self._handle_error("Ya te encuentras en el primer Pokémon (#0001).", "#FFE082")

    def _on_next_click(self):
        """Navegar al Pokémon siguiente."""
        self.search_pokemon(self.current_pokemon_id + 1)


def main():
    root = tk.Tk()
    
    # Intentar aplicar icono temático si la plataforma lo soporta
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    app = PokedexApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
