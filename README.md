# Find Your Book

## Kurulum adımları

* python paketlerini kur
* boş veritabanı yarat

### Python paketleri kuruluşu

```commandline
cd FindYourBook
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Veritabanı yaratma

```sh
cd FindYourBook
source .venv/bin/activate
mkdir database
python -m app.db.init_db
# FindYourBoook/database/books.db oluşmuş olmalı
```


Önemli not, mac kullanıcıları terminalde önce 
```cd PycharmProjects/FindYourBook```
sonra 
```chmod +x click_to_start_MAC.command```
runlamayı unutmayın
