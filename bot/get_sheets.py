from db import db_session
from config import Config
import gspread
from models import Schedule, Month, Users
from datetime import datetime
import logging

# # Указываем путь к JSON
gc = gspread.service_account(filename='mypythonsheets-339911-57bc2e8e8e89.json')
# #Открываем таблицу SmartPRO Расписание"
table = gc.open_by_key(Config.GOOGLE_KEY)


class GetSheets:
    def __init__(self, filename=None, table_key=None):
        self.gc = self.init_app(filename)
        self.table = self.get_table(table_key)
        self.results = []
        self.results_msg = []

    @staticmethod
    def init_app(filename=None):
        """Иницилизация пользователя для работы google таблицами.
        filename - это путь до файла json"""
        if filename is None:
            raise 'Неверный json файл'
        return gspread.service_account(filename=filename)

    def get_table(self, table_key):
        """Выбор таблицы. Надо дополнить"""
        if table_key is None:
            raise 'Невыбрана тиблица'
        return self.gc.open_by_key(table_key)

    def get_sheet_table(self):
        """Проверка всех листов из таблицы, если их нет добавляем в базу данных"""
        list_sheets = []
        for i in self.table.worksheets():
            if Month.exists(i.title) is None:
                Month.set_moth(title=i.title)
                self.set_data_worksheet(i)
            list_sheets.append(i)
        return list_sheets

    @staticmethod
    def set_data_worksheet(worksheet):
        list_of_lists = worksheet.get_all_values()
        sheet = Month.query.filter(Month.title == worksheet.title).first()
        data_sheet_list = []
        for i in list_of_lists:
            first_str = list_of_lists[0][0]
            check = True
            if Schedule.query.filter(Schedule.first_str == first_str).first() is None:
                if i != list_of_lists[0] and Config.CHECK_ONE != i:
                    if i[1] != '':
                        my_date = datetime.strptime(i[1], "%d.%m.%Y").date()
                        check = False
                    data_sheet_list.append(Schedule(
                        km=i[0],
                        date=my_date,
                        city=i[2],
                        artist=i[3],
                        playground=i[4],
                        executor=i[5],
                        note=i[6],
                        manager=i[7],
                        month_id=sheet.id,
                        first_str=first_str,
                        check=check
                    ))
        Schedule.set_data(data_sheet_list)

    ######################################################################
    def search_data_changes_sheet(self, sheets):
        self.results = []
        for sheet in sheets:
            month = Month.query.filter(Month.title == sheet.title).first()
            if month is not None:
                data = Schedule.query.filter(Schedule.month_id == month.id).all()
                self.data_loading(sheet, data)
        return self.results

    def data_loading(self, sheet, data):
        list_of_lists = sheet.get_all_values()
        self.check_data_has_changed(list_of_lists, data)

    def check_data_has_changed(self, list_of_lists, data):
        my_date = None
        dom = True
        for i in data:
            for n in list_of_lists:
                if i.date.strftime("%d.%m.%Y") == n[1] and my_date != n[1]:
                    my_date = n[1]
                    self.results.append((i, n))

                    break
                if i.date.strftime("%d.%m.%Y") == n[1] and my_date == n[1] and dom:
                    dom = False
                if my_date == i.date.strftime("%d.%m.%Y") and n[1] == '' and dom is False:
                    dom = True
                    my_date = None
                    self.results.append((i, n))

    ######################################################################
    def chech_in(self, lists):
        self.results_msg = []
        for model, row in lists:
            self.update_db(model, row)
        if self.results_msg:
            return self.results_msg

    def update_db(self, i, n):
        if i.km != n[0] or n[2] != i.city or n[3] != i.artist or n[4] != i.playground or n[5] != i.executor or n[
            6] != i.note or i.manager != n[7]:

            if i.city == '' and i.artist == '' and i.playground == '':
                bool = True
            else:
                bool = False


            i.km = n[0]
            i.city = n[2]
            i.artist = n[3]
            i.playground = n[4]
            i.executor = n[5]
            i.note = n[6]
            i.manager = n[7]
            db_session.commit()
            self.preparing_a_message(i, bool)
            # preparing_a_message(i, message)

    def preparing_a_message(self, model, bool):
        if model.city != '' and model.artist != '':
            self.results_msg.append((model, bool))
