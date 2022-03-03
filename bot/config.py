from os import getenv


class Config():
    DB_USER = getenv("DB_USER")
    DB_PASSWORD = getenv("DB_PASSWORD")
    DB_HOST = getenv("DB_HOST")
    DB_BASE = getenv("DB_BASE")
    GOOGLE_JSON = getenv("GOOGLE_JSON")
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_BASE}"
    DELAY = int(getenv('DELAY'))*60

    GOOGLE_KEY = getenv('GOOGLE_KEY')
    GOOGLE_TABLE_HALL = getenv('GOOGLE_TABLE_HALL')
    API_TOKEN = getenv('API_TOKEN')
    CHECK_ONE = ['км', 'дата', 'город', 'артист', 'площадка', 'исполнитель', 'примечание', 'менеджер']
    TIME_SLEEP = 7
    ROW_HEAD_HALL = ['ГОРОД', 'НАИМЕНОВАНИЕ', 'АДРЕС', 'ЗАМЕТКИ', 'КОНТАКТ. ЛИЦО', 'САЙТ']
