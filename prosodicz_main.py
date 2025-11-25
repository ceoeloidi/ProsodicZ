import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import librosa
import librosa.display
import sounddevice as sd
import soundfile as sf
import threading
import os
from datetime import datetime

class ProsodiczApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prosodicz BY CHIHAB EL OIDI")
        self.root.geometry("1400x900")
        
        # Variables
        self.is_recording = False
        self.audio_data = None
        self.sample_rate = 44100
        self.current_mode = tk.StringVar(value="Déclarative")
        self.current_file = None
        
        # Créer les répertoires de stockage
        self.recordings_dir = "recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
        
        self.setup_ui()
        self.create_menu()
    
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame contrôle (gauche)
        control_frame = ttk.LabelFrame(main_frame, text="Contrôle", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Sélection du mode
        ttk.Label(control_frame, text="Mode d'enregistrement:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        modes = ["Déclarative", "Interrogative", "Exclamative", "Impérative"]
        for mode in modes:
            ttk.Radiobutton(control_frame, text=mode, variable=self.current_mode, 
                           value=mode).pack(anchor=tk.W, padx=20)
        
        # Boutons d'action
        ttk.Label(control_frame, text="Actions:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(20, 10))
        
        ttk.Button(control_frame, text="Enregistrer (5s)", command=self.start_recording).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Importer Audio", command=self.import_audio).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Lire l'audio", command=self.play_audio).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Sauvegarder", command=self.save_recording).pack(fill=tk.X, pady=5)
        
        # Informations
        ttk.Label(control_frame, text="Informations:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(20, 10))
        
        self.info_label = ttk.Label(control_frame, text="Aucune donnée chargée", justify=tk.LEFT)
        self.info_label.pack(anchor=tk.W, pady=5)
        
        # Frame visualisation (droite)
        viz_frame = ttk.LabelFrame(main_frame, text="Visualisation", padding=5)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas_frame = ttk.Frame(viz_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame boutons visualisation
        viz_buttons_frame = ttk.Frame(viz_frame)
        viz_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(viz_buttons_frame, text="Afficher Signal", command=self.plot_signal).pack(side=tk.LEFT, padx=2)
        ttk.Button(viz_buttons_frame, text="Afficher F0", command=self.plot_f0).pack(side=tk.LEFT, padx=2)
        ttk.Button(viz_buttons_frame, text="Afficher Spectrogramme", command=self.plot_spectrogram).pack(side=tk.LEFT, padx=2)
        ttk.Button(viz_buttons_frame, text="Tous", command=self.plot_all).pack(side=tk.LEFT, padx=2)
    
    def create_menu(self):
        """Créer la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Enregistrer
        enregistrer_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Enregistrer", menu=enregistrer_menu)
        enregistrer_menu.add_command(label="Phrase Déclarative", command=lambda: self.menu_record("Déclarative"))
        enregistrer_menu.add_command(label="Phrase Interrogative", command=lambda: self.menu_record("Interrogative"))
        enregistrer_menu.add_command(label="Phrase Exclamative", command=lambda: self.menu_record("Exclamative"))
        enregistrer_menu.add_command(label="Phrase Impérative", command=lambda: self.menu_record("Impérative"))
        
        # Menu Affichage
        affichage_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Affichage", menu=affichage_menu)
        affichage_menu.add_command(label="Signal Déclaratif", command=lambda: self.menu_display("Déclarative"))
        affichage_menu.add_command(label="Signal Interrogatif", command=lambda: self.menu_display("Interrogative"))
        affichage_menu.add_command(label="Signal Exclamatif", command=lambda: self.menu_display("Exclamative"))
        affichage_menu.add_command(label="Signal Impératif", command=lambda: self.menu_display("Impérative"))
        affichage_menu.add_separator()
        affichage_menu.add_command(label="Tous les signaux", command=self.plot_all_types)
    
    def menu_record(self, mode):
        """Enregistrement via menu"""
        self.current_mode.set(mode)
        messagebox.showinfo("Enregistrement", f"Enregistrement en mode: {mode}\nCliquez sur OK pour commencer.")
        self.start_recording()
    
    def menu_display(self, mode):
        """Affichage des signaux via menu"""
        saved_file = os.path.join(self.recordings_dir, f"{mode}_latest.wav")
        if os.path.exists(saved_file):
            self.audio_data, self.sample_rate = librosa.load(saved_file, sr=None)
            self.plot_signal()
        else:
            messagebox.showwarning("Fichier non trouvé", f"Aucun enregistrement {mode} trouvé.")
    
    def start_recording(self):
        """Démarrer l'enregistrement"""
        self.is_recording = True
        thread = threading.Thread(target=self._record_audio)
        thread.start()
    
    def _record_audio(self):
        """Enregistrement audio dans un thread"""
        try:
            duration = 5
            messagebox.showinfo("Enregistrement", f"Enregistrement en cours...\nMode: {self.current_mode.get()}\nDurée: {duration}s")
            
            recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype=np.float32)
            sd.wait()
            
            self.audio_data = recording.flatten()
            self.update_info()
            messagebox.showinfo("Succès", "Enregistrement terminé!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'enregistrement: {str(e)}")
        finally:
            self.is_recording = False
    
    def import_audio(self):
        """Importer un fichier audio"""
        file_types = [("Fichiers Audio", "*.mp3 *.ogg *.wav *.flac"), 
                     ("WAV files", "*.wav"),
                     ("MP3 files", "*.mp3"),
                     ("OGG files", "*.ogg"),
                     ("FLAC files", "*.flac"),
                     ("Tous", "*.*")]
        
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            try:
                self.current_file = file_path
                self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
                self.update_info()
                messagebox.showinfo("Succès", f"Fichier chargé: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de chargement: {str(e)}")
    
    def play_audio(self):
        """Jouer l'audio"""
        if self.audio_data is not None:
            try:
                sd.play(self.audio_data, self.sample_rate)
                messagebox.showinfo("Lecture", "Lecture en cours...")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de lecture: {str(e)}")
        else:
            messagebox.showwarning("Attention", "Aucun audio à lire.")
    
    def save_recording(self):
        """Sauvegarder l'enregistrement"""
        if self.audio_data is not None:
            filename = os.path.join(self.recordings_dir, f"{self.current_mode.get()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            sf.write(filename, self.audio_data, self.sample_rate)
            
            # Aussi sauvegarder comme "latest"
            latest_file = os.path.join(self.recordings_dir, f"{self.current_mode.get()}_latest.wav")
            sf.write(latest_file, self.audio_data, self.sample_rate)
            
            messagebox.showinfo("Succès", f"Fichier sauvegardé: {filename}")
        else:
            messagebox.showwarning("Attention", "Aucun audio à sauvegarder.")
    
    def update_info(self):
        """Mettre à jour les informations"""
        if self.audio_data is not None:
            duration = len(self.audio_data) / self.sample_rate
            info_text = f"Mode: {self.current_mode.get()}\n"
            info_text += f"Durée: {duration:.2f}s\n"
            info_text += f"Fréquence: {self.sample_rate} Hz\n"
            info_text += f"Amplitude: {np.max(np.abs(self.audio_data)):.3f}"
            self.info_label.config(text=info_text)
    
    def plot_signal(self):
        """Afficher le signal audio"""
        if self.audio_data is None:
            messagebox.showwarning("Attention", "Aucun audio chargé.")
            return
        
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        time = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.audio_data))
        ax.plot(time, self.audio_data, linewidth=0.5)
        ax.set_xlabel("Temps (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"Signal Audio - Mode: {self.current_mode.get()}")
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def plot_f0(self):
        """Afficher la fréquence fondamentale F0"""
        if self.audio_data is None:
            messagebox.showwarning("Attention", "Aucun audio chargé.")
            return
        
        try:
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            fig = Figure(figsize=(10, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Calcul de F0 avec librosa
            f0 = librosa.yin(self.audio_data, fmin=50, fmax=400)
            time = librosa.frames_to_time(np.arange(len(f0)), sr=self.sample_rate)
            
            # Filtrer les valeurs invalides (0 = non-voisé)
            f0_filtered = np.where(f0 > 0, f0, np.nan)
            
            ax.plot(time, f0_filtered, linewidth=1.5, color='green')
            ax.set_xlabel("Temps (s)")
            ax.set_ylabel("Fréquence (Hz)")
            ax.set_title(f"Fréquence Fondamentale (F0) - Mode: {self.current_mode.get()}")
            ax.grid(True, alpha=0.3)
            
            # Moyenne F0
            f0_mean = np.nanmean(f0_filtered)
            ax.axhline(y=f0_mean, color='r', linestyle='--', label=f"Moyenne F0: {f0_mean:.1f} Hz")
            ax.legend()
            
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur calcul F0: {str(e)}")
    
    def plot_spectrogram(self):
        """Afficher le spectrogramme"""
        if self.audio_data is None:
            messagebox.showwarning("Attention", "Aucun audio chargé.")
            return
        
        try:
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            fig = Figure(figsize=(10, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            S = librosa.feature.melspectrogram(y=self.audio_data, sr=self.sample_rate)
            S_db = librosa.power_to_db(S, ref=np.max)
            
            img = librosa.display.specshow(S_db, sr=self.sample_rate, x_axis='time', y_axis='mel', ax=ax)
            ax.set_title(f"Spectrogramme - Mode: {self.current_mode.get()}")
            fig.colorbar(img, ax=ax, format='%+2.0f dB')
            
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur spectrogramme: {str(e)}")
    
    def plot_all(self):
        """Afficher tous les graphiques"""
        if self.audio_data is None:
            messagebox.showwarning("Attention", "Aucun audio chargé.")
            return
        
        try:
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            fig = Figure(figsize=(12, 10), dpi=100)
            
            # Signal
            ax1 = fig.add_subplot(311)
            time = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.audio_data))
            ax1.plot(time, self.audio_data, linewidth=0.5)
            ax1.set_ylabel("Amplitude")
            ax1.set_title(f"Signal Audio - Mode: {self.current_mode.get()}")
            ax1.grid(True, alpha=0.3)
            
            # F0
            ax2 = fig.add_subplot(312)
            f0 = librosa.yin(self.audio_data, fmin=50, fmax=400)
            f0_time = librosa.frames_to_time(np.arange(len(f0)), sr=self.sample_rate)
            f0_filtered = np.where(f0 > 0, f0, np.nan)
            ax2.plot(f0_time, f0_filtered, linewidth=1.5, color='green')
            f0_mean = np.nanmean(f0_filtered)
            ax2.axhline(y=f0_mean, color='r', linestyle='--', label=f"Moyenne: {f0_mean:.1f} Hz")
            ax2.set_ylabel("Fréquence (Hz)")
            ax2.set_title("Fréquence Fondamentale (F0)")
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Spectrogramme
            ax3 = fig.add_subplot(313)
            S = librosa.feature.melspectrogram(y=self.audio_data, sr=self.sample_rate)
            S_db = librosa.power_to_db(S, ref=np.max)
            img = librosa.display.specshow(S_db, sr=self.sample_rate, x_axis='time', y_axis='mel', ax=ax3)
            ax3.set_title("Spectrogramme")
            fig.colorbar(img, ax=ax3, format='%+2.0f dB')
            
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur affichage complet: {str(e)}")
    
    def plot_all_types(self):
        """Afficher tous les types d'enregistrements"""
        try:
            types = ["Déclarative", "Interrogative", "Exclamative", "Impérative"]
            existing_files = []
            
            for type_mode in types:
                file_path = os.path.join(self.recordings_dir, f"{type_mode}_latest.wav")
                if os.path.exists(file_path):
                    existing_files.append((type_mode, file_path))
            
            if not existing_files:
                messagebox.showwarning("Attention", "Aucun enregistrement trouvé.")
                return
            
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            n_plots = len(existing_files)
            fig = Figure(figsize=(14, 3*n_plots), dpi=100)
            
            for idx, (type_mode, file_path) in enumerate(existing_files):
                audio, sr = librosa.load(file_path, sr=None)
                
                ax = fig.add_subplot(n_plots, 1, idx+1)
                time = np.linspace(0, len(audio) / sr, len(audio))
                ax.plot(time, audio, linewidth=0.5)
                ax.set_ylabel("Amplitude")
                ax.set_xlabel("Temps (s)")
                ax.set_title(f"Signal - Mode: {type_mode}")
                ax.grid(True, alpha=0.3)
            
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur comparaison: {str(e)}")

def main():
    root = tk.Tk()
    app = ProsodiczApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
