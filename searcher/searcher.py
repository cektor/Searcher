import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QListWidget, QMessageBox, QHBoxLayout, QCheckBox, QComboBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

def get_logo_path():
    """Logo dosyasının yolunu döndürür."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "searcherlo.png")
    elif os.path.exists("/usr/share/icons/hicolor/48x48/apps/searcherlo.png"):
        return "/usr/share/icons/hicolor/48x48/apps/searcherlo.png"
    elif os.path.exists("searcherlo.png"):
        return "searcherlo.png"
    return None

def get_icon_path():
    """Simge dosyasının yolunu döndürür."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "searcherlo.png")
    elif os.path.exists("/usr/share/icons/hicolor/48x48/apps/searcherlo.png"):
        return "/usr/share/icons/hicolor/48x48/apps/searcherlo.png"
    return None

LOGO_PATH = get_logo_path()
ICON_PATH = get_icon_path()

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
        
        # About text
        about_text = QLabel("""
        <h2>Searcher</h2>
        <p>Gelişmiş Dosya Arama Uygulaması</p>
        <p>Kullanıcıların bilgisayarlarındaki dosyaları hızlı ve etkili bir şekilde aramasını sağlar. Uygulama, belirli dosya adlarını veya içeriklerini aramak için genişletilmiş arama seçenekleri sunar. Kullanıcılar, arama sonuçlarını dosya adlarına veya içeriklerine göre filtreleyebilir ve sonuçları listeleyebilir. Ayrıca, dosya konumlarını açmak için dosya yöneticilerini kullanarak dosyaları kolayca açabilirler. Kullanıcı dostu arayüzü ve özelleştirilebilir arama seçenekleriyle, Searcher, kullanıcıların dosya yönetimlerini kolaylaştıran bir araçtır.</p>
        <p>Geliştirici: ALG Yazılım Inc.©\n</p>
        <p>www.algyazilim.com | info@algyazilim.com\n\n</p>
        <p>Fatih ÖNDER (CekToR) | fatih@algyazilim.com\n</p>
        <p>GitHub: https://github.com/cektor\n\n</p>
        <p>Sürüm: 1.0</p>
        <p>ALG Yazılım Pardus'a Göç'ü Destekler.\n\n</p>
        <p>Telif Hakkı © 2024 GNU .</p>
        """)
        about_text.setAlignment(Qt.AlignCenter)
        about_text.setStyleSheet("color: white;")
        about_text.setWordWrap(True)  # Taşan metni alt satıra geçirir.
        about_text.setOpenExternalLinks(True)
        about_text.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Metin seçilebilir ve kopyalanabilir
        
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
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Searcher")
        self.setGeometry(100, 100, 800, 600)

        # Pencere simgesi ayarla
        if ICON_PATH and os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        # Tema ve stil ayarları
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #eeeeee;
            }
            QLineEdit {
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
            QLabel {
                color: #eeeeee;
                font-size: 14px;
            }
        """)

        # Logo label
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
        
        # About button
        about_button = QPushButton("Hakkında")
        about_button.clicked.connect(self.show_about_dialog)

        self.result_list = QListWidget()
        self.result_list.setEnabled(False)

        # Dosya formatları için ComboBox (Başlangıçta gizli)
        self.format_label = QLabel("Dosya uzantısı seçin:")
        self.format_label.setStyleSheet("color: #eeeeee;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Dosya Uzantısı Seçin!", "txt", "doc", "docx", "rtf", "html", "htm", "xls", "xlsx", "csv", "ods", "json", "xml", "sql", "mdb", "accdb", "py", "js", "php", "java", "c", "cpp", "sh", "bat"])
        self.format_combo.setStyleSheet("color: #eeeeee; background-color: #1e1e1e;")
        self.format_label.hide()
        self.format_combo.hide()

        # Kök dizin arama için CheckBox
        self.root_directory_checkbox = QCheckBox("Bağlı disklerde ara")
        self.root_directory_checkbox.setStyleSheet("color: #eeeeee;")

        # Dosya içeriklerinde arama için CheckBox
        self.content_search_checkbox = QCheckBox("Dosya içeriklerinde ara")
        self.content_search_checkbox.setStyleSheet("color: #eeeeee;")

        # Sonuç sayısı etiketi
        self.result_count_label = QLabel()
        self.result_count_label.setAlignment(Qt.AlignCenter)
        self.result_count_label.setStyleSheet("color: #66ff66; font-size: 16px;")

        # Layout oluşturma
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.search_button)
        input_layout.addWidget(about_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(logo_label)
        main_layout.addWidget(self.label)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.root_directory_checkbox)
        main_layout.addWidget(self.content_search_checkbox)
        main_layout.addWidget(self.format_label)
        main_layout.addWidget(self.format_combo)
        main_layout.addWidget(self.result_list)
        main_layout.addWidget(self.result_count_label)
        self.setLayout(main_layout)

        # Sinyaller ve slotlar
        self.search_button.clicked.connect(self.search_file)
        self.content_search_checkbox.stateChanged.connect(self.toggle_format_options)
        self.result_list.itemClicked.connect(self.open_file_location)
        about_button.clicked.connect(self.show_about_dialog)

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def toggle_format_options(self):
        if self.content_search_checkbox.isChecked():
            self.format_label.show()
            self.format_combo.show()
        else:
            self.format_label.hide()
            self.format_combo.hide()

    def search_file(self):
        search_query = self.input.text().strip()
        selected_format = self.format_combo.currentText() if self.content_search_checkbox.isChecked() else None

        if not search_query:
            QMessageBox.warning(self, "Hata", "Lütfen aranacak kelimeyi veya dosya adını girin.")
            return

        self.result_list.clear()
        self.result_list.setEnabled(False)
        self.result_count_label.clear()
        self.label.setText("Arama yapılıyor, lütfen bekleyin...")
        self.label.setStyleSheet("color: #ffcc00;")
        QApplication.processEvents()

        try:
            if self.root_directory_checkbox.isChecked():
                search_paths = ["/media", "/mnt"]  # diskler ve bağlı cihazlar
            else:
                search_paths = [os.path.expanduser("~")]  # Kullanıcı ev dizini

            search_path = ' '.join(search_paths)  # Tüm dizinleri birleştir

            if selected_format == "Tüm Dosyalar" or not selected_format:
                search_command = f"find {search_path} -type f 2>/dev/null"
            else:
                search_command = f"find {search_path} -type f -name '*.{selected_format}' 2>/dev/null"

            result = subprocess.check_output(search_command, shell=True, text=True)
            file_paths = result.strip().split("\n")

            matching_files = []

            if self.content_search_checkbox.isChecked():
                for file_path in file_paths:
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                        if search_query in content:
                            matching_files.append(file_path)
                    except Exception:
                        continue
            else:
                for file_path in file_paths:
                    if search_query in os.path.basename(file_path):
                        matching_files.append(file_path)

            if matching_files:
                for file in matching_files:
                    self.result_list.addItem(file)
                self.result_list.setEnabled(True)
                self.label.setText("Arama tamamlandı. Listeden seçim yapabilirsiniz.")
                self.label.setStyleSheet("color: #66ff66;")
                self.result_count_label.setText(f"Sonuç sayısı: {len(matching_files)}")
            else:
                self.label.setText("Hiçbir sonuç bulunamadı.")
                self.label.setStyleSheet("color: #ff6666;")
        except subprocess.CalledProcessError:
            self.label.setText("Arama sırasında bir hata oluştu.")
            self.label.setStyleSheet("color: #ff6666;")
        except Exception as e:
            self.label.setText(f"Bir hata oluştu: {e}")
            self.label.setStyleSheet("color: #ff6666;")


    def open_file_location(self, item):
        file_path = item.text()
        file_dir = os.path.dirname(file_path)
        try:
            if sys.platform.startswith('linux'):
                subprocess.run(["xdg-open", file_dir])
            elif sys.platform.startswith('win32'):
                os.startfile(file_dir)
            elif sys.platform.startswith('darwin'):
                subprocess.run(["open", file_dir])
            else:
                QMessageBox.warning(self, "Hata", "Dosya yöneticisi açılamadı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya yolunu açarken bir hata oluştu: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if ICON_PATH:
        app.setWindowIcon(QIcon(ICON_PATH))
    window = FileSearchApp()
    window.show()
    sys.exit(app.exec_())
