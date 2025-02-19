import tkinter as tk
from tkinter import messagebox, scrolledtext
from rosreestr2coord import Area
import subprocess
import sys
import re  
from xml.etree.ElementTree import tostring 
import json  

def install_dependencies():
    try:
        import rosreestr2coord
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rosreestr2coord"])

install_dependencies()

def sanitize_filename(cadastral_number):
    return re.sub(r'[<>:"/\\|?*]', '-', cadastral_number)

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
        
        if isinstance(kml_data, str):
            kml_string = kml_data
        else:
            kml_string = tostring(kml_data.getroot(), encoding='utf-8').decode('utf-8')
            
        safe_filename = sanitize_filename(cadastral_number)
        output_path = f"{safe_filename}.kml"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(kml_string)

        log_message = f"Файл {output_path} успешно создан!\n"
        log_text.insert(tk.END, log_message)
        log_text.see(tk.END)

    except Exception as e:
        error_message = f"Ошибка: {str(e)}\n"
        log_text.insert(tk.END, error_message)
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
        
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        
        safe_filename = sanitize_filename(cadastral_number)
        output_path = f"{safe_filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        log_message = f"Файл {output_path} успешно создан!\n"
        log_text.insert(tk.END, log_message)
        log_text.see(tk.END)

    except Exception as e:
        error_message = f"Ошибка: {str(e)}\n"
        log_text.insert(tk.END, error_message)
        log_text.see(tk.END)

root = tk.Tk()
root.title("Кадастровый номер в KML и JSON")

entry = tk.Entry(root, width=50)
entry.pack(pady=20)


button_kml = tk.Button(root, text="Получить KML", command=get_kml)
button_kml.pack(pady=10)

button_json = tk.Button(root, text="Получить данные в формате JSON", command=get_json)
button_json.pack(pady=10)

log_text = scrolledtext.ScrolledText(root, width=60, height=15)
log_text.pack(pady=20)

root.mainloop()
