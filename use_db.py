from mysql.connector import connect, Error
import datetime


class DB:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self):
        try:
            with connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
            ) as connection:
                self.connection = connection
        except Error as er:
            print(er)

    def select_data(self, station_name: str, raw_date: str = datetime.date.today()) -> list:
        """
        Получает данные из базы с данными Метостанции.
        site - Название станции
        t1 - Температуру
        p - Давление
        h - Влажность
        +----+-------+------+-----+-----+
        | id |  site |  t1  |  p  |  h  |
        +----+-------+------+-----+-----+
        :param station_name: Название станции
        :param raw_date: Дата
        :return: [{'date': str, 'temperature': float, 'pressure': float, 'humidity': float}]
        """
        select = r"SELECT date, t1, p, h FROM data WHERE site='{site}' AND date BETWEEN '{date}' AND '{date_1} ORDER BY id DESC'"
        selected = select.format(**{'site': station_name,
                                    'date': datetime.date.fromisoformat(raw_date),
                                    'date_1': datetime.date.fromisoformat(raw_date) + datetime.timedelta(days=1)})
        data = []
        # Выборка по дате
        with self.connection.cursor() as cursor:
            cursor.execute(selected)
            result = cursor.fetchall()
            # Проверка наличия данных
            if len(result) != 0:
                for row in result:
                    data.append({'date': row[0], 'temperature': row[1], 'pressure': row[2],
                                 'humidity': row[3]})
            # Данные на дату отсутствуют. Берутся данные на последнюю дату.
            else:
                cursor.execute(f'SELECT date FROM data WHERE site={station_name} ORDER BY id DESC LIMIT 1')
                result = cursor.fetchall()
                last_date = result[0][0].strt_date()
                cursor.execute(select.format(**{'site': station_name,
                                                'date': last_date,
                                                'date_1': last_date + datetime.timedelta(days=1)}))
                result = cursor.fetchall()
                if len(result) == 0:
                    raise KeyError('Данные отсутствуют')
                for row in result:
                    data.append(
                        {'date': row[0], 'temperature': row[1], 'pressure': row[2], 'humidity': row[3]})
                print(f'Измерений на {raw_date} нет! Данные взяты на последнюю дату - {last_date}')
        self.connection.close()
        return data
