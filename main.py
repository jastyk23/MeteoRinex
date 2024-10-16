from pathlib import Path
import transform_coord
import use_db
from os import environ


class MeteoRinex:
    def __init__(self, station_name: str, coordinates: list, meteo_data: list):
        """
        Собирает MeteoRINEX
        :param station_name: название станции (4 символа)
        :param coordinates: прямоугольные координаты и геодезическая выоста [x, y, z, h]
        :param meteo_data: данные метеостанции [{'date': str, 'temperature': float, 'pressure': float, 'humidity': float}]
        """
        self.name = station_name
        self.date = meteo_data[0]['date'][:10]
        self.coord = {
            'x': coordinates[0],
            'y': coordinates[1],
            'z': coordinates[2],
            'h': coordinates[3]
        }
        self.meteo_data = meteo_data
        self.rinex_head = """     3.04           METEOROLOGICAL DATA                     RINEX VERSION / TYPE
MeteoRinex                              {measure_date} UTC PGM / RUN BY / DATE 
CNG1                                                        MARKER NAME         
     3    PR    TD    HR                                    # / TYPES OF OBSERV 
Vaisala             *Vaisala WXT510                      PR SENSOR MOD/TYPE/ACC 
Vaisala             *Vaisala WXT510                      TD SENSOR MOD/TYPE/ACC 
Vaisala             *Vaisala WXT510                      HR SENSOR MOD/TYPE/ACC 
  {x}  {y}  {z}     {h}  PR SENSOR POS XYZ/H    
  {x}  {y}  {z}     {h}  TD SENSOR POS XYZ/H    
  {x}  {y}  {z}     {h}  HR SENSOR POS XYZ/H    
                                                            END OF HEADER       """

    @staticmethod
    def len_func(x: str) -> str:
        if len(x) == 3:
            new_x = '   ' + x
        elif len(x) == 4:
            new_x = '  ' + x
        elif len(x) == 5:
            new_x = ' ' + x
        else:
            new_x = x
        return new_x

    def rinex_body(self) -> str:
        measure = ''
        for el in self.meteo_data:
            pres = None
            temp = None
            wet = None
            measure_part_1 = f"\n {el['date'].strftime('%Y')} {el['date'].strftime('%m')} {el['date'].strftime('%d')} {el['date'].strftime('%H')} {el['date'].strftime('%M')} {el['date'].strftime('%S')}"
            tmp_pres = str(round(el['pressure'], 1))
            tmp_temp = str(round(el['temperature'], 1))
            tmp_wet = str(round(el['humidity'], 1))
            pres = self.len_func(tmp_pres)
            temp = self.len_func(tmp_temp)
            wet = self.len_func(tmp_wet)
            measure_part_2 = f" {pres} {temp} {wet}"
            full_measure = measure_part_1 + measure_part_2
            if len(full_measure) < 80:
                n = 81 - len(full_measure)
                measure += full_measure + ' ' * n
            else:
                measure += full_measure
        return measure

    def rinex(self) -> str:
        rinex_head = self.rinex_head.format(**{"measure_date": self.date,
                                               "x": round(self.coord['x'], 4),
                                               "y": round(self.coord['y'], 4),
                                               "z": round(self.coord['z'], 4),
                                               "h": round(self.coord['h'], 4)})
        return rinex_head + self.rinex_body()


if __name__ == '__main__':
    station = {
        'CNG1': {
            'x': 2846194.17,
            'y': 2185227.73,
            'z': 5255558.03
        }
    }
    host = environ.get('HOST')
    db_name = environ.get('DB_NAME')
    user_name = environ.get('USER')
    passw = environ.get('PASSWORD')
    db_data = {'host': host,
                'user': user_name,
                'password': passw,
                'database': db_name}
    raw_date = "2022-11-20"
    transform_coord = transform_coord.Transformation(xyz=[station['CNG1']['x'], station['CNG1']['y'], station['CNG1']['z']])
    coord = transform_coord.transformCoord('GSK2011', 'WGS84')
    coord.append(transform_coord.toGeodeticCoord('GSK2011')[2])
    db = use_db.DB(host=db_data['host'], user=db_data['user'], password=db_data['password'], database=db_data['database'])
    db.connect()
    data = db.select_data('CNG1', raw_date)
    date = data[0]['date']
    rinex = MeteoRinex(station_name='CNG1', meteo_data=data, coordinates=coord)
    path = Path(f'Rinex/{date.date()}')
    path.mkdir(parents=True, exist_ok=True)
    with open(
            f'Rinex/{date.date()}/CNG100RUS_U_{date.strftime("%Y")}{date.strftime("%j")}0000_01D_MM.rnx',
            'w') as file:
        file.write(rinex.rinex())
