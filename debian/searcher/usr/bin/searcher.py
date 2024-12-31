import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QListWidget, QMessageBox, QHBoxLayout, QCheckBox, QComboBox, QDialog,
    QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import mmap

def get_resource_path(filename):
    """Kaynak dosyalarının yolunu döndürür."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    elif os.path.exists(f"/usr/share/icons/hicolor/48x48/apps/{filename}"):
        return f"/usr/share/icons/hicolor/48x48/apps/{filename}"
    elif os.path.exists(filename):
        return filename
    return None

LOGO_PATH = get_resource_path("searcherlo.png")
ICON_PATH = get_resource_path("searcherlo.png")

# Sabitler güncelleme
MOUNT_PATHS = ['/mnt', '/media']  # Bağlı disk yolları
HOME_DIR = os.path.expanduser('~')
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', '.env'}
MAX_WORKERS = min(multiprocessing.cpu_count(), 4)
CHUNK_SIZE = 100
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def get_mounted_paths():
    """Bağlı disklerin yollarını döndürür"""
    mounted_paths = set()
    for mount_point in MOUNT_PATHS:
        if os.path.exists(mount_point):
            try:
                for item in os.listdir(mount_point):
                    full_path = os.path.join(mount_point, item)
                    if os.path.ismount(full_path):
                        mounted_paths.add(full_path)
            except PermissionError:
                continue
    return mounted_paths

class SearchWorker(QThread):
    """Arama işlemlerini arka planda yürüten worker sınıfı"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, search_query, content_search=False, root_search=False, file_format=None):
        super().__init__()
        self.search_query = search_query.lower()  # Aramayı küçük harfe çevir
        self.content_search = content_search
        self.root_search = root_search  # Bağlı disklerde ara seçeneği
        self.file_format = file_format.lower() if file_format else None
        self.is_running = True
        self.cpu_count = MAX_WORKERS

    def stop(self):
        self.is_running = False

    def run(self):
        try:
            matching_items = set()
            processed_items = 0
            
            # Arama yollarını belirle
            search_paths = [HOME_DIR] if not self.root_search else []

            # Bağlı disklerde ara seçili ise
            if self.root_search:
                # /media dizinindeki bağlı diskleri ekle
                if os.path.exists('/media'):
                    for user in os.listdir('/media'):
                        user_media = os.path.join('/media', user)
                        if os.path.isdir(user_media):
                            try:
                                for device in os.listdir(user_media):
                                    device_path = os.path.join(user_media, device)
                                    if os.path.ismount(device_path):
                                        search_paths.append(device_path)
                            except PermissionError:
                                continue
                
                # /mnt dizinindeki bağlı diskleri ekle
                if os.path.exists('/mnt'):
                    try:
                        for mount in os.listdir('/mnt'):
                            mount_path = os.path.join('/mnt', mount)
                            if os.path.ismount(mount_path):
                                search_paths.append(mount_path)
                    except PermissionError:
                        pass

            with ProcessPoolExecutor(max_workers=self.cpu_count) as executor:
                for base_path in search_paths:
                    if not self.is_running:
                        break
                        
                    for root, dirs, files in os.walk(base_path, topdown=True):
                        if not self.is_running:
                            break

                        # Atlanacak dizinleri filtrele
                        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                        
                        # Önce dizinleri ara
                        for dir_name in dirs:
                            if self.search_query in dir_name.lower():
                                matching_items.add(os.path.join(root, dir_name))
                        
                        # Dosyaları ara
                        current_files = []
                        for name in files:
                            if self.file_format and not name.lower().endswith(f'.{self.file_format}'):
                                continue
                                
                            full_path = os.path.join(root, name)
                            
                            # Dosya adında arama
                            if self.search_query in name.lower():
                                matching_items.add(full_path)
                            # İçerik araması aktifse
                            elif self.content_search:
                                current_files.append(full_path)
                        
                        # İçerik araması
                        if self.content_search and current_files:
                            search_tasks = [(f, self.search_query) for f in current_files]
                            results = executor.map(search_in_file, search_tasks)
                            matching_items.update(r for r in results if r)
                        
                        processed_items += len(files) + len(dirs)
                        self.progress.emit(processed_items)

            self.finished.emit(sorted(matching_items))

        except Exception as e:
            self.error.emit(str(e))

    def is_binary(self, file_path):
        """Dosyanın binary olup olmadığını kontrol et"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk  # Null bayt varsa binary dosyadır
        except:
            return True

def search_in_file(args):
    file_path, search_query = args
    try:
        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            if search_query in content:
                return file_path
    except:
        pass
    return None

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hakkında")
        self.setGeometry(300, 300, 400, 250)
        layout = QVBoxLayout()
        
        # Logo
        logo_label = QLabel()
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            logo_pixmap = QPixmap(LOGO_PATH)
            scaled_logo = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setFixedSize(500, 600)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("Logo Bulunamadı")
        logo_label.setAlignment(Qt.AlignCenter)
        
        about_text = QLabel("""
        <h2>Searcher</h2>
        <p>Gelişmiş Dosya Arama Uygulaması</p>
        <p>Kullanıcıların bilgisayarlarındaki dosyaları hızlı ve etkili bir şekilde aramasını sağlar. 
        Uygulama, belirli dosya adlarını veya içeriklerini aramak için genişletilmiş arama seçenekleri sunar.</p>
        <p>Geliştirici: ALG Yazılım Inc.©</p>
        <p>www.algyazilim.com | info@algyazilim.com</p>
        <p>Fatih ÖNDER (CekToR) | fatih@algyazilim.com</p>
        <p>GitHub: https://github.com/cektor</p>
        <p>Sürüm: 1.0</p>
        <p>ALG Yazılım Pardus'a Göç'ü Destekler.</p>
        <p>Telif Hakkı © 2024 GNU</p>
        """)
        about_text.setAlignment(Qt.AlignCenter)
        about_text.setStyleSheet("color: white;")
        about_text.setWordWrap(True)
        about_text.setOpenExternalLinks(True)
        about_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        layout.addWidget(logo_label)
        layout.addWidget(about_text)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: white;
            }
        """)

class FileSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.search_worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Searcher")
        self.setGeometry(100, 100, 800, 600)

        if ICON_PATH and os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        # Tema ve stil ayarları
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #eeeeee;
            }
            QLineEdit, QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 8px;
                color: #eeeeee;
                font-size: 14px;
            }
            QPushButton {
                background-color: #282828;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 8px;
                color: #eeeeee;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
                color: #eeeeee;
                font-size: 13px;
            }
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 5px;
                text-align: center;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)

        # Logo
        logo_label = QLabel()
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            logo_pixmap = QPixmap(LOGO_PATH)
            scaled_logo = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("Logo Bulunamadı")
        logo_label.setAlignment(Qt.AlignCenter)

        # Ana bileşenler
        self.label = QLabel("Aranacak kelimeyi veya dosya adını girin:")
        self.input = QLineEdit()
        self.search_button = QPushButton("Ara")
        self.about_button = QPushButton("Hakkında")
        self.result_list = QListWidget()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()

        # Dosya formatları için ComboBox
        self.format_label = QLabel("Dosya uzantısı seçin:")
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Dosya Uzantısı Seçin!", "txt", "doc", "docx", "pdf", "rtf", 
            "html", "htm", "xls", "xlsx", "csv", "ods", "json", "xml", 
            "sql", "mdb", "accdb", "py", "js", "php", "java", "c", "cpp", 
            "sh", "bat"
        ])
        self.format_label.hide()
        self.format_combo.hide()

        # Checkboxes
        self.root_directory_checkbox = QCheckBox("Bağlı disklerde ara")
        self.content_search_checkbox = QCheckBox("Dosya içeriklerinde ara")
        
        # Sonuç sayısı etiketi
        self.result_count_label = QLabel()
        self.result_count_label.setAlignment(Qt.AlignCenter)
        self.result_count_label.setStyleSheet("color: #66ff66; font-size: 16px;")

        # Layout oluşturma
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.search_button)
        input_layout.addWidget(self.about_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(logo_label)
        main_layout.addWidget(self.label)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.root_directory_checkbox)
        main_layout.addWidget(self.content_search_checkbox)
        main_layout.addWidget(self.format_label)
        main_layout.addWidget(self.format_combo)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_list)
        main_layout.addWidget(self.result_count_label)
        
        self.setLayout(main_layout)

        # Sinyaller
        self.search_button.clicked.connect(self.start_search)
        self.about_button.clicked.connect(self.show_about_dialog)
        self.content_search_checkbox.stateChanged.connect(self.toggle_format_options)
        self.result_list.itemDoubleClicked.connect(self.open_file_location)
        self.input.returnPressed.connect(self.start_search)

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def toggle_format_options(self):
        is_content_search = self.content_search_checkbox.isChecked()
        self.format_label.setVisible(is_content_search)
        self.format_combo.setVisible(is_content_search)
        
        # İçerik araması seçildiğinde varsayılan uzantıyı txt yap
        if is_content_search:
            self.format_combo.setCurrentText("txt")

    def start_search(self):
        search_query = self.input.text().strip()
        
        if not search_query:
            QMessageBox.warning(self, "Hata", "Lütfen aranacak kelimeyi veya dosya adını girin.")
            return

        self.result_list.clear()
        self.result_list.setEnabled(False)
        self.result_count_label.clear()
        self.label.setText("Arama yapılıyor, lütfen bekleyin...")
        self.label.setStyleSheet("color: #ffcc00;")
        self.search_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # Worker thread'i başlat
        self.search_worker = SearchWorker(
            search_query,
            self.content_search_checkbox.isChecked(),
            self.root_directory_checkbox.isChecked(),
            self.format_combo.currentText() if self.content_search_checkbox.isChecked() else None
        )
        self.search_worker.finished.connect(self.handle_search_results)
        self.search_worker.error.connect(self.handle_search_error)
        self.search_worker.progress.connect(self.update_progress)
        self.search_worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_search_results(self, matching_files):
        self.progress_bar.hide()
        self.search_button.setEnabled(True)

        if matching_files:
            for file in matching_files:
                self.result_list.addItem(file)
            self.result_list.setEnabled(True)
            self.label.setText("Arama tamamlandı. Dosyaya çift tıklayarak konumunu açabilirsiniz.")
            self.label.setStyleSheet("color: #66ff66;")
            self.result_count_label.setText(f"Sonuç sayısı: {len(matching_files)}")
        else:
            self.label.setText("Hiçbir sonuç bulunamadı.")
            self.label.setStyleSheet("color: #ff6666;")

    def handle_search_error(self, error_message):
        self.progress_bar.hide()
        self.search_button.setEnabled(True)
        self.label.setText(f"Bir hata oluştu: {error_message}")
        self.label.setStyleSheet("color: #ff6666;")

    def open_file_location(self, item):
        file_path = item.text()
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        
        # Desteklenen dosya yöneticileri ve komutları
        file_managers = [
            ('nautilus', ['nautilus', '--select', file_path]),
            ('dolphin', ['dolphin', '--select', file_path]),
            ('nemo', ['nemo', file_path]),
            ('thunar', ['thunar', file_dir]),
            ('caja', ['caja', file_dir]),
            ('pcmanfm', ['pcmanfm', file_dir]),
            ('konqueror', ['konqueror', file_dir]),
            ('pantheon-files', ['pantheon-files', file_dir]),
            ('xdg-open', ['xdg-open', file_dir])  # Fallback seçenek
        ]
        
        try:
            if sys.platform.startswith('linux'):
                file_manager_found = False
                
                # Her dosya yöneticisini kontrol et
                for fm_name, fm_command in file_managers:
                    # Dosya yöneticisinin yüklü olup olmadığını kontrol et
                    if os.system(f'which {fm_name} >/dev/null 2>&1') == 0:
                        try:
                            subprocess.run(fm_command)
                            file_manager_found = True
                            break
                        except subprocess.SubprocessError:
                            continue
                
                if not file_manager_found:
                    QMessageBox.warning(self, "Uyarı", 
                        "Desteklenen bir dosya yöneticisi bulunamadı.\n"
                        "Lütfen bir dosya yöneticisi yükleyin.")
                    
            elif sys.platform.startswith('win32'):
                # Windows'ta Explorer ile aç ve dosyayı seç
                subprocess.run(['explorer', '/select,', file_path])
                
            elif sys.platform.startswith('darwin'):
                # macOS'ta Finder ile aç ve dosyayı seç
                subprocess.run(['open', '-R', file_path])
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", 
                f"Dosya yolunu açarken bir hata oluştu:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if ICON_PATH:
        app.setWindowIcon(QIcon(ICON_PATH))
    window = FileSearchApp()
    window.show()
    sys.exit(app.exec_())
