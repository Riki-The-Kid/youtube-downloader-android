import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import platform
import yt_dlp
import json

class YouTubeDownloaderApp(App):
    def build(self):
        self.title = "YouTube Downloader"
        
        # Layout principale
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Input URL
        url_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        url_layout.add_widget(Label(text='URL YouTube:', size_hint_x=0.3))
        self.url_input = TextInput(multiline=False, size_hint_x=0.7)
        url_layout.add_widget(self.url_input)
        main_layout.add_widget(url_layout)
        
        # Bottone per ottenere info
        self.info_button = Button(text='Ottieni Informazioni Video', size_hint_y=None, height=50)
        self.info_button.bind(on_press=self.get_video_info)
        main_layout.add_widget(self.info_button)
        
        # Info video
        self.video_info_label = Label(text='Inserisci un URL per vedere le informazioni',text_size=(None, None), halign='center')
        main_layout.add_widget(self.video_info_label)
        
        # Selezione formato
        format_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        format_layout.add_widget(Label(text='Formato:', size_hint_x=0.3))
        self.format_spinner = Spinner(text='Seleziona formato', values=[], size_hint_x=0.7)
        format_layout.add_widget(self.format_spinner)
        main_layout.add_widget(format_layout)
        
        # Bottone download
        self.download_button = Button(text='Scarica', size_hint_y=None, height=50, disabled=True)
        self.download_button.bind(on_press=self.start_download)
        main_layout.add_widget(self.download_button)
        
        # Progress bar
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        main_layout.add_widget(self.progress_bar)
        
        # Status label
        self.status_label = Label(text='Pronto', size_hint_y=None, height=30)
        main_layout.add_widget(self.status_label)
        
        self.video_formats = []
        
        return main_layout
    
    def get_video_info(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup("Errore", "Inserisci un URL valido")
            return
        
        self.info_button.disabled = True
        self.status_label.text = "Ottenendo informazioni..."
        
        # Esegui in thread separato per non bloccare l'UI
        threading.Thread(target=self._fetch_video_info, args=(url,)).start()
    
    def _fetch_video_info(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Aggiorna UI nel thread principale
                Clock.schedule_once(lambda dt: self._update_video_info(info), 0)
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)
    
    def _update_video_info(self, info):
        title = info.get('title', 'Titolo non disponibile')
        duration = info.get('duration', 0)
        uploader = info.get('uploader', 'Autore non disponibile')
        
        # Formatta durata
        duration_str = f"{duration//60}:{duration%60:02d}" if duration else "N/A"
        
        self.video_info_label.text = f"Titolo: {title}\nAutore: {uploader}\nDurata: {duration_str}"
        
        # Estrai formati disponibili
        formats = info.get('formats', [])
        self.video_formats = []
        format_options = []
        
        # Aggiungi opzione solo audio
        audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
        if audio_formats:
            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
            self.video_formats.append({
                'format_id': best_audio['format_id'],
                'description': f"Solo Audio - {best_audio.get('ext', 'unknown')} ({best_audio.get('abr', 'unknown')}kbps)",
                'type': 'audio'
            })
            format_options.append(f"Solo Audio - {best_audio.get('ext', 'unknown')} ({best_audio.get('abr', 'unknown')}kbps)")
        
        # Aggiungi formati video+audio
        video_formats = [f for f in formats if f.get('height') and f.get('acodec') != 'none']
        video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
        
        added_heights = set()
        for fmt in video_formats[:5]:  # Limita a 5 formati video
            height = fmt.get('height')
            if height and height not in added_heights:
                self.video_formats.append({
                    'format_id': fmt['format_id'],
                    'description': f"Video {height}p - {fmt.get('ext', 'unknown')}",
                    'type': 'video'
                })
                format_options.append(f"Video {height}p - {fmt.get('ext', 'unknown')}")
                added_heights.add(height)
        
        self.format_spinner.values = format_options
        if format_options:
            self.format_spinner.text = format_options[0]
            self.download_button.disabled = False
        
        self.info_button.disabled = False
        self.status_label.text = "Informazioni ottenute!"
    
    def _show_error(self, error_msg):
        self.info_button.disabled = False
        self.status_label.text = "Errore nell'ottenere le informazioni"
        self.show_popup("Errore", f"Errore: {error_msg}")
    
    def start_download(self, instance):
        if not self.format_spinner.text or self.format_spinner.text == 'Seleziona formato':
            self.show_popup("Errore", "Seleziona un formato")
            return
        
        # Trova il formato selezionato
        selected_format = None
        for i, fmt in enumerate(self.video_formats):
            if self.format_spinner.values[i] == self.format_spinner.text:
                selected_format = fmt
                break
        
        if not selected_format:
            self.show_popup("Errore", "Formato non valido")
            return
        
        self.download_button.disabled = True
        self.progress_bar.value = 0
        self.status_label.text = "Iniziando download..."
        
        # Avvia download in thread separato
        threading.Thread(target=self._download_video, args=(self.url_input.text.strip(), selected_format)).start()
    
    def _download_video(self, url, format_info):
        try:
            # Determina la cartella di download
            if platform == 'android':
                download_path = '/sdcard/Download/YouTubeDownloader'
            else:
                download_path = os.path.expanduser('~/Downloads/YouTubeDownloader')
            
            os.makedirs(download_path, exist_ok=True)
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        Clock.schedule_once(lambda dt: self._update_progress(percent), 0)
                elif d['status'] == 'finished':
                    Clock.schedule_once(lambda dt: self._download_finished(d['filename']), 0)
            
            ydl_opts = {
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'format': format_info['format_id'],
                'progress_hooks': [progress_hook],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self._download_error(str(e)), 0)
    
    def _update_progress(self, percent):
        self.progress_bar.value = min(percent, 100)
        self.status_label.text = f"Download in corso... {percent:.1f}%"
    
    def _download_finished(self, filename):
        self.progress_bar.value = 100
        self.status_label.text = "Download completato!"
        self.download_button.disabled = False
        self.show_popup("Successo", f"Download completato!\nFile salvato in: {filename}")
    
    def _download_error(self, error_msg):
        self.status_label.text = "Errore durante il download"
        self.download_button.disabled = False
        self.show_popup("Errore Download", f"Errore: {error_msg}")
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message, text_size=(300, None), halign='center'))
        
        close_button = Button(text='Chiudi', size_hint_y=None, height=40)
        popup_layout.add_widget(close_button)
        
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.6))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    YouTubeDownloaderApp().run()
