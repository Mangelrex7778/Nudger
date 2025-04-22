import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import time
import threading
import os
import json
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import hashlib
import base64
import pyautogui
from googletrans import Translator

current_theme = "light"  # Tema por defecto
current_effect = "glass"  # Efecto Inicial
windowed_mode = False  # Iniciar en pantalla completa
custom_resolution = False
selected_resolution = (1920, 1080)  # Resolución inicial (ajústala según tus necesidades)
language_config_active = False

# Textos a traducir
texts_to_translate = {
    "save_button": "Guardar",
    "load_button": "Cargar",
    "achievements_button": "Logros",
    "config_button": "Config",
    "more_improvements_button": "Más mejoras",
    "exit_button": "Salir",
    "big_button": "El Botón",
    "counter_label": "Presionaste el botón {click_count} veces",
    "buddy_label": "Buddy ({required_clicks_buddy} Clicks)",
    "buddies_text": "Tienes {buddy_count} Buddies Actualmente",
    "nudge_label": "Nudge ({required_clicks_nudge} Clicks)",
    "nudges_text": "Tienes {nudge_count} Nudges Actualmente",
    "screen_config_button": "Configuración de Pantalla",
    "audio_config_button": "Configuración de Audio",
    "language_config_button": "Lenguaje",
    "general_config_button": "Configuración General",
    "trophies_config_button": "Configuración de Trofeos",
    "credits_button": "Créditos",
    "theme_config_button": "Tema Visual",
    "aero_effects_button": "Efectos Aero",
    "theme_light_button": "Tema Visual Claro",
    "theme_dark_button": "Tema Visual Oscuro",
    "theme_schedule_button": "Tema Visual Horario",
    "aero_glass_button": "Efecto Aero Glass",
    "aero_basic_button": "Efecto Aero Basic",
    "flat_effect_button": "Efecto Plano",
    "pixel_art_button": "Efecto Pixel Art Glory"
}


# Inicializar el traductor
translator = Translator()

# Lista de lenguajes disponibles y sus códigos
languages = {
    "Español": "es",
    "English": "en",
    "Français": "fr",
    "Deutsch": "de",
    "Italiano": "it",
    "Português": "pt",
    "Русский": "ru",
    "日本語": "ja",
    "简体中文": "zh-CN",
    "한국어": "ko",
    "العربية": "ar",
    "हिन्दी": "hi",
    "বাংলা": "bn",
    "Türkçe": "tr",
    "Polski": "pl",
    "Nederlands": "nl",
    "Ελληνικά": "el",
    "Svenska": "sv",
    "Dansk": "da",
    "Norsk": "no"
}

# Variable para almacenar el idioma actual
current_language = "es"


# Inicializar pygame
pygame.init()

# Intentar inicializar el joystick
joystick_count = pygame.joystick.get_count()
joystick = None  # Inicializar joystick como None
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("Joystick conectado:", joystick.get_name())
else:
    print("No se detectó ningún joystick. Se utilizará mouse y teclado.")

# Clave de encriptación (ahora forma parte del código)
ENCRYPTION_KEY = "ClaveSecreta"

# Variables para el control del mouse con el joystick
mouse_mode = False  # Modo de mouse inactivo al inicio
mouse_sensitivity = 15  # Sensibilidad del mouse
deadzone = 0.1  # Zona muerta del joystick

# Variables para el modo AFK
afk_active = False
last_mouse_position = None
afk_timer = None
afk_overlay = None  # Definir afk_overlay como una variable global
time_label = None  # Variable para el label de la hora

# Variable para el estado de la configuración
config_active = False

# Función para activar la pantalla AFK
def activate_afk_screen():
    global afk_active, afk_overlay, last_mouse_position, time_label
    afk_active = True
    last_mouse_position = pyautogui.position()

    # Crear la capa negra con opacidad
    afk_overlay = tk.Toplevel(root)
    afk_overlay.attributes("-fullscreen", True)
    afk_overlay.attributes("-alpha", 0.9)
    afk_overlay.configure(bg="black")

    # Obtener la hora actual
    now = datetime.now()
    formatted_time = now.strftime("%I:%M %p")  # Formato 12 horas con AM/PM

    # Crear el label para la hora (color blanco)
    time_label = tk.Label(
        afk_overlay, text=formatted_time, font=("Dosis", 48), bg="black", fg="white"
    )
    time_label.place(
        relx=1.0, rely=1.0, anchor="se", padx=20, pady=20
    )  # Colocado abajo a la derecha

    # Actualizar la hora cada segundo
    def update_time():
        if afk_active:
            now = datetime.now()
            formatted_time = now.strftime("%I:%M %p")
            time_label.config(text=formatted_time)
            afk_overlay.after(1000, update_time)

    update_time()

# Función para desactivar la pantalla AFK
def deactivate_afk_screen():
    global afk_active, afk_overlay, afk_timer
    afk_active = False
    if afk_overlay:
        afk_overlay.destroy()
        afk_overlay = None
    if afk_timer:
        root.after_cancel(afk_timer)
        afk_timer = None

# Función para resetear el temporizador AFK
def reset_afk_timer():
    global afk_timer, afk_active
    if afk_timer:
        root.after_cancel(afk_timer)
        afk_timer = None

    if afk_active:
        deactivate_afk_screen()

    afk_timer = root.after(60000, activate_afk_screen)  # 60000 ms = 1 minuto

# Función para comprobar movimiento del mouse
def check_mouse_movement():
    global last_mouse_position
    if not afk_active:
        current_mouse_position = pyautogui.position()
        if current_mouse_position != last_mouse_position:
            reset_afk_timer()
            last_mouse_position = current_mouse_position  # Actualizar posición
    root.after(1000, check_mouse_movement)  # Comprobar cada segundo

# Función para reproducir sonido sin delay (Button sound)
def play_button_sound():
    button_sound = pygame.mixer.Sound("Resources/Button.wav")
    button_sound.play()

# Función para reproducir el sonido del botón grande
def play_big_button_sound():
    big_button_sound = pygame.mixer.Sound("Resources/click.mp3")
    big_button_sound.play()

# Función para reproducir el sonido de Nudge
def play_nudge_sound():
    nudge_sound = pygame.mixer.Sound("Resources/nudge.mp3")
    nudge_sound.play()

# Funciones para reproducir los sonidos de Buddy
def play_buddy_cute_1():
    buddy_cute_1 = pygame.mixer.Sound("Resources/buddycute1.mp3")
    buddy_cute_1.play()

def play_buddy_cute_2():
    buddy_cute_2 = pygame.mixer.Sound("Resources/buddycute2.mp3")
    buddy_cute_2.play()

def play_buddy_cute_3():
    buddy_cute_3 = pygame.mixer.Sound("Resources/buddycute3.mp3")
    buddy_cute_3.play()

def play_buddy_cute_4():
    buddy_cute_4 = pygame.mixer.Sound("Resources/buddycute4.mp3")
    buddy_cute_4.play()

def play_buddy_cute_5():
    buddy_cute_5 = pygame.mixer.Sound("Resources/buddycute5.mp3")
    buddy_cute_5.play()

# Función para reproducir música de fondo en loop continuo (MainMenu sound)
def play_background_music():
    pygame.mixer.music.load("Resources/MainMenu.wav")
    pygame.mixer.music.play(loops=-1, start=0.0)

# Función para encriptar datos
def encrypt_data(data, key):
    encrypted_data = ""
    key_length = len(key)
    for i, char in enumerate(data):
        key_char = key[i % key_length]
        encrypted_data += chr(ord(char) ^ ord(key_char))
    return base64.b64encode(encrypted_data.encode()).decode()

# Función para desencriptar datos
def decrypt_data(data, key):
    decrypted_data = base64.b64decode(data.encode()).decode()
    original_data = ""
    key_length = len(key)
    for i, char in enumerate(decrypted_data):
        key_char = key[i % key_length]
        original_data += chr(ord(char) ^ ord(key_char))
    return original_data

# Función para guardar el progreso (ahora con encriptación)
def save_game():
    global click_count, cps, buddy_count, nudge_count, first_buddy_achievement, ten_buddies_achievement, first_nudge_achievement, master_of_clicks_achievement
    global current_theme, current_effect
    fecha_actual = datetime.now().strftime("%d-%m")
    save_data = {
        "clicks_hechos": click_count,
        "cps": cps,
        "mejoras_compradas": {"buddies": buddy_count, "nudges": nudge_count},
        "fecha_jugada": fecha_actual,
        "horas_jugadas": 0,
        "logros": {
            "primer_buddy": first_buddy_achievement,
            "ten_buddies": ten_buddies_achievement,
            "primer_nudge": first_nudge_achievement,
            "master_of_clicks": master_of_clicks_achievement,
        },
        "tema": current_theme,
        "efecto": current_effect,
    }

    # Generar un hash único para el archivo
    data_string = json.dumps(save_data, sort_keys=True).encode("utf-8")
    hash_object = hashlib.sha256(data_string)
    unique_hash = hash_object.hexdigest()

    # Encriptar el hash
    encrypted_hash = encrypt_data(unique_hash, ENCRYPTION_KEY)

    # Agregar el hash encriptado al JSON
    save_data["hash"] = encrypted_hash

    # Encriptar el JSON completo
    encrypted_save_data = encrypt_data(json.dumps(save_data), ENCRYPTION_KEY)

    # Crear la carpeta "Saves" si no existe
    if not os.path.exists("Saves"):
        os.makedirs("Saves")

    # Guardar el archivo JSON encriptado
    with open(f"Saves/SaveFile{fecha_actual}.json", "w") as f:
        f.write(encrypted_save_data)

    play_button_sound()

def auto_save():
    global click_count, cps, buddy_count, nudge_count, first_buddy_achievement, ten_buddies_achievement, first_nudge_achievement, master_of_clicks_achievement
    global current_theme, current_effect
    while True:
        time.sleep(600)  # Esperar 10 minutos (600 segundos)

        fecha_actual = datetime.now().strftime("%d-%m")
        save_data = {
            "clicks_hechos": click_count,
            "cps": cps,
            "mejoras_compradas": {"buddies": buddy_count, "nudges": nudge_count},
            "fecha_jugada": fecha_actual,
            "horas_jugadas": 0,
            "logros": {
                "primer_buddy": first_buddy_achievement,
                "ten_buddies": ten_buddies_achievement,
                "primer_nudge": first_nudge_achievement,
                "master_of_clicks": master_of_clicks_achievement,
            },
            "tema": current_theme,
            "efecto": current_effect,
        }

        # Generar un hash único para el archivo
        data_string = json.dumps(save_data, sort_keys=True).encode("utf-8")
        hash_object = hashlib.sha256(data_string)
        unique_hash = hash_object.hexdigest()

        # Encriptar el hash
        encrypted_hash = encrypt_data(unique_hash, ENCRYPTION_KEY)

        # Agregar el hash encriptado al JSON
        save_data["hash"] = encrypted_hash

        # Encriptar el JSON completo
        encrypted_save_data = encrypt_data(json.dumps(save_data), ENCRYPTION_KEY)

        # Crear la carpeta "Saves" si no existe
        if not os.path.exists("Saves"):
            os.makedirs("Saves")

        # Guardar el archivo JSON encriptado con "autosave" en el nombre
        with open(f"Saves/Autosave {fecha_actual}.json", "w") as f:
            f.write(encrypted_save_data)

# Iniciar el hilo de auto-guardado
auto_save_thread = threading.Thread(target=auto_save)
auto_save_thread.daemon = True  # Permite que el programa se cierre aunque el hilo esté en ejecución
auto_save_thread.start()

# Función para seleccionar un archivo con el joystick (necesaria para load_game)
def select_file_with_joystick():
    """
    Permite al usuario seleccionar un archivo .json usando el joystick.
    Devuelve la ruta del archivo seleccionado o None si no se selecciona ninguno.
    """

    def get_files(directory):
        """Obtiene la lista de archivos .json en el directorio dado."""
        return [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f.endswith(".json")
        ]

    def draw_file_list(canvas, files, selected_index, scroll_y):
        """Dibuja la lista de archivos en el canvas."""
        canvas.delete("all")
        y = scroll_y
        for i, file in enumerate(files):
            if i == selected_index:
                color = "yellow"  # Resaltar el archivo seleccionado
            else:
                color = "white"
            canvas.create_text(
                10, y, text=file, anchor="nw", fill=color, font=("Dosis", 12)
            )
            y += 20

    # Configuración inicial
    file_select_root = tk.Toplevel(root)
    file_select_root.title("Selecciona un archivo para cargar")
    file_select_root.geometry("400x300")
    file_select_root.configure(bg="black")

    canvas = tk.Canvas(file_select_root, bg="black")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(file_select_root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    saves_dir = "Saves"
    if not os.path.exists(saves_dir):
        os.makedirs(saves_dir)

    files = get_files(saves_dir)
    selected_index = 0
    scroll_y = 0
    max_visible_files = 10  # Número máximo de archivos visibles sin scroll

    draw_file_list(canvas, files, selected_index, scroll_y)

    def update_selection(direction):
        """Actualiza la selección del archivo basado en la entrada del joystick."""
        nonlocal selected_index, scroll_y
        if direction == "up":
            selected_index = max(0, selected_index - 1)
            if selected_index < scroll_y / 20:
                scroll_y = max(0, scroll_y - 20)
        elif direction == "down":
            selected_index = min(len(files) - 1, selected_index + 1)
            if selected_index >= scroll_y / 20 + max_visible_files:
                scroll_y = min((len(files) - max_visible_files) * 20, scroll_y + 20)

        draw_file_list(canvas, files, selected_index, scroll_y)

    def confirm_selection():
        """Confirma la selección del archivo y cierra la ventana."""
        nonlocal selected_index
        if selected_index != -1:
            file_select_root.destroy()
        else:
            selected_index = 0  # Resetear el index

    # Manejo de eventos del joystick
    def joystick_handler():
        nonlocal selected_index

        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 1:  # Eje Y del joystick izquierdo
                    if event.value < -deadzone:
                        update_selection("up")
                    elif event.value > deadzone:
                        update_selection("down")
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1:  # D-pad arriba
                    update_selection("up")
                elif event.value[1] == -1:  # D-pad abajo
                    update_selection("down")
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Botón A
                    confirm_selection()
                elif event.button == 1:  # Botón B
                    selected_index = -1
                    confirm_selection()

        file_select_root.after(100, joystick_handler)

    joystick_handler()
    file_select_root.wait_window()

    if selected_index != -1 and files:
        return os.path.join(saves_dir, files[selected_index])
    else:
        return None

# Función para cargar el progreso (ahora con desencriptación y validaciones)
def load_game():
    global joystick, current_theme, current_effect

    if joystick:
        file_path = select_file_with_joystick()
    else:
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json")]
        )

    if file_path:

        def anti_piracy_screen(color):
            global anti_piracy_active
            # Eliminar widgets
            for widget in root.winfo_children():
                widget.destroy()

            # Desactivar sonidos
            pygame.mixer.music.stop()

            # Pantalla completa de color
            root.configure(bg=color)

            # Reproducir sonido de error
            error_sound = pygame.mixer.Sound("Resources/Beep.mp3")
            error_sound.play()

            # Mensaje en pantalla
            error_message = (
                "El programa ha detectado un archivo .JSON Defectuoso o con clave de encriptación incorrecta.\n"
                "Pibe Emoji Studios no tolera actos como Trampas en los juegos.\n"
                "Para un mejor juego sano, no cargue archivos .JSON de terceros, use los oficiales del programa al guardar progreso,\n"
                "ubicados en la carpeta Saves.\n"
                "Use ALT + F4 Para cerrar el programa y procure no volver a usar ese archivo .JSON.\n"
                "Hasta que decida que hacer, la pantalla seguirá así."
            )

            error_label = tk.Label(
                root,
                text=error_message,
                font=("Dosis", 20),
                bg=color,
                fg="white",
                justify="center",
            )
            error_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

            # Copyright
            copyright_label = tk.Label(
                root,
                text="Pibe Emoji Studios (C) 2021 - 2025",
                font=("Dosis", 32),
                bg=color,
                fg="white",
            )
            copyright_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

            anti_piracy_active = True

        try:
            with open(file_path, "r") as f:
                encrypted_content = f.read()

            # Intentar desencriptar el contenido
            try:
                decrypted_content = decrypt_data(encrypted_content, ENCRYPTION_KEY)
                loaded_data = json.loads(decrypted_content)
                is_encrypted = True
            except:
                # Si falla la desencriptación, asumir que no está encriptado
                with open(file_path, "r") as f:
                    loaded_data = json.load(f)
                is_encrypted = False

            # Verificar si el archivo tiene un hash (si está encriptado)
            if is_encrypted and "hash" in loaded_data:
                # Obtener el hash encriptado y desencriptarlo
                encrypted_hash = loaded_data["hash"]
                decrypted_hash = decrypt_data(encrypted_hash, ENCRYPTION_KEY)

                # Crear una copia de los datos cargados sin el hash para la verificación
                temp_data = loaded_data.copy()
                temp_data.pop("hash")

                # Generar un nuevo hash a partir de los datos cargados
                data_string = json.dumps(temp_data, sort_keys=True).encode("utf-8")
                hash_object = hashlib.sha256(data_string)
                new_hash = hash_object.hexdigest()

                # Verificar si el hash coincide
                if new_hash != decrypted_hash:
                    print(
                        "Error: El archivo ha sido modificado o está corrupto (hash incorrecto)."
                    )
                    # Activar pantalla antipiratería en azul si el hash es incorrecto
                    root.after(10000, lambda: anti_piracy_screen("blue"))
                    return

            # Si no está encriptado, también verificar el hash (si existe)
            elif not is_encrypted and "hash" in loaded_data:
                # Obtener el hash (no está encriptado)
                existing_hash = loaded_data["hash"]

                # Crear una copia de los datos cargados sin el hash para la verificación
                temp_data = loaded_data.copy()
                temp_data.pop("hash")

                # Generar un nuevo hash a partir de los datos cargados
                data_string = json.dumps(temp_data, sort_keys=True).encode("utf-8")
                hash_object = hashlib.sha256(data_string)
                new_hash = hash_object.hexdigest()

                if new_hash != existing_hash:
                    print(
                        "Error: El archivo no está encriptado pero el hash es incorrecto."
                    )
                    # Activar pantalla antipiratería en azul
                    root.after(10000, lambda: anti_piracy_screen("blue"))
                    return

            # Si falta una clave en el JSON, activar pantalla antipiratería en rojo
            if not all(
                key in loaded_data
                for key in [
                    "clicks_hechos",
                    "cps",
                    "mejoras_compradas",
                    "fecha_jugada",
                    "horas_jugadas",
                    "logros",
                    "tema",
                    "efecto",
                ]
            ):
                print("Error: Estructura del archivo JSON incorrecta.")
                # Activar pantalla antipiratería en rojo si la estructura es incorrecta
                root.after(10000, lambda: anti_piracy_screen("red"))
                return

            # Si todo está bien, cargar los datos
            global click_count, cps, buddy_count, nudge_count, counter_label, buddies_text, nudges_text, cps_label, first_buddy_achievement, ten_buddies_achievement, first_nudge_achievement, master_of_clicks_achievement
            click_count = loaded_data["clicks_hechos"]
            cps = loaded_data["cps"]
            buddy_count = loaded_data["mejoras_compradas"]["buddies"]
            nudge_count = loaded_data["mejoras_compradas"]["nudges"]

            # Cargar tema y efecto
            current_theme = loaded_data.get("tema", "light")
            current_effect = loaded_data.get("efecto", "glass")

            # Cargar logros, si no existen poner a False para que no de errores
            first_buddy_achievement = loaded_data.get("logros", {}).get(
                "primer_buddy", False
            )
            ten_buddies_achievement = loaded_data.get("logros", {}).get(
                "ten_buddies", False
            )
            first_nudge_achievement = loaded_data.get("logros", {}).get(
                "primer_nudge", False
            )
            master_of_clicks_achievement = loaded_data.get("logros", {}).get(
                "master_of_clicks", False
            )

            # Actualizar los widgets con los datos cargados
            counter_label.config(text=f"Presionaste el botón {click_count} veces")
            buddies_text.config(text=f"Tienes {buddy_count} Buddies Actualmente")
            nudges_text.config(text=f"Tienes {nudge_count} Nudges Actualmente")
            cps_label.config(text=f"{cps} CPS")

            # Actualizar la interfaz con el tema cargado
            show_main_menu()

            play_button_sound()

        except json.JSONDecodeError:
            print("Error: Archivo JSON inválido o no se pudo desencriptar.")
            # Activar pantalla antipiratería en rojo si hay un error de decodificación JSON
            root.after(10000, lambda: anti_piracy_screen("red"))
        except Exception as e:
            print(f"Error inesperado: {e}")
            root.after(10000, lambda: anti_piracy_screen("red"))

# Crear ventana principal
root = tk.Tk()
root.title("Nudger")
root.attributes("-fullscreen", True)

# Variables para controlar el modo de ventana
fullscreen = True

# Variable para estado de la pantalla anti piratería
anti_piracy_active = False

# Función para alternar entre modo de ventana y pantalla completa
def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        root.attributes("-fullscreen", True)
        root.geometry("")  # Restablecer tamaño para pantalla completa
    else:
        root.attributes("-fullscreen", False)
        root.geometry("1200x800")  # Establecer tamaño para modo ventana

# Configurar el atajo de teclado para alternar el modo de ventana
root.bind("<Alt-Return>", toggle_fullscreen)  # Alt + Enter

# Colores
WHITE = "#FFFFFF"
BLACK = "#000000"
LIGHT_GREEN = "#90EE90"
YELLOW = "#FFFF00"
DARK_BLUE = "#00008B"
RED = "#FF0000"
CYAN = "#00FFFF"
LIGHT_CYAN = "#E0FFFF"
LIGHT_BLUE = "#ADD8E6"

# Configuración de la pantalla
root.configure(bg=WHITE)

# Cargar imagen del logo
logo_image = tk.PhotoImage(file="Resources/NudgerLogo.png")
menu_logo_image = tk.PhotoImage(file="Resources/NudgerLogoMini.png")
buddy_image = tk.PhotoImage(file="Resources/Buddy.png")  # Cargar imagen de Buddy
nudge_image = tk.PhotoImage(file="Resources/Nudge.png")  # Cargar imagen de Nudge

# Cargar la fuente Dosis
dosis_font = ImageFont.truetype("Resources/Dosis-Regular.ttf", 16)
dosis_font_tk = ("Dosis", 16)  # Fuente para tkinter

# Crear widgets de pantalla de carga
logo_label = tk.Label(root, image=logo_image, bg=WHITE)
logo_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

loading_bar = ttk.Progressbar(
    root, orient="horizontal", length=400, mode="determinate"
)
loading_bar.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

studio_label = tk.Label(
    root, text="Pibe Emoji Studios", font=dosis_font_tk, bg=WHITE, fg=BLACK
)
studio_label.place(relx=0.95, rely=0.95, anchor=tk.SE)

copyright_label = tk.Label(
    root, text="Copyright (C) 2025 Guille's Stuff", font=dosis_font_tk, bg=WHITE, fg=BLACK
)
copyright_label.place(relx=0.05, rely=0.95, anchor=tk.SW)

# Función para simular carga
def update_loading():
    for i in range(101):
        loading_bar["value"] = i
        root.update_idletasks()
        root.after(50)

# Función para crear botones como imágenes
def create_image_button(text, x, y, command, normal_image_path, pressed_image_path, parent=None):
    # Usar root como padre por defecto si no se especifica
    if parent is None:
        parent = root
    
    # Cargar las imágenes
    button_image_normal = Image.open(normal_image_path)
    button_image_pressed = Image.open(pressed_image_path)

    # Agregar texto al centro de la imagen
    font_size = 30 if parent != root else 16  # Fuente más grande para Config
    font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcula las dimensiones de la imagen
    width, height = button_image_normal.size

    # Crea un objeto draw para la primera imagen
    draw_normal = ImageDraw.Draw(button_image_normal)

    # Ajusta el tamaño de la fuente para que encaje en la imagen
    while (
        draw_normal.textbbox((0, 0), text, font=font)[2] > width - (60 if parent != root else 10)
        or draw_normal.textbbox((0, 0), text, font=font)[3] > height - (20 if parent != root else 10)
    ):
        font_size -= 1
        font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcular el tamaño de la caja del texto
    text_bbox_normal = draw_normal.textbbox((0, 0), text, font=font)
    text_width_normal = text_bbox_normal[2] - text_bbox_normal[0]
    text_height_normal = text_bbox_normal[3] - text_bbox_normal[1]
    # Calcular la posición central
    text_x_normal = (width - text_width_normal) / 2
    text_y_normal = (height - text_height_normal) / 2

    # Dibujar el texto en la primera imagen
    draw_normal.text(
        (text_x_normal, text_y_normal), text, font=font, fill=WHITE
    )

    # Guarda la imagen modificada para la primera imagen
    button_image_normal_tk = ImageTk.PhotoImage(button_image_normal)

    # Crea un objeto draw para la segunda imagen
    draw_pressed = ImageDraw.Draw(button_image_pressed)

    # Ajusta el tamaño de la fuente para que encaje en la imagen (usar el mismo tamaño calculado para la primera)
    font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcular el tamaño de la caja del texto
    text_bbox_pressed = draw_pressed.textbbox((0, 0), text, font=font)
    text_width_pressed = text_bbox_pressed[2] - text_bbox_pressed[0]
    text_height_pressed = text_bbox_pressed[3] - text_bbox_pressed[1]
    # Calcular la posición central
    text_x_pressed = (width - text_width_pressed) / 2
    text_y_pressed = (height - text_height_pressed) / 2

    # Dibujar el texto en la segunda imagen
    draw_pressed.text(
        (text_x_pressed, text_y_pressed), text, font=font, fill=WHITE
    )

    # Guarda la imagen modificada para la segunda imagen
    button_image_pressed_tk = ImageTk.PhotoImage(button_image_pressed)

    # Crear el botón como una etiqueta con imagen
    button_label = tk.Label(parent, image=button_image_normal_tk, bg="black" if parent != root else "white", borderwidth=0, highlightthickness=0)
    button_label.place(x=x, y=y, anchor="ne")
    button_label.image_normal = button_image_normal_tk
    button_label.image_pressed = button_image_pressed_tk

    # Función para cambiar entre imágenes al clickear
    def button_click(event):
        button_label.config(image=button_label.image_pressed)
        parent.after(
            100, lambda: button_label.config(image=button_label.image_normal)
        )
        command()

    # Funciones para animar al pasar el ratón
    def on_enter(event):
        button_label.config(image=button_label.image_pressed)

    def on_leave(event):
        button_label.config(image=button_label.image_normal)

    button_label.bind("<Button-1>", button_click)
    button_label.bind("<Enter>", on_enter)
    button_label.bind("<Leave>", on_leave)

    return button_label

# Función para mostrar el menú principal y el botón animado
def show_main_menu():
    global current_theme, current_effect

    # Configurar ventana del menú principal
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="black" if current_theme == "dark" else "white")

    # Mostrar logo en la esquina superior izquierda
    logo_label = tk.Label(
        root, image=menu_logo_image, bg="black" if current_theme == "dark" else "white"
    )
    logo_label.place(x=10, y=10, anchor=tk.NW)

    # Funciones para crear botones como imagenes
    def create_image_button(
        text, x, y, command, normal_image_path, pressed_image_path
    ):
        # Cargar las imagenes
        if current_effect == "glass":
            button_image_normal = Image.open(normal_image_path)
            button_image_pressed = Image.open(pressed_image_path)
        elif current_effect == "basic":
            normal_image_path = normal_image_path.replace("MiniButtonTexture", "MiniButtonBasicTexture")
            normal_image_path = normal_image_path.replace("MiniButtonYellow", "MiniButtonYellowBasic")
            normal_image_path = normal_image_path.replace("MiniButtonRed", "MiniButtonRedBasic")
            pressed_image_path = pressed_image_path.replace("MiniButtonTexture", "MiniButtonBasicTexture")
            pressed_image_path = pressed_image_path.replace("MiniButtonYellow", "MiniButtonYellowBasic")
            pressed_image_path = pressed_image_path.replace("MiniButtonRed", "MiniButtonRedBasic")
            button_image_normal = Image.open(normal_image_path)
            button_image_pressed = Image.open(pressed_image_path)
        
        else: #flat
          
            normal_image_path = normal_image_path.replace("MiniButtonTexture", "MiniButtonFlatTexture")
            normal_image_path = normal_image_path.replace("MiniButtonYellow", "MiniButtonYellowFlat")
            normal_image_path = normal_image_path.replace("MiniButtonRed", "MiniButtonRedFlat")
            pressed_image_path = pressed_image_path.replace("MiniButtonTexture", "MiniButtonFlatTexture")
            pressed_image_path = pressed_image_path.replace("MiniButtonYellow", "MiniButtonYellowFlat")
            pressed_image_path = pressed_image_path.replace("MiniButtonRed", "MiniButtonRedFlat")
            button_image_normal = Image.open(normal_image_path)
            button_image_pressed = Image.open(pressed_image_path)
            

        # Agregar texto al centro de la imagen
        font_size = 16  # Tamaño de fuente inicial
        font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

        # Calcula las dimensiones de la imagen
        width, height = button_image_normal.size

        # Crea un objeto draw para la primera imagen
        draw_normal = ImageDraw.Draw(button_image_normal)

        # Ajusta el tamaño de la fuente para que encaje en la imagen
        while (
            draw_normal.textbbox((0, 0), text, font=font)[2] > width - 10
            or draw_normal.textbbox((0, 0), text, font=font)[3] > height - 10
        ):
            font_size -= 1
            font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

        # Calcular el tamaño de la caja del texto
        text_bbox_normal = draw_normal.textbbox((0, 0), text, font=font)
        text_width_normal = text_bbox_normal[2] - text_bbox_normal[0]
        text_height_normal = text_bbox_normal[3] - text_bbox_normal[1]
        # Calcular la posicion central
        text_x_normal = (width - text_width_normal) / 2
        text_y_normal = (height - text_height_normal) / 2

        # Definir el color del texto basado en el tema actual
        text_color = WHITE if current_theme == "dark" else BLACK

        # Dibujar el texto en la primera imagen
        draw_normal.text(
            (text_x_normal, text_y_normal), text, font=font, fill=text_color
        )

        # Guarda la imagen modificada para la primera imagen
        button_image_normal_tk = ImageTk.PhotoImage(button_image_normal)

        # Crea un objeto draw para la segunda imagen
        draw_pressed = ImageDraw.Draw(button_image_pressed)

        # Ajusta el tamaño de la fuente para que encaje en la imagen (usar el mismo tamaño calculado para la primera)
        font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

        # Calcular el tamaño de la caja del texto
        text_bbox_pressed = draw_pressed.textbbox((0, 0), text, font=font)
        text_width_pressed = text_bbox_pressed[2] - text_bbox_pressed[0]
        text_height_pressed = text_bbox_pressed[3] - text_bbox_pressed[1]
        # Calcular la posicion central
        text_x_pressed = (width - text_width_pressed) / 2
        text_y_pressed = (height - text_height_pressed) / 2

        # Definir el color del texto basado en el tema actual
        text_color = WHITE if current_theme == "dark" else BLACK

        # Dibujar el texto en la segunda imagen
        draw_pressed.text(
            (text_x_pressed, text_y_pressed), text, font=font, fill=text_color
        )

        # Guarda la imagen modificada para la segunda imagen
        button_image_pressed_tk = ImageTk.PhotoImage(button_image_pressed)

        # Crear el botón como una etiqueta con imagen
        button_label = tk.Label(
            root,
            image=button_image_normal_tk,
            bg="black" if current_theme == "dark" else "white",
        )
        button_label.place(x=x, y=y)
        button_label.image_normal = button_image_normal_tk
        button_label.image_pressed = button_image_pressed_tk

        # Funcion para cambiar entre imagenes al clickear
        def button_click(event):
            button_label.config(image=button_label.image_pressed)
            root.after(
                100, lambda: button_label.config(image=button_label.image_normal)
            )
            command()

        # Funciones para animar al pasar el ratón
        def on_enter(event):
            button_label.config(image=button_label.image_pressed)

        def on_leave(event):
            button_label.config(image=button_label.image_normal)

        button_label.bind("<Button-1>", button_click)
        button_label.bind("<Enter>", on_enter)
        button_label.bind("<Leave>", on_leave)

        return button_label

    def play_button_sound():
        play_sound("Resources/Button.wav")
    
    #Aqui se crean los botones del menu principal
    create_image_button(
        "Guardar",
        50,
        250,
        save_game,
        "Resources/MiniButtonTexture01.png",
        "Resources/MiniButtonTexture02.png",
    )
    create_image_button(
        "Cargar",
        50,
        370,
        load_game,
        "Resources/MiniButtonTexture01.png",
        "Resources/MiniButtonTexture02.png",
    )
    create_image_button(
        "Logros",
        50,
        490,
        lambda: play_button_sound(),
        "Resources/MiniButtonYellow01.png",
        "Resources/MiniButtonYellow02.png",
    )
    create_image_button(
        "Config",
        50,
        610,
        lambda: [play_button_sound(), show_config_menu()],  # Llama a la función show_config_menu()
        "Resources/MiniButtonTexture01.png",
        "Resources/MiniButtonTexture02.png",
    )
    create_image_button(
        "Más mejoras",
        50,
        730,
        lambda: play_button_sound(),
        "Resources/MiniButtonYellow01.png",
        "Resources/MiniButtonYellow02.png",
    )
    create_image_button(
        "Salir",
        50,
        850,
        root.quit,
        "Resources/MiniButtonRed01.png",
        "Resources/MiniButtonRed02.png",
    )

    # Cargar las imágenes para el botón grande
    if current_effect == "glass":
        button_image_normal = Image.open("Resources/BigButtonTexture01.png")
        button_image_pressed = Image.open("Resources/BigButtonTexture02.png")
    elif current_effect == "basic":
        button_image_normal = Image.open("Resources/BigButtonBasicTexture01.png")
        button_image_pressed = Image.open("Resources/BigButtonBasicTexture02.png")
    else: #flat
        button_image_normal = Image.open("Resources/BigButtonFlatTexture01.png")
        button_image_pressed = Image.open("Resources/BigButtonFlatTexture02.png")
        

    # Agregar texto "El Botón" al centro de la imagen
    font_size = 70  # Tamaño de fuente inicial
    font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcula las dimensiones de la imagen
    width, height = button_image_normal.size

    # Crea un objeto draw para la primera imagen
    draw_normal = ImageDraw.Draw(button_image_normal)

    # Ajusta el tamaño de la fuente para que encaje en la imagen
    while (
        draw_normal.textbbox((0, 0), "El Botón", font=font)[2] > width - 30
        or draw_normal.textbbox((0, 0), "El Botón", font=font)[3] > height - 40
    ):
        font_size -= 2
        font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcular el tamaño de la caja del texto
    text_bbox_normal = draw_normal.textbbox((0, 0), "El Botón", font=font)
    text_width_normal = text_bbox_normal[2] - text_bbox_normal[0]
    text_height_normal = text_bbox_normal[3] - text_bbox_normal[1]
    # Calcular la posicion central
    text_x_normal = (width - text_width_normal) / 2
    text_y_normal = (height - text_height_normal) / 2

    # Dibujar el texto en la primera imagen
    draw_normal.text(
        (text_x_normal, text_y_normal), "El Botón", font=font, fill=WHITE
    )

    # Guarda la imagen modificada para la primera imagen
    button_image_normal_tk = ImageTk.PhotoImage(button_image_normal)

    # Crea un objeto draw para la segunda imagen
    draw_pressed = ImageDraw.Draw(button_image_pressed)

    # Ajusta el tamaño de la fuente para que encaje en la imagen (usar el mismo tamaño calculado para la primera)
    font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcular el tamaño de la caja del texto
    text_bbox_pressed = draw_pressed.textbbox((0, 0), "El Botón", font=font)
    text_width_pressed = text_bbox_pressed[2] - text_bbox_pressed[0]
    text_height_pressed = text_bbox_pressed[3] - text_bbox_pressed[1]
    # Calcular la posicion central
    text_x_normal = (width - text_width_normal) / 2
    text_y_normal = (height - text_height_normal) / 2

    # Dibujar el texto en la primera imagen
    draw_normal.text(
        (text_x_normal, text_y_normal), "El Botón", font=font, fill=WHITE
    )

    # Guarda la imagen modificada para la primera imagen
    button_image_normal_tk = ImageTk.PhotoImage(button_image_normal)

    # Crea un objeto draw para la segunda imagen
    draw_pressed = ImageDraw.Draw(button_image_pressed)

    # Ajusta el tamaño de la fuente para que encaje en la imagen (usar el mismo tamaño calculado para la primera)
    font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcular el tamaño de la caja del texto
    text_bbox_pressed = draw_pressed.textbbox((0, 0), "El Botón", font=font)
    text_width_pressed = text_bbox_pressed[2] - text_bbox_pressed[0]
    text_height_pressed = text_bbox_pressed[3] - text_bbox_pressed[1]
    # Calcular la posicion central
    text_x_pressed = (width - text_width_pressed) / 2
    text_y_pressed = (height - text_height_pressed) / 2

    # Dibujar el texto en la segunda imagen
    draw_pressed.text(
        (text_x_pressed, text_y_pressed), "El Botón", font=font, fill=WHITE
    )

    # Guarda la imagen modificada para la segunda imagen
    button_image_pressed_tk = ImageTk.PhotoImage(button_image_pressed)

    # Crear el botón grande como una etiqueta con imagen
    global button_label
    button_label = tk.Label(root, image=button_image_normal_tk, bg=WHITE)
    # Centrar el botón
    button_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    button_label.image_normal = button_image_normal_tk
    button_label.image_pressed = button_image_pressed_tk


    # Funcion para cambiar entre imagenes al clickear, ahora está definida dentro de show_main_menu
    def animate_button(event=None):
        global click_count
        click_count += 1
        counter_label.config(
            text=f"Presionaste el botón {click_count} veces", font=dosis_font_tk
               )
        button_label.config(image=button_label.image_pressed)
        root.after(
            100, lambda: button_label.config(image=button_label.image_normal)
        )
        play_big_button_sound()  # Usar la función específica para el botón grande

    # Funciones para animar al pasar el ratón
    def on_enter(event):
        button_label.config(image=button_label.image_pressed)

    def on_leave(event):
        button_label.config(image=button_label.image_normal)

    button_label.bind("<Button-1>", animate_button)
    button_label.bind("<Enter>", on_enter)
    button_label.bind("<Leave>", on_leave)

    # Crear contador de clics
    global click_count, counter_label, master_of_clicks_achievement
    click_count = 0
    counter_label = tk.Label(
        root,
        text=f"Presionaste el botón {click_count} veces",
        font=dosis_font_tk,
        bg=WHITE,
        fg=BLACK,
        highlightthickness=2,
        highlightbackground=CYAN,
    )
    counter_label.place(relx=0.5, rely=0.65, anchor=tk.CENTER)
    master_of_clicks_achievement = False  # Inicializar logro Maestro de los Clicks a False

    # Sección de mejoras a la derecha
    improvements_label = tk.Label(
        root, text="Mejoras", font=dosis_font_tk, bg=WHITE, fg=BLACK
    )
    improvements_label.place(relx=0.95, rely=0.05, anchor=tk.NE)

    # Buddies
    buddy_label = tk.Label(
        root, text="Buddy (20 Clicks)", font=dosis_font_tk, bg=WHITE, fg=BLACK
    )
    buddy_label.place(relx=0.95, rely=0.1, anchor=tk.NE)

    buddy_image_label = tk.Label(root, image=buddy_image, bg=WHITE)
    buddy_image_label.place(relx=0.95, rely=0.2, anchor=tk.NE)

    global buddy_count, cps, required_clicks_buddy, cps_label, buddies_text, first_buddy_achievement, ten_buddies_achievement, first_nudge_achievement
    buddy_count = 0

    
    cps = 0  # Inicializa CPS a 0, porque los clicks automaticos los da el buddy
    required_clicks_buddy = 20
    first_buddy_achievement = False  # Inicializar el logro del primer buddy a False
    ten_buddies_achievement = False  # Inicializar el logro de 10 buddies a False
    first_nudge_achievement = False  # Inicializar logro del primer nudge a False

    # Mostrar siempre "1 CPS" de forma estática (sin cambiar este texto)
    cps_label = tk.Label(root, text="1 CPS", font=dosis_font_tk, bg=WHITE, fg=BLACK)
    cps_label.place(relx=0.95, rely=0.3, anchor=tk.NE)

        # Ahora buy_buddy está definida dentro de show_main_menu
    def buy_buddy():
        global buddy_count, click_count, cps, required_clicks_buddy, first_buddy_achievement, ten_buddies_achievement
        if click_count >= required_clicks_buddy:
            click_count -= required_clicks_buddy
            
            # Check if it's the first buddy
            if buddy_count == 0:
               show_achievement_popup("👤Primer Buddy 👤", "Resources/BuddyTrophy.png") # Mostrar logro del primer buddy
               first_buddy_achievement = True
            
            elif buddy_count == 9 and not ten_buddies_achievement:
               show_achievement_popup("👤10 Buddies 👤", "Resources/10BuddiesTrophy.png")  # Mostrar logro de 10 buddies
               ten_buddies_achievement = True
            
            buddy_count += 1
            required_clicks_buddy += 20
            cps += 1 # Incrementa 1 CPS (click automatico)
            counter_label.config(text=f"Presionaste el botón {click_count} veces", font=dosis_font_tk)
            buddy_label.config(text=f"Buddy ({required_clicks_buddy} Clicks)", font=dosis_font_tk)
            buddies_text.config(text=f"Tienes {buddy_count} Buddies Actualmente", font=dosis_font_tk)
            # cps_label.config(text=f"{cps} CPS")  # Actualizar CPS en la etiqueta
            
            # Reproducir un sonido aleatorio de Buddy
            buddy_sounds = [play_buddy_cute_1, play_buddy_cute_2, play_buddy_cute_3, play_buddy_cute_4, play_buddy_cute_5]
            random.choice(buddy_sounds)()

    create_image_button("Comprar Buddy", 0.95, 0.4, buy_buddy, "Resources/MiniButtonTexture01.png", "Resources/MiniButtonTexture02.png").place(relx=0.95, rely=0.4, anchor=tk.NE)

    buddies_text = tk.Label(
        root,
        text=f"Tienes {buddy_count} Buddies Actualmente",
        font=dosis_font_tk,
        bg=WHITE,
        fg=BLACK
    )
    buddies_text.place(relx=0.95, rely=0.5, anchor=tk.NE)

    # Nudges
    nudge_label = tk.Label(root, text="Nudge (200 Clicks)", font=dosis_font_tk, bg=WHITE, fg=BLACK)
    nudge_label.place(relx=0.95, rely=0.55, anchor=tk.NE)

    nudge_image_label = tk.Label(root, image=nudge_image, bg=WHITE)
    nudge_image_label.place(relx=0.95, rely=0.6, anchor=tk.NE)  # Ajuste aquí

    global nudge_count, required_clicks_nudge, nudge_cps, nudges_text
    nudge_count = 0
    required_clicks_nudge = 200
    nudge_cps = 5

    # Mostrar siempre "5 CPS" de forma estática al lado del logo de Nudge
    nudge_cps_label = tk.Label(root, text="5 CPS", font=dosis_font_tk, bg=WHITE, fg=BLACK)
    nudge_cps_label.place(relx=0.95, rely=0.7, anchor=tk.NE)

    # buy_nudge ahora está definida dentro de show_main_menu
    def buy_nudge():
        global nudge_count, click_count, cps, required_clicks_nudge, first_nudge_achievement
        if click_count >= required_clicks_nudge:
            click_count -= required_clicks_nudge

            if nudge_count == 0:
                 show_achievement_popup("👤Primer Nudge 👤", "Resources/NudgeTrophy.png")
                 first_nudge_achievement = True

            nudge_count += 1
            required_clicks_nudge += 100
            cps += nudge_cps # Incrementa 5 CPS (clicks automaticos)
            counter_label.config(text=f"Presionaste el botón {click_count} veces", font=dosis_font_tk)
            nudge_label.config(text=f"Nudge ({required_clicks_nudge} Clicks)", font=dosis_font_tk)
            nudges_text.config(text=f"Tienes {nudge_count} Nudges Actualmente", font=dosis_font_tk)
           # cps_label.config(text=f"{cps} CPS") # Actualizar CPS en la etiqueta (QUITADO)
            play_nudge_sound() # Reproducir el sonido de Nudge

    create_image_button("Comprar Nudge", 0.95, 0.75, buy_nudge, "Resources/MiniButtonYellow01.png", "Resources/MiniButtonYellow02.png").place(relx=0.95, rely=0.75, anchor=tk.NE)

    nudges_text = tk.Label(
        root,
        text=f"Tienes {nudge_count} Nudges Actualmente",
        font=dosis_font_tk,
        bg=WHITE,
        fg=BLACK
    )
    nudges_text.place(relx=0.95, rely=0.85, anchor=tk.NE)

    # Hilo para CPS en segundo plano
    def cps_thread():
        global click_count, cps, master_of_clicks_achievement
        while True:
            time.sleep(1)  # Esperar 1 segundo
            click_count += cps  # Aumentar el contador según los CPS
            counter_label.config(text=f"Presionaste el botón {click_count} veces", font=dosis_font_tk)
            if click_count >= 1000 and not master_of_clicks_achievement:
                master_of_clicks_achievement = True
                show_achievement_popup("🖱️Maestro de los Clicks 🖱️", "Resources/MocTrophy.png")
    threading.Thread(target=cps_thread, daemon=True).start()

# Función para reproducir un sonido
def play_sound(sound_path):
    try:
        sound = pygame.mixer.Sound(sound_path)
        sound.play()
    except pygame.error as e:
        print(f"Error al reproducir sonido: {e}")


    # Función para actualizar el tema según la hora
def update_theme_by_time():
    global current_theme, config_overlay
    now = datetime.now()
    current_hour = now.hour

    if 7 <= current_hour < 18:
        current_theme = "light"
    else:
        current_theme = "dark"

    if config_overlay:
        config_overlay.configure(bg="black" if current_theme == "dark" else "white")
        background_label = config_overlay.winfo_children()[0]  # Asumiendo que el primer hijo es el label del fondo
        background_label.config(bg="black" if current_theme == "dark" else "white")

        for child in config_overlay.winfo_children():
            if isinstance(child, tk.Label) and hasattr(child, 'image'):
                child.config(bg="black" if current_theme == "dark" else "white")

    # Programar la próxima actualización en 1 minuto
    root.after(60000, update_theme_by_time)

    
def translate_texts(target_language):
    global texts_to_translate
    for key, text in texts_to_translate.items():
        texts_to_translate[key] = translate_text(text, target_language)

    # Actualizar la interfaz según el estado actual
    update_ui()

def translate_text(text, target_language):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        print(f"Error al traducir el texto: {e}")
        return text

def change_language(language_code):
    global current_language
    current_language = language_code
    translate_texts(current_language)
    update_ui()  # Llama a la función para actualizar la interfaz

def update_ui():
    """Actualiza la interfaz de usuario según el estado actual."""
    if config_active:
        # Si un menú de configuración está activo, redibujarlo
        config_overlay.destroy()  # Destruye el menú de configuración actual
        show_config_menu()       # Vuelve a crear el menú de configuración
    else:
        # Si no hay menú de configuración, redibuja el menú principal
        show_main_menu()        
        
# Función para mostrar el menú de configuración
def show_config_menu():
    """
    Muestra el menú de configuración principal como una capa semitransparente
    sobre la ventana principal. Permite acceder a diferentes submenús de configuración.
    """
    global config_active, config_overlay, close_button_image_normal, close_button_image_pressed
    global current_theme, current_effect

    if not config_active:
        config_active = True

        # Crear una capa semitransparente
        config_overlay = tk.Toplevel(root)
        config_overlay.attributes("-fullscreen", True)
        config_overlay.attributes("-alpha", 0.7)
        config_overlay.configure(
            bg="black" if current_theme == "dark" else "white"
        )

        # Colocar la textura de fondo
        background_texture = Image.open("Resources/MenuTexture.png")
        background_texture_tk = ImageTk.PhotoImage(background_texture)
        background_label = tk.Label(
            config_overlay,
            image=background_texture_tk,
            bg="black" if current_theme == "dark" else "white",
        )
        background_label.image = background_texture_tk
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Cargar las imagenes del boton de cerrar
        if current_effect == "glass":
           close_button_image_normal = Image.open("Resources/CloseTexture01.png")
           close_button_image_pressed = Image.open("Resources/CloseTexture02.png")
        elif current_effect == "basic":
            close_button_image_normal = Image.open("Resources/CloseTextureBasic01.png")
            close_button_image_pressed = Image.open("Resources/CloseTextureBasic02.png")
        else:  # flat
            close_button_image_normal = Image.open("Resources/CloseTextureFlat01.png")
            close_button_image_pressed = Image.open("Resources/CloseTextureFlat02.png")

        close_button_image_normal_tk = ImageTk.PhotoImage(
            close_button_image_normal
        )
        close_button_image_pressed_tk = ImageTk.PhotoImage(
            close_button_image_pressed
        )

        def on_close_enter(event):
            close_button_label.config(image=close_button_image_pressed_tk)

        def on_close_leave(event):
            close_button_label.config(image=close_button_image_normal_tk)

        def close_config_menu():
            """Cierra el menú de configuración actual."""
            global config_active
            config_active = False
            play_sound("Resources/Close.mp3")
            config_overlay.destroy()

        def open_main_config_menu():
            """Vuelve a abrir el menú principal (actualmente redundante)."""
            close_config_menu()
            show_config_menu()

        # Crear el botón de cerrar como una etiqueta con imagen
        close_button_label = tk.Label(
            config_overlay,
            image=close_button_image_normal_tk,
            bg="black" if current_theme == "dark" else "white",
            borderwidth=0,
            highlightthickness=0,
        )
        close_button_label.image = close_button_image_normal_tk  # mantén la referencia
        close_button_label.place(relx=0.95, rely=0.05, anchor="ne")

        # Asociar los eventos para la animación del botón
        close_button_label.bind("<Enter>", on_close_enter)
        close_button_label.bind("<Leave>", on_close_leave)
        close_button_label.bind("<Button-1>", lambda event: close_config_menu())

        # --- Función para crear botones de configuración ---
        def create_config_button(
            text,
            x,
            y,
            command,
            normal_image_path,
            pressed_image_path,
            icon_image_path=None,
            icon_default=False,
            aero_menu = False
        ):
            # Cargar las imagenes
            if current_effect == "glass":
               button_image_normal = Image.open(normal_image_path)
               button_image_pressed = Image.open(pressed_image_path)
            elif current_effect == "basic":
                button_image_normal = Image.open("Resources/MenuButtonTextureBasic01.png")
                button_image_pressed = Image.open("Resources/MenuButtonTextureBasic02.png")
            else:  # flat
                button_image_normal = Image.open("Resources/MenuButtonTextureFlat01.png")
                button_image_pressed = Image.open("Resources/MenuButtonTextureFlat02.png")

            # Agregar texto al centro de la imagen
            font_size = 24  # Tamaño de fuente inicial
            font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

            # Calcula las dimensiones de la imagen
            width, height = button_image_normal.size

            # Crea un objeto draw para la primera imagen
            draw_normal = ImageDraw.Draw(button_image_normal)

            # Ajusta el tamaño de la fuente para que encaje en la imagen
            while (
                draw_normal.textbbox((0, 0), text, font=font)[2] > width - 10
                or draw_normal.textbbox((0, 0), text, font=font)[3] > height - 10
            ):
                font_size -= 1
                font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

            # Calcular el tamaño de la caja del texto
            text_bbox_normal = draw_normal.textbbox((0, 0), text, font=font)
            text_width_normal = text_bbox_normal[2] - text_bbox_normal[0]
            text_height_normal = text_bbox_normal[3] - text_bbox_normal[1]
            # Calcular la posicion central
            text_x_normal = (width - text_width_normal) / 2
            text_y_normal = (height - text_height_normal) / 2
            
            # Definir el color del texto basado en el tema actual
            text_color = WHITE if current_theme == "dark" else BLACK

            # Dibujar el texto en la primera imagen
            draw_normal.text(
                (text_x_normal, text_y_normal), text, font=font, fill=text_color
            )

            # Guarda la imagen modificada para la primera imagen
            button_image_normal_tk = ImageTk.PhotoImage(button_image_normal)

            # Crea un objeto draw para la segunda imagen
            draw_pressed = ImageDraw.Draw(button_image_pressed)

            # Ajusta el tamaño de la fuente para que encaje en la imagen (usar el mismo tamaño calculado para la primera)
            font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

            # Calcular el tamaño de la caja del texto
            text_bbox_pressed = draw_pressed.textbbox((0, 0), text, font=font)
            text_width_pressed = text_bbox_pressed[2] - text_bbox_pressed[0]
            text_height_pressed = text_bbox_pressed[3] - text_bbox_pressed[1]
            # Calcular la posicion central
            text_x_pressed = (width - text_width_pressed) / 2
            text_y_pressed = (height - text_height_pressed) / 2
             # Definir el color del texto basado en el tema actual
            text_color = WHITE if current_theme == "dark" else BLACK
            # Dibujar el texto en la segunda imagen
            draw_pressed.text(
                (text_x_pressed, text_y_pressed), text, font=font, fill=text_color
            )

            # Guarda la imagen modificada para la segunda imagen
            button_image_pressed_tk = ImageTk.PhotoImage(button_image_pressed)

            # Crear el botón como una etiqueta con imagen
            button_label = tk.Label(config_overlay, image=button_image_normal_tk, bg="black" if current_theme == "dark" else "white", borderwidth=0, highlightthickness=0)
            button_label.image_normal = button_image_normal_tk
            button_label.image_pressed = button_image_pressed_tk
            button_label.place(x=x, y=y)
            
            # Cargar la imagen del icono si se proporciona
            
            if icon_image_path:
                if aero_menu and current_effect == "flat" and text != "Efecto Plano":
                    icon_image_path = "Resources/CloseTextureFlat01.png"
                icon_image = Image.open(icon_image_path)
                icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
                icon_image_tk = ImageTk.PhotoImage(icon_image)
                icon_label = tk.Label(config_overlay, image=icon_image_tk, bg="black" if current_theme == "dark" else "white", borderwidth=0, highlightthickness=0)
                icon_label.image = icon_image_tk  # Guardar la referencia
                icon_label.place(x=x + button_image_normal.width + 10, y=y + (button_image_normal.height - 32) // 2)
            
            if icon_default:
               icon_image = Image.open("Resources/Selected.png")
               if aero_menu and current_effect == "flat":
                  icon_image = Image.open("Resources/SelectedFlat.png")
               icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
               icon_image_tk = ImageTk.PhotoImage(icon_image)
               icon_label = tk.Label(config_overlay, image=icon_image_tk, bg="black" if current_theme == "dark" else "white", borderwidth=0, highlightthickness=0)
               icon_label.image = icon_image_tk  # Guardar la referencia
               icon_label.place(x=x + button_image_normal.width + 10, y=y + (button_image_normal.height - 32) // 2)

            # Funcion para cambiar entre imagenes al clickear
            def button_click(event):
                button_label.config(image=button_label.image_pressed)
                config_overlay.after(
                    100, lambda: button_label.config(image=button_label.image_normal)
                )
                play_sound("Resources/Button.wav")
                command()

            # Funciones para animar al pasar el ratón
            def on_enter(event):
                button_label.config(image=button_label.image_pressed)

            def on_leave(event):
                button_label.config(image=button_label.image_normal)

            button_label.bind("<Button-1>", button_click)
            button_label.bind("<Enter>", on_enter)
            button_label.bind("<Leave>", on_leave)

            return button_label
        
        def show_theme_config_menu():
            global config_active, config_overlay
            global current_theme
            if config_active:
                config_active = False
                config_overlay.destroy()

            config_active = True
                # Crear una capa semitransparente
            config_overlay = tk.Toplevel(root)
            config_overlay.attributes('-fullscreen', True)
            config_overlay.attributes('-alpha', 0.7)
            config_overlay.configure(bg="black" if current_theme == "dark" else "white")

            # Colocar la textura de fondo
            background_texture = Image.open("Resources/MenuTexture.png")
            background_texture_tk = ImageTk.PhotoImage(background_texture)
            background_label = tk.Label(config_overlay, image=background_texture_tk, bg="black" if current_theme == "dark" else "white")
            background_label.image = background_texture_tk
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Cargar las imagenes del boton de cerrar
            if current_effect == "glass":
               close_button_image_normal = Image.open("Resources/CloseTexture01.png")
               close_button_image_pressed = Image.open("Resources/CloseTexture02.png")
            elif current_effect == "basic":
                close_button_image_normal = Image.open("Resources/CloseTextureBasic01.png")
                close_button_image_pressed = Image.open("Resources/CloseTextureBasic02.png")
            else:  # flat
                close_button_image_normal = Image.open("Resources/CloseTextureFlat01.png")
                close_button_image_pressed = Image.open("Resources/CloseTextureFlat02.png")
            
            close_button_image_normal_tk = ImageTk.PhotoImage(close_button_image_normal)
            close_button_image_pressed_tk = ImageTk.PhotoImage(close_button_image_pressed)
            
            
            def on_close_enter(event):
                close_button_label.config(image=close_button_image_pressed_tk)

            def on_close_leave(event):
                close_button_label.config(image=close_button_image_normal_tk)
                
            def close_config_menu():
                global config_active
                config_active = False
                play_sound("Resources/Close.mp3")
                config_overlay.destroy()
            
            def open_screen_config_menu():
              close_config_menu()
              show_screen_config_menu()
                
            # Crear el botón de cerrar como una etiqueta con imagen
            close_button_label = tk.Label(config_overlay, image=close_button_image_normal_tk, bg="black" if current_theme == "dark" else "white", borderwidth=0, highlightthickness=0)
            close_button_label.image = close_button_image_normal_tk  # mantén la referencia
            close_button_label.place(relx=0.95, rely=0.05, anchor="ne")
            
            # Asociar los eventos para la animación del botón
            close_button_label.bind("<Enter>", on_close_enter)
            close_button_label.bind("<Leave>", on_close_leave)
            close_button_label.bind("<Button-1>", lambda event: open_screen_config_menu())
            
            def change_theme_to_light():
                global current_theme
                current_theme = "light"
                show_main_menu()
                open_screen_config_menu()

            def change_theme_to_dark():
               global current_theme
               current_theme = "dark"
               show_main_menu()
               open_screen_config_menu()

            def change_theme_to_schedule():
                global current_theme
                update_theme_by_time()
                show_main_menu()
                open_screen_config_menu()

            theme_light_button = create_config_button(
                "Tema Visual Claro",
                50,
                50,
                lambda: change_theme_to_light(),
                "Resources/MenuButtonTexture01.png",
                "Resources/MenuButtonTexture02.png",
                "Resources/CloseTexture01.png" if current_theme != "light" else "Resources/Selected.png"
            )
            theme_dark_button = create_config_button(
                "Tema Visual Oscuro",
                50,
                150,
                lambda: change_theme_to_dark(),
                "Resources/MenuButtonTexture01.png",
                "Resources/MenuButtonTexture02.png",
                "Resources/Selected.png" if current_theme == "dark" else "Resources/CloseTexture01.png"
            )
            theme_schedule_button = create_config_button(
                "Tema Visual Horario",
                50,
                250,
                lambda: change_theme_to_schedule(),
                "Resources/MenuButtonTexture01.png",
                "Resources/MenuButtonTexture02.png",
                "Resources/Selected.png" if current_theme == "dark"  else "Resources/CloseTexture01.png"
            )
        
        def show_screen_config_menu():
            global config_active, config_overlay
            global current_theme
            if config_active:
                config_active = False
                config_overlay.destroy()

            config_active = True
                # Crear una capa semitransparente
            config_overlay = tk.Toplevel(root)
            config_overlay.attributes('-fullscreen', True)
            config_overlay.attributes('-alpha', 0.7)
            config_overlay.configure(bg="black" if current_theme == "dark" else "white")

            # Colocar la textura de fondo
            background_texture = Image.open("Resources/MenuTexture.png")
            background_texture_tk = ImageTk.PhotoImage(background_texture)
            background_label = tk.Label(config_overlay, image=background_texture_tk, bg="black" if current_theme == "dark" else "white")
            background_label.image = background_texture_tk
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Cargar las imagenes del boton de cerrar
            if current_effect == "glass":
               close_button_image_normal = Image.open("Resources/CloseTexture01.png")
               close_button_image_pressed = Image.open("Resources/CloseTexture02.png")
            elif current_effect == "basic":
                close_button_image_normal = Image.open("Resources/CloseTextureBasic01.png")
                close_button_image_pressed = Image.open("Resources/CloseTextureBasic02.png")
            else:  # flat
                close_button_image_normal = Image.open("Resources/CloseTextureFlat01.png")
                close_button_image_pressed = Image.open("Resources/CloseTextureFlat02.png")
            
            close_button_image_normal_tk = ImageTk.PhotoImage(close_button_image_normal)
            close_button_image_pressed_tk = ImageTk.PhotoImage(close_button_image_pressed)
            
            
            def on_close_enter(event):
                close_button_label.config(image=close_button_image_pressed_tk)

            def on_close_leave(event):
                close_button_label.config(image=close_button_image_normal_tk)
                
            def close_config_menu():
                global config_active
                config_active = False
                play_sound("Resources/Close.mp3")
                config_overlay.destroy()
            
            def open_main_config_menu():
              close_config_menu()
              show_config_menu()
                
            # Crear el botón de cerrar como una etiqueta con imagen
            close_button_label = tk.Label(config_overlay, image=close_button_image_normal_tk, bg="black" if current_theme == "dark" else "white", borderwidth=0, highlightthickness=0)
            close_button_label.image = close_button_image_normal_tk  # mantén la referencia
            close_button_label.place(relx=0.95, rely=0.05, anchor="ne")
            
            # Asociar los eventos para la animación del botón
            close_button_label.bind("<Enter>", on_close_enter)
            close_button_label.bind("<Leave>", on_close_leave)
            close_button_label.bind("<Button-1>", lambda event: open_main_config_menu())
                
            theme_config_button = create_config_button(
                "Tema Visual",
                50,
                50,
                 lambda: show_theme_config_menu(),
                "Resources/MenuButtonTexture01.png",
                "Resources/MenuButtonTexture02.png",
                "Resources/Visual.png"
            )
            aero_effects_button = create_config_button(
                "Efectos Aero",
                50,
                150,
                lambda: show_aero_config_menu(),
                "Resources/MenuButtonTexture01.png",
                "Resources/MenuButtonTexture02.png",
                "Resources/AeroEffects.png"
            )
        
            
        screen_config_button = create_config_button(
            "Configuración de Pantalla",
            50,
            50,
             lambda: show_screen_config_menu(),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/DisplayConfig.png"
        )
        audio_config_button = create_config_button(
            "Configuración de Audio",
            50,
            150,
            lambda: print("Configuración de audio"),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/AudioConfig.png"
        )
        language_config_button = create_config_button(
            "Lenguaje",
            50,
            250,
            lambda: print("Configuración de lenguaje"),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/LanguageConfig.png"
        )
        general_config_button = create_config_button(
            "Configuración General",
            50,
            350,
            lambda: print("Configuración general"),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/Settings.png"
        )
        trophies_config_button = create_config_button(
            "Configuración de Trofeos",
            50,
            450,
            lambda: print("Configuración de trofeos"),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
             "Resources/TrophyConfig.png"
        )
        credits_button = create_config_button(
            "Créditos",
            50,
            550,
            lambda: print("Créditos"),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/Credits.png"
        )

        def show_aero_config_menu():
            global config_active, config_overlay
            global current_theme, current_effect
            if config_active:
                config_active = False
                config_overlay.destroy()

            config_active = True
                # Crear una capa semitransparente
            config_overlay = tk.Toplevel(root)
            config_overlay.attributes('-fullscreen', True)
            config_overlay.attributes('-alpha', 0.7)
            config_overlay.configure(bg="black" if current_theme == "dark" else "white")

            # Colocar la textura de fondo
            background_texture = Image.open("Resources/MenuTexture.png")
            background_texture_tk = ImageTk.PhotoImage(background_texture)
            background_label = tk.Label(config_overlay, image=background_texture_tk, bg="black" if current_theme == "dark" else "white")
            background_label.image = background_texture_tk
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            
            # Cargar las imagenes del boton de cerrar
            if current_effect == "glass":
               close_button_image_normal = Image.open("Resources/CloseTexture01.png")
               close_button_image_pressed = Image.open("Resources/CloseTexture02.png")
            elif current_effect == "basic":
                close_button_image_normal = Image.open("Resources/CloseTextureBasic01.png")
                close_button_image_pressed = Image.open("Resources/CloseTextureBasic02.png")
            else:  # flat
                close_button_image_normal = Image.open("Resources/CloseTextureFlat01.png")
                close_button_image_pressed = Image.open("Resources/CloseTextureFlat02.png")
            
            close_button_image_normal_tk = ImageTk.PhotoImage(close_button_image_normal)
            close_button_image_pressed_tk = ImageTk.PhotoImage(close_button_image_pressed)
            
            
            def on_close_enter(event):
                close_button_label.config(image=close_button_image_pressed_tk)

            def on_close_leave(event):
                close_button_label.config(image=close_button_image_normal_tk)
                
            def close_config_menu():
                global config_active
                config_active = False
                play_sound("Resources/Close.mp3")
                config_overlay.destroy()
            
            def open_screen_config_menu():
              close_config_menu()
              show_screen_config_menu()
              
            def set_aero_glass_effect():
              global current_effect
              current_effect = "glass"
              show_main_menu()
              open_screen_config_menu()

            def set_aero_basic_effect():
              global current_effect
              current_effect = "basic"
              show_main_menu()
              open_screen_config_menu()

            def set_flat_effect():
              global current_effect
              current_effect = "flat"
              show_main_menu()
              open_screen_config_menu()

             # Crear los botones de efectos Aero
            aero_glass_button = create_config_button(
            "Efecto Aero Glass",
            50,
            50,
            lambda: set_aero_glass_effect(),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/Selected.png" if current_effect == "glass" else "Resources/CloseTexture01.png",
            aero_menu = True
            )
            aero_basic_button = create_config_button(
            "Efecto Aero Basic",
            50,
            150,
            lambda: set_aero_basic_effect(),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/SelectedBasic.png" if current_effect == "basic" else "Resources/CloseTexture01.png",
            aero_menu = True
            )
            flat_effect_button = create_config_button(
            "Efecto Plano",
            50,
            250,
            lambda: set_flat_effect(),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/SelectedFlat.png" if current_effect == "flat" else "Resources/CloseTexture01.png",
            aero_menu = True
            )
            pixel_art_button = create_config_button(
            "Efecto Pixel Art Glory",
            50,
            350,
            lambda: print("Efecto Pixel Art Glory"),
            "Resources/MenuButtonTexture01.png",
            "Resources/MenuButtonTexture02.png",
            "Resources/CloseTexture01.png",
            aero_menu = True
        )

                
            # Crear el botón de cerrar como una etiqueta con imagen
            close_button_label = tk.Label(config_overlay, image=close_button_image_normal_tk, bg="black" if current_theme == "dark" else "white", borderwidth=0, highlightthickness=0)
            close_button_label.image = close_button_image_normal_tk  # mantén la referencia
            close_button_label.place(relx=0.95, rely=0.05, anchor="ne")
            
            # Asociar los eventos para la animación del botón
            close_button_label.bind("<Enter>", on_close_enter)
            close_button_label.bind("<Leave>", on_close_leave)
            close_button_label.bind("<Button-1>", lambda event: open_screen_config_menu())


# Función para mostrar el popup de logro
def show_achievement_popup(description_text, trophy_path):
    global achievement_popup, current_effect
    achievement_popup = tk.Toplevel(root)
    achievement_popup.overrideredirect(True)  # Ocultar la barra de título

    # Cargar la textura de fondo
    if current_effect == "glass":
        badge_image = Image.open("Resources/BadgeTexture01.png")
    elif current_effect == "basic":
        badge_image = Image.open("Resources/BadgeTextureBasic01.png")
    else: # flat
        badge_image = Image.open("Resources/BadgeTextureFlat01.png")

    # Calcula las dimensiones de la textura
    badge_width, badge_height = badge_image.size

    # Crear un objeto draw
    draw = ImageDraw.Draw(badge_image)

    # Define los textos
    achievement_text = "Has obtenido un logro"

    # Define la fuente y su tamaño
    font_size = 20  # Tamaño de fuente inicial (aumentado a 20)
    font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Ajusta el tamaño de la fuente para que encaje en la imagen
    while (
        draw.textbbox((0, 0), achievement_text, font=font)[2] > badge_width - 10
        or draw.textbbox((0, 0), achievement_text, font=font)[3] > badge_height - 40
        or draw.textbbox((0, 0), description_text, font=font)[2] > badge_width - 10
        or draw.textbbox((0, 0), description_text, font=font)[3] > badge_height - 40
    ):
        font_size -= 1
        font = ImageFont.truetype("Resources/Dosis-Regular.ttf", font_size)

    # Calcular la posición vertical central del texto del logro
    text_bbox = draw.textbbox((0, 0), achievement_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (badge_width - text_width) / 2
    text_y = (
        badge_height / 2
    ) - (
        text_height
    ) - 10  # Calcula el centro vertical y resta la altura del texto + un pequeño margen

    # Calcular la posición vertical central del texto de la descripción
    text_bbox2 = draw.textbbox((0, 0), description_text, font=font)
    text_width2 = text_bbox2[2] - text_bbox2[0]
    text_height2 = text_bbox2[3] - text_bbox2[1]
    text_x2 = (badge_width - text_width2) / 2
    text_y2 = (
        badge_height / 2
    ) + 10  # Calcula el centro vertical + un margen para ponerlo abajo del logro

    # Dibuja los textos en la imagen con color blanco
    draw.text((text_x, text_y), achievement_text, font=font, fill="white")
    draw.text((text_x2, text_y2), description_text, font=font, fill="white")

    badge_image_tk = ImageTk.PhotoImage(badge_image)
    badge_label = tk.Label(achievement_popup, image=badge_image_tk, bg="white")
    badge_label.image = badge_image_tk  # Mantener la referencia
    badge_label.pack()

    # Cargar el icono del logro
    trophy_image = Image.open(trophy_path)
    trophy_image_tk = ImageTk.PhotoImage(trophy_image)
    trophy_label = tk.Label(achievement_popup, image=trophy_image_tk, bg="white")
    trophy_label.image = trophy_image_tk
    trophy_label.place(x=10, y=10)  # Ajustar posición si es necesario

    # Centrar el popup en la pantalla y moverlo arriba
    achievement_popup.update_idletasks()
    width = achievement_popup.winfo_width()
    height = achievement_popup.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = 10  # Mostrar en la parte superior de la pantalla
    achievement_popup.geometry(f"{width}x{height}+{x}+{y}")

    # Reproducir sonido
    achievement_sound = pygame.mixer.Sound("Resources/Achievement.mp3")
    achievement_sound.play()

    # Efecto fade-in
    fade_in_popup(
        achievement_popup, 0.0, 0.1
    )  # Inicia con alpha 0 y llega a 0.1 para que no sea invisible.

    # Desaparecer el popup con efecto fade-out después de 5 segundos
    root.after(5000, lambda: fade_out_popup(achievement_popup, 0.1))

def fade_in_popup(popup, alpha, rate):
    """Aplica un efecto de fade-in a un popup."""

    def set_alpha(a):
        if a <= 1:
            popup.attributes("-alpha", a)
            root.after(30, lambda: set_alpha(a + rate))

    set_alpha(alpha)

def fade_out_popup(popup, alpha):
    """Aplica un efecto de fade-out a un popup y lo destruye."""

    def set_alpha(a):
        if a >= 0:
            popup.attributes("-alpha", a)
            root.after(30, lambda: set_alpha(a - 0.05))
        else:
            popup.destroy()

    set_alpha(alpha)

# Mostrar pantalla de carga
update_loading()

# Mostrar el menú principal
show_main_menu()

# Reproducir música de fondo
play_background_music()

# Ejecutar la aplicación
root.mainloop()