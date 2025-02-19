import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from rosreestr2coord import Area
import subprocess
import sys
import re
from xml.etree.ElementTree import tostring
import json

# Автоустановка зависимостей
def install_dependencies():
    try:
        import rosreestr2coord
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rosreestr2coord"])

install_dependencies()

def sanitize_filename(cadastral_number):
    return re.sub(r'[<>:"/\\|?*]', '-', cadastral_number)

save_path = ""

def select_save_path():
    global save_path
    save_path = filedialog.askdirectory()
    if save_path:
        log_text.insert(tk.END, f"Путь сохранения: {save_path}\n")
        log_text.see(tk.END)

def get_kml():
    cadastral_number = entry.get()
    if not cadastral_number:
        messagebox.showerror("Ошибка", "Введите кадастровый номер")
        return

    try:
        area = Area(cadastral_number, area_type=1)
        if area.feature is None:
            raise ValueError("Нет доступных геометрических данных для данного кадастрового номера.")

        kml_data = area.to_kml()
        if not kml_data:
            raise ValueError("Не удалось получить данные KML.")

        kml_string = kml_data if isinstance(kml_data, str) else tostring(kml_data.getroot(), encoding='utf-8').decode('utf-8')

        safe_filename = sanitize_filename(cadastral_number)
        output_path = f"{save_path}/{safe_filename}.kml" if save_path else f"{safe_filename}.kml"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(kml_string)

        log_text.insert(tk.END, f"Файл {output_path} успешно создан!\n")
        log_text.see(tk.END)

    except Exception as e:
        log_text.insert(tk.END, f"Ошибка: {str(e)}\n")
        log_text.see(tk.END)

def get_json():
    cadastral_number = entry.get()
    if not cadastral_number:
        messagebox.showerror("Ошибка", "Введите кадастровый номер")
        return

    try:
        area = Area(cadastral_number, area_type=1)
        if area.feature is None:
            raise ValueError("Нет доступных геометрических данных для данного кадастрового номера.")

        json_data = area.to_geojson()
        if not json_data:
            raise ValueError("Не удалось получить данные в формате JSON.")

        json_data = json.loads(json_data) if isinstance(json_data, str) else json_data

        safe_filename = sanitize_filename(cadastral_number)
        output_path = f"{save_path}/{safe_filename}.json" if save_path else f"{safe_filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        log_text.insert(tk.END, f"Файл {output_path} успешно создан!\n")
        log_text.see(tk.END)

    except Exception as e:
        log_text.insert(tk.END, f"Ошибка: {str(e)}\n")
        log_text.see(tk.END)

def on_closing():
    if messagebox.askyesno("Выход", "Вы действительно хотите выйти?"):
        root.destroy()

def start_drag(event):
    global drag_data
    drag_data = {"x": event.x, "y": event.y}

def do_drag(event):
    x = root.winfo_x() - drag_data["x"] + event.x
    y = root.winfo_y() - drag_data["y"] + event.y
    root.geometry(f"+{x}+{y}")

root = tk.Tk()
root.title("Кадастровый номер в KML и JSON")
root.geometry("500x400")
root.configure(bg="#2C2F33")

root.bind("<Button-1>", start_drag)
root.bind("<B1-Motion>", do_drag)
root.bind("<Escape>", lambda e: on_closing())

frame = tk.Frame(root, bg="#2C2F33")
frame.pack(pady=10, padx=10)

entry = tk.Entry(frame, width=40, font=("Arial", 14), bg="#23272A", fg="white", insertbackground="white")
entry.pack(pady=10)

button_frame = tk.Frame(root, bg="#2C2F33")
button_frame.pack(pady=10)

def create_button(text, command):
    return tk.Button(
        button_frame, text=text, command=command,
        font=("Arial", 12), bg="#7289DA", fg="white", bd=0, padx=10, pady=5,
        activebackground="#5B6EAE", activeforeground="white"
    )

button_kml = create_button("Получить KML", get_kml)
button_kml.pack(pady=5, fill=tk.X)

button_json = create_button("Получить JSON", get_json)
button_json.pack(pady=5, fill=tk.X)

button_path = create_button("Выбрать путь сохранения", select_save_path)
button_path.pack(pady=5, fill=tk.X)

button_exit = create_button("Выход", on_closing)
button_exit.pack(pady=5, fill=tk.X)

log_text = scrolledtext.ScrolledText(root, width=60, height=10, bg="#23272A", fg="white", insertbackground="white")
log_text.pack(pady=10)

root.mainloop()