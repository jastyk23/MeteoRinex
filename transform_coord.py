import math

# a: Большая полуось. Радиус экватора.  a = b / (1 - f)
# b: Малая полуось. Полярный радиус  b = a * (1 - f)
# f: Обратное Геометрическое сжатие   f = (a - b) / a
# sqr(e): квадрат первого эксцентриситета  e2 = 2 * f - sqr(f)
# sqr(e_comma): квадрат второго эксцентриситета  e'2 = (sqr(a) - sqr(b)) / sqr(b)

# Параметры эллипсоидов
Ellipsoids = {
    'GSK2011': {
    'a': 6378136.5,
    'f': 1 / 298.2564151,
    },
    'WGS84': {
        'a': 6378136.5,
        'b': 6356752.3142,
        'f': 1 / 298.257223563,
    },
    'SPHERE': {
        'a': 6371000,
        'f': 0,
    },
    'ITRF2008': {
        'a': 6378136.6,
        'f': 1 / 298.25642,
    },
    'ITRF2014': {
        'a': 6378136.6,
        'f': 1 / 298.25642,
    },
    'ITRF2020': {
        'a': 6378137,
        'f': 1 / 298.257222101,
    },
    'SK42': {
        'a': 6378245,
        'f': 1 / 298.3
    },
    'SK95': {
        'a': 6378245,
        'f': 1 / 298.3
    },
    'KRASOVSKIY': {
        'a': 6378245,
        'f': 1 / 298.3
    },
    'BESSEL1841': {
        'a': 6377397.155,
        'f': 1 / 299.15281285
    },
}

# Параметры перехода СК
TransformationParams = {
    'SK42': {
        'GSK2011': {
            'delta_x': 23.557,
            'delta_y': -140.858,
            'delta_z': -79.770,
            'omega_x': -0.0017,
            'omega_y': -0.3464,
            'omega_z': -0.7943,
            'm': -0.2274e-6
        },
        'WGS84': {
            'delta_x': 23.550,
            'delta_y': -140.950,
            'delta_z': -79.800,
            'omega_x': 0.0000,
            'omega_y': -0.3500,
            'omega_z': -0.7900,
            'm': -0.2200e-6
        }
    },
    'SK95': {
        'GSK2011': {
            'delta_x': 24.457,
            'delta_y': -130.798,
            'delta_z': -81.530,
            'omega_x': -0.0017,
            'omega_y': -0.0036,
            'omega_z': -0.1343,
            'm': -0.2274e-6
        },
        'WGS84': {
            'delta_x': 24.470,
            'delta_y': -130.890,
            'delta_z': -81.560,
            'omega_x': 0.0000,
            'omega_y': 0.0000,
            'omega_z': -0.1300,
            'm': -0.2200e-6
        }

    },
    'WGS84': {
        'GSK2011': {
            'delta_x': -0.013,
            'delta_y': 0.092,
            'delta_z': 0.030,
            'omega_x': -0.0017,
            'omega_y': 0.0036,
            'omega_z': -0.0043,
            'm': -0.0074e-6
        },
        'PZ90.11': {
            'delta_x': -0.013,
            'delta_y': 0.106,
            'delta_z': 0.022,
            'omega_x': -0.0023,
            'omega_y': 0.0035,
            'omega_z': -0.0042,
            'm': -0.0080e-6
        }
    },
    'ITRF2008': {
        'GSK2011': {
            'delta_x': 0.002,
            'delta_y': -0.003,
            'delta_z': -0.003,
            'omega_x': +0.000053,
            'omega_y': 0.000093,
            'omega_z': -0.000012,
            'm': 0.0008e-6
        },
        'PZ90.11': {
            'delta_x': 0.003,
            'delta_y': 0.001,
            'delta_z': -0.000,
            'omega_x': -0.000019,
            'omega_y': 0.000042,
            'omega_z': -0.000002,
            'm': -0.0000e-6
        }
    },
    'PZ90.11': {
        'GSK2011': {
            'delta_x': 0.000,
            'delta_y': -0.014,
            'delta_z': 0.008,
            'omega_x': 0.000562,
            'omega_y': 0.000019,
            'omega_z': -0.000053,
            'm': 0.0006e-6
        }
    }
}


# Класс параметров перехода
class TransformationParam:
    def __init__(self, raw_sk: str, trans_sk: str):
        try:
            self.param = TransformationParams[raw_sk][trans_sk]
            self._name = raw_sk + '-' + trans_sk
        except KeyError:
            try:
                self.param = TransformationParams[trans_sk][raw_sk]
                self._name = trans_sk + '-' + raw_sk
            except KeyError:
                print('Данный переход не предусмотрен скриптом.')
                quit()

        self._delta_x = self.param['delta_x']
        self._delta_y = self.param['delta_y']
        self._delta_z = self.param['delta_z']
        self._omega_x = self.param['omega_x']
        self._omega_y = self.param['omega_y']
        self._omega_z = self.param['omega_z']
        self._m = self.param['m']

    @property
    def name(self):
        return self._name

    @property
    def delta_x(self):
        return self._delta_x

    @property
    def delta_y(self):
        return self._delta_y

    @property
    def delta_z(self):
        return self._delta_z

    @property
    def omega_x(self):
        return self._omega_x

    @property
    def omega_y(self):
        return self._omega_y

    @property
    def omega_z(self):
        return self._omega_z

    @property
    def m(self):
        return self._m


# Класс параметров эллипсоида
class Ellipsoid:
    def __init__(self, ellipsoid: str):
        if ellipsoid not in Ellipsoids:
            raise EllipsoidNotFoundException(ellipsoid)

        self._name = ellipsoid

        self._a = Ellipsoids[ellipsoid]['a']
        self._f = Ellipsoids[ellipsoid]['f']

        self._b = self._a * (1 - self._f)

        self._e = math.sqrt(1 - (self._b ** 2) / (self._a ** 2))
        self._e_sqr = self._e ** 2  # f * (2 - f)

        self._e2 = math.sqrt((self._a ** 2 - self._b ** 2) / (self._b ** 2))

        self._e2_sqr = self._e2 ** 2

        self._alpha = 1 / self._f

    @property
    def name(self):
        return self._name

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def alpha(self):
        return self._alpha

    @property
    def f(self):
        return self._f

    @property
    def e(self):
        return self._e

    @property
    def e_sqr(self):
        return self._e_sqr

    @property
    def e2(self):
        return self._e2

    @property
    def e2_sqr(self):
        return self._e2_sqr


class EllipsoidNotFoundException(Exception):
    def __init__(self, ellipsoid):
        self.ellipsoid = ellipsoid

    def __str__(self):
        return 'Ellipsoid {} not found' % self.ellipsoid


# Трансформирование координат
class Transformation:
    def __init__(self, xyz: list):
        """
        Класс преобразование пространственных прямоугольных координат на основании ГОСТ Р 51794-2008
        :param xyz: координаты [x: float, y: float, z: float]
        """
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]



    def transformCoord(self, raw_sk: str, trans_sk: str) -> list:
        """
        Переход мужду СК
        :param raw_sk: исходная СК
        :param trans_sk: получаемая СК
        :return: координаты в нужной СК [x, y, z]
        """
        trans_params = TransformationParam(raw_sk, trans_sk)
        omega_x = math.radians(trans_params.omega_x / 3600)
        omega_y = math.radians(trans_params.omega_y / 3600)
        omega_z = math.radians(trans_params.omega_z / 3600)
        # Условие прямого / обратного перехода
        # Если True значит используется форула прямого перехода
        # Если False - обратного
        rule = raw_sk + '-' + trans_sk
        checker = rule == trans_params.name

        # Элементы матрицы доворота
        a11 = math.cos(omega_z) * math.cos(omega_y) - (math.sin(omega_z) * math.sin(omega_x) * math.sin(omega_y))
        a12 = math.sin(omega_z) * math.cos(omega_y) + (math.cos(omega_z) * math.sin(omega_x) * math.sin(omega_y))
        a13 = (- math.cos(omega_x)) * math.sin(omega_y)
        a21 = (- math.sin(omega_z)) * math.cos(omega_x)
        a22 = math.cos(omega_z) * math.cos(omega_x)
        a23 = math.sin(omega_x)
        a31 = math.cos(omega_z) * math.sin(omega_y) + (math.sin(omega_z) * math.sin(omega_x) * math.cos(omega_y))
        a32 = math.sin(omega_z) * math.sin(omega_y) - (math.cos(omega_z) * math.sin(omega_x) * math.cos(omega_y))
        a33 = math.cos(omega_x) * math.cos(omega_y)

        # Элементы транспонированной матрицы доворота
        alt_a11 = a11
        alt_a12 = a21
        alt_a13 = a31
        alt_a21 = a12
        alt_a22 = a22
        alt_a23 = a32
        alt_a31 = a13
        alt_a32 = a23
        alt_a33 = a33

        # Проверка правила перехода
        if checker:
            trans_x = (1 + trans_params.m) * (a11 * x + a12 * y + a13 * z) + trans_params.delta_x
            trans_y = (1 + trans_params.m) * (a21 * x + a22 * y + a23 * z) + trans_params.delta_y
            trans_z = (1 + trans_params.m) * (a31 * x + a32 * y + a33 * z) + trans_params.delta_z

        else:
            trans_x = (1 - trans_params.m) * (alt_a11 * x + alt_a12 * y + alt_a13 * z) - trans_params.delta_x
            trans_y = (1 - trans_params.m) * (alt_a21 * x + alt_a22 * y + alt_a23 * z) - trans_params.delta_y
            trans_z = (1 - trans_params.m) * (alt_a31 * x + alt_a32 * y + alt_a33 * z) - trans_params.delta_z

        trans_coord = [trans_x, trans_y, trans_z]
        return trans_coord


    def toGeodeticCoord(self, ell_name: str, precision=10e-4) -> list:
        """
        Преобразование пространственных прямоугольных координат в геодезические
        :param ell_name: название эллипсоида: 'GSK2011', 'WGS84', 'SPHERE', 'PZ90', 'PZ90.02', 'PZ90.11', 'GRS80', 'ITRF2008', 'ITRF2014', 'ITRF2020', 'SK42', 'SK95', 'KRASOVSKIY', 'BESSEL1841'
        :param precision: 10e-4 - допуск прекращения итераций. Согласно ГОСТ Р 51794-2008: 'При преобразованиях координат в качестве допуска прекращения итеративного
                                                                            процесса принимают значение (10^-4). В этом случае погрешность вычисления
                                                                            геодезическом высоты не превышает 0,003 м.'
        :return: геодезические координаты [lat, lon, H]
        """
        ell = Ellipsoid(ell_name)
        a = ell.a
        e2 = ell.e_sqr
        D = math.sqrt(x ** 2 + y ** 2)
        if D == 0:
            lat = (math.pi * z) / 2 * abs(z)
            lon = 0
            height = z * math.sin(lat) - a * math.sqrt(1 - e2 * math.sin(lat) ** 2)
        else:
            lon_a = abs(math.asin(y / D))
            if self.y < 0 < self.x:
                lon = 2 * math.pi - lon_a
            elif self.y < 0 > self.x:
                lon = math.pi + lon_a
            elif self.y > 0 > self.x:
                lon = math.pi - lon_a
            elif self.y > 0 < self.x:
                lon = lon_a
            elif self.y == 0 > self.x:
                lon = 0
            elif self.y == 0 < self.x:
                lon = math.pi

            if self.z == 0:
                lat = 0
                height = D - a
            else:
                # r, c, p - вспомогательные величины
                # s1, s2 - вспомогательные величины для реализации итеративного процесса
                r = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
                c = math.asin(self.z / r)
                p = (e2 * a) / (2 * r)
                rule = True
                s1 = 0
                lat_i = 0
                while rule:
                    b_i = c + s1
                    s2 = math.asin((p * math.sin(2 * lat_i)) / (math.sqrt(1 - e2 * (math.sin(lat_i) ** 2))))

                    d = abs(s2 - s1)

                    if d >= precision:
                        s1 = s2
                    else:
                        rule = False

                lat = lat_i

                height = D * math.cos(lat) + z * math.sin(lat) - a * math.sqrt(1 - e2 * (math.sin(lat) ** 2))

        g_coord = [math.degrees(lat), math.degrees(lon), height]
        return g_coord
