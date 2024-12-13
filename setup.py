from setuptools import setup, find_packages

setup(
    name="searcher",  # Paket adı
    version="1.0",  # Paket sürümü
    description="Searcher - Advanced Search Manager",  # Paket açıklaması
    author="Fatih Önder",  # Paket sahibi adı
    author_email="fatih@algyazilim.com",  # Paket sahibi e-posta adresi
    url="https://github.com/cektor/Searcher",  # Paket deposu URL'si
    packages=find_packages(),  # Otomatik olarak tüm alt paketleri bulur
    install_requires=[
        'PyQt5>=5.15.0',  # PyQt5 bağımlılığı (versiyon sınırı belirtilmiş)
        'Pillow>=8.0.0',  # Pillow bağımlılığı (versiyon sınırı belirtilmiş)
        'PyPDF2>=1.26.0',  # PyPDF2 bağımlılığı (versiyon sınırı belirtilmiş)
    ],
    package_data={
        'searcher': ['*.png', '*.desktop'],  # 'searcher' paketine dahil dosyalar
    },
    data_files=[
        ('share/applications', ['searcher.desktop']),  # Uygulama menüsüne .desktop dosyasını ekler
        ('share/icons/hicolor/48x48/apps', ['searcherlo.png']),  # Simgeyi uygun yere ekler
    ],
    entry_points={
        'gui_scripts': [
            'searcher=searcher:main',  # `searcher` modülündeki `main` fonksiyonu çalıştırılır
        ]
    },
)
