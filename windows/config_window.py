import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import cv2
from PIL import Image, ImageTk

# Colores
COLOR_BG = "#003049"
COLOR_TEXT = "#FFFFFF"
COLOR_PRIMARY = "#003049"
COLOR_SUCCESS = "#A1DD70"
COLOR_DANGER = "#FF5555"


class ConfigWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.cam_index_var = tk.StringVar(value="0")
        self.cam_previews = {}
        self.cap_list = {}

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Configuración del Sistema")
        self.window.configure(bg=COLOR_BG)
        self.window.geometry("500x500")

        main = tk.Frame(self.window, bg=COLOR_BG, padx=20, pady=20)
        main.pack(fill="both", expand=True)

        tk.Label(
            main,
            text="⚙️ CONFIGURACIÓN",
            font=("Segoe UI", 18, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=10)

        # ================= CÁMARA =================
        tk.Label(
            main,
            text="📷 Cámara seleccionada",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(anchor="w", pady=5)

        self.cam_label = tk.Label(
            main,
            text="Ninguna seleccionada",
            fg=COLOR_TEXT,
            bg=COLOR_BG
        )
        self.cam_label.pack(anchor="w")

        tk.Button(
            main,
            text="🔍 Ver cámaras disponibles",
            bg=COLOR_PRIMARY,
            fg="white",
            command=self.abrir_selector_camaras
        ).pack(fill="x", pady=10)

        # ================= PARÁMETROS =================
        tk.Label(main, text="Frames confirmación", fg=COLOR_TEXT, bg=COLOR_BG).pack(anchor="w")

        self.frames_var = tk.StringVar(value="5")
        tk.Entry(main, textvariable=self.frames_var).pack(fill="x", pady=5)

        tk.Label(main, text="Umbral (0.5 - 1.0)", fg=COLOR_TEXT, bg=COLOR_BG).pack(anchor="w")

        self.umbral_var = tk.StringVar(value="0.8")
        tk.Entry(main, textvariable=self.umbral_var).pack(fill="x", pady=5)

        # BOTONES
        tk.Button(main, text="💾 Guardar", bg=COLOR_SUCCESS, command=self.save_config).pack(fill="x", pady=10)

        tk.Button(main, text="❌ Cerrar", bg=COLOR_DANGER, fg="white",
                  command=self.window.destroy).pack(fill="x")

        self.cargar_configuracion()

    # ================= SELECTOR DE CÁMARAS =================
    def abrir_selector_camaras(self):
        win = tk.Toplevel(self.window)
        win.title("Selector de cámaras")
        win.geometry("900x500")
        win.configure(bg=COLOR_BG)

        container = tk.Frame(win, bg=COLOR_BG)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="📷 Selecciona una cámara",
                 font=("Segoe UI", 14, "bold"),
                 fg=COLOR_TEXT, bg=COLOR_BG).pack(pady=10)

        grid = tk.Frame(container, bg=COLOR_BG)
        grid.pack()

        self.cap_list = {}
        self.cam_previews = {}

        for i in range(5):
            cap = cv2.VideoCapture(i)  # 🔥 SIN CAP_DSHOW

            if cap.isOpened():
                ret, frame = cap.read()

                if ret:
                    frame = cv2.resize(frame, (250, 180))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(img)

                    cam_frame = tk.Frame(grid, bg="white", bd=2, relief="groove")
                    cam_frame.grid(row=0, column=i, padx=10)

                    lbl = tk.Label(cam_frame, image=imgtk)
                    lbl.image = imgtk
                    lbl.pack()

                    tk.Label(cam_frame, text=f"Cámara {i}").pack()

                    tk.Button(
                        cam_frame,
                        text="Seleccionar",
                        bg=COLOR_SUCCESS,
                        command=lambda idx=i: self.seleccionar_camara(idx, win)
                    ).pack(pady=5)

                    self.cap_list[i] = cap
                    self.cam_previews[i] = lbl

                    self.actualizar_preview(i)
                else:
                    cap.release()
            else:
                cap.release()

    def actualizar_preview(self, i):
        cap = self.cap_list.get(i)

        if cap:
            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (250, 180))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(img)

                label = self.cam_previews[i]
                label.configure(image=imgtk)
                label.image = imgtk

            label.after(30, lambda: self.actualizar_preview(i))

    def seleccionar_camara(self, index, window):
        self.cam_index_var.set(str(index))
        self.cam_label.config(text=f"🎥 Cámara seleccionada: {index}")

        for cap in self.cap_list.values():
            cap.release()

        window.destroy()

    def cargar_configuracion(self):
        try:
            with open("config.pkl", "rb") as f:
                config = pickle.load(f)
                self.cam_index_var.set(str(config.get("camera_index", 0)))
                self.cam_label.config(text=f"🎥 Cámara: {self.cam_index_var.get()}")
        except:
            pass

    def save_config(self):
        try:
            config = {
                "camera_index": int(self.cam_index_var.get()),
                "frames_confirmacion": int(self.frames_var.get()),
                "umbral_reconocimiento": float(self.umbral_var.get()),
                "backend": "AUTO"
            }

            with open("config.pkl", "wb") as f:
                pickle.dump(config, f)

            messagebox.showinfo("OK", "Configuración guardada")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))