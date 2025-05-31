import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import asyncio
import threading
import os

class YouTubeDownloader(toga.App):
    def startup(self):
        """Costruisce e mostra l'applicazione Toga."""
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Titolo
        title_label = toga.Label(
            "YouTube Downloader",
            style=Pack(padding=10, font_size=20, font_weight="bold", text_align="center")
        )
        
        # Input URL
        self.url_input = toga.TextInput(
            placeholder="Incolla qui l'URL di YouTube...",
            style=Pack(padding=5, flex=1, height=40)
        )
        
        # Bottone download
        download_button = toga.Button(
            "📥 Scarica Video",
            on_press=self.download_video,
            style=Pack(padding=10, height=50, background_color="#FF0000")
        )
        
        # Label di stato
        self.status_label = toga.Label(
            "Pronto per scaricare",
            style=Pack(padding=5, text_align="center", color="#555555")
        )
        
        # Progress bar (simulata con label)
        self.progress_label = toga.Label(
            "",
            style=Pack(padding=5, text_align="center", font_family="monospace")
        )
        
        # Aggiungi tutto alla main box
        main_box.add(title_label)
        main_box.add(self.url_input)
        main_box.add(download_button)
        main_box.add(self.status_label)
        main_box.add(self.progress_label)
        
        # Crea la finestra principale
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def download_video(self, widget):
        """Avvia il download del video in un thread separato"""
        url = self.url_input.value.strip()
        
        if not url:
            self.status_label.text = "❌ Inserisci un URL valido!"
            return
        
        if "youtube.com" not in url and "youtu.be" not in url:
            self.status_label.text = "❌ URL non valido (solo YouTube)"
            return
            
        # Avvia download in thread separato per non bloccare UI
        thread = threading.Thread(target=self._download_worker, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _download_worker(self, url):
        """Worker per il download (eseguito in thread separato)"""
        try:
            self.status_label.text = "🔍 Analizzando video..."
            self.progress_label.text = "▓░░░░░░░░░ 10%"
            
            # Simula download (in realtà qui useresti yt-dlp)
            import time
            
            steps = [
                ("🔗 Collegamento al server...", "▓▓░░░░░░░░ 20%"),
                ("📊 Recupero informazioni video...", "▓▓▓░░░░░░░ 30%"), 
                ("🎥 Analisi qualità disponibili...", "▓▓▓▓░░░░░░ 40%"),
                ("📥 Inizio download...", "▓▓▓▓▓░░░░░ 50%"),
                ("📦 Download in corso...", "▓▓▓▓▓▓▓░░░ 70%"),
                ("✅ Finalizzazione...", "▓▓▓▓▓▓▓▓▓░ 90%"),
                ("✅ Download completato!", "▓▓▓▓▓▓▓▓▓▓ 100%")
            ]
            
            for status, progress in steps:
                time.sleep(2)  # Simula tempo di processing
                self.status_label.text = status
                self.progress_label.text = progress
                
            # Reset dopo 3 secondi
            time.sleep(3)
            self.status_label.text = "Pronto per un nuovo download"
            self.progress_label.text = ""
            self.url_input.value = ""
            
        except Exception as e:
            self.status_label.text = f"❌ Errore: {str(e)[:30]}..."
            self.progress_label.text = ""

def main():
    return YouTubeDownloader('YouTube Downloader', 'org.example.youtubedownloader')

if __name__ == '__main__':
    main().main_loop()
