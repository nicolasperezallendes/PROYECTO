"""Datos limpios de los 43 establecimientos con enseñanza media (base 23.10.2026)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
_base = {e['n']: e for e in json.load(open(os.path.join(HERE, 'base.json')))}

# Sectores PLADECO 2024-2028 (Tabla 20). Peñuelas Alto se agrupa con Tierras Blancas,
# como en los mapas por delegación (indicación del 28.10.2026).
SECTORES = ['Península', 'San Juan', 'Punta Mira – El Sauce', 'La Herradura – Sindempart',
            'La Cantera – Peñuelas', 'Tierras Blancas y Peñuelas Alto', 'Rural Cordillera', 'Tongoy']

# n: (nombre limpio, dirección limpia, sector, etiqueta corta)
LIMPIO = {
    1: ('Colegio Cardenal José María Caro', 'Cardenal Caro 701, El Llano', 'Península', 'Colegio Cardenal Caro'),
    2: ('Colegio Pablo Neruda', 'Ruta D-409 km 18, Camino Interior 9505, Pan de Azúcar', 'Rural Cordillera', 'Colegio Pablo Neruda'),
    3: ('Colegio de Artes Claudio Arrau', 'Av. Videla 199', 'Península', 'Colegio de Artes Claudio Arrau'),
    4: ('Instituto de Administración y Comercio Estado de Israel', 'Manuel Jesús Rivera 320, San Juan', 'San Juan', 'IAC Estado de Israel'),
    5: ('Liceo de Ciencias y Humanidades San Josemaría Escrivá', 'Los Clarines 1871', 'Punta Mira – El Sauce', 'Liceo San Josemaría Escrivá'),
    6: ('Liceo Bicentenario de Excelencia Instituto Superior de Comercio de Coquimbo', 'Doctor Marín 367', 'Península', 'Instituto Superior de Comercio'),
    7: ('Liceo Carmen Aurora Rodríguez Henríquez', 'Dolores Endeiza 185, Tongoy', 'Tongoy', 'Liceo Carmen A. Rodríguez'),
    8: ('Liceo Diego Portales', 'Av. Francisco Varela Oriente 950', 'Península', 'Liceo Diego Portales'),
    9: ('Liceo Fernando Binvignat Marín', 'Arauco 1050, Tierras Blancas', 'Tierras Blancas y Peñuelas Alto', 'Liceo Fernando Binvignat'),
    10: ('Liceo Industrial José Tomás de Urmeneta', 'Ossandón 1000', 'Península', 'Liceo Industrial J. T. de Urmeneta'),
    11: ('Aula Hospitalaria de Coquimbo', 'Cirujano Videla s/n', 'Península', 'Aula Hospitalaria'),
    12: ('Colegio Alta Cordillera', 'Cardenal Carlos Oviedo 3380', 'La Cantera – Peñuelas', 'Colegio Alta Cordillera'),
    13: ('Colegio Altazor', 'Regimiento Arica 700, Peñuelas Alto', 'Tierras Blancas y Peñuelas Alto', 'Colegio Altazor'),
    14: ("Colegio Bernardo O'Higgins", 'Av. Matta 86', 'Península', "Colegio Bernardo O'Higgins"),
    15: ('Colegio Cristóbal Colón', 'Los Clarines 2201', 'Punta Mira – El Sauce', 'Colegio Cristóbal Colón'),
    16: ('Colegio Discovery', 'Pedro Lagos 721, El Llano', 'Península', 'Colegio Discovery'),
    17: ('Colegio Español', 'Av. Alessandri 303', 'Península', 'Colegio Español'),
    18: ('Colegio Francis School', 'Los Tulipanes 254', 'La Herradura – Sindempart', 'Colegio Francis School'),
    19: ('Colegio Manuel Montt', 'Los Espinos Sur 2715, El Sauce', 'Punta Mira – El Sauce', 'Colegio Manuel Montt'),
    20: ('Colegio María Educa', 'Fray Jorge 850, Bosque San Carlos', 'Tierras Blancas y Peñuelas Alto', 'Colegio María Educa'),
    21: ('Colegio Metodista de Coquimbo', 'San Martín 1598', 'Península', 'Colegio Metodista'),
    22: ('Colegio Particular Komvux Coquimbo', 'Av. Pdte. Arturo Alessandri 1859', 'Punta Mira – El Sauce', 'Colegio Komvux'),
    23: ('Colegio Particular Calasanz', 'Valdivia 951, Tierras Blancas', 'Tierras Blancas y Peñuelas Alto', 'Colegio Calasanz'),
    24: ('Colegio Particular Gabriela Mistral', 'Abtao 22', 'Península', 'Colegio Gabriela Mistral'),
    25: ('Colegio Particular Leonardo Da Vinci', 'Juan Barrera Cortés 2050, El Agrado de Peñuelas', 'Tierras Blancas y Peñuelas Alto', 'Colegio Leonardo Da Vinci'),
    26: ('Colegio Particular San Gabriel', 'Eleuterio Ramírez 440', 'Península', 'Colegio San Gabriel'),
    27: ('Colegio Rakiduam', 'Av. La Cantera 610', 'La Cantera – Peñuelas', 'Colegio Rakiduam'),
    28: ('Colegio San Lorenzo', 'Narciso Herrera 2575', 'La Cantera – Peñuelas', 'Colegio San Lorenzo'),
    29: ('Colegio San Luis', 'Av. Bernardo Ossandón 350', 'Península', 'Colegio San Luis'),
    30: ('Colegio Santa Familia', 'Eduardo Mallea 601', 'Punta Mira – El Sauce', 'Colegio Santa Familia'),
    31: ('Colegio Santa Helena College', 'Av. Videla 235', 'Península', 'Santa Helena College'),
    32: ('Colegio Santa María de Belén N° 162', 'Las Begonias 361-371, Sindempart', 'La Herradura – Sindempart', 'Colegio Santa María de Belén'),
    33: ('Colegio Santa Marta', 'Manuel Rodríguez 2110', 'Península', 'Colegio Santa Marta'),
    34: ('Colegio Técnico Profesional Altue', 'Cabo Exequiel Aroca 1340, Tierras Blancas', 'Tierras Blancas y Peñuelas Alto', 'CTP Altue'),
    35: ('Escuela Diego de Almeyda', 'Santiago 1244, Tierras Blancas', 'Tierras Blancas y Peñuelas Alto', 'Escuela Diego de Almeyda'),
    36: ('Escuela San Marino College', 'Los Huertos 1731', 'La Cantera – Peñuelas', 'San Marino College'),
    37: ("Kid's World School", 'Ignacio Carrera Pinto 955, El Llano', 'Península', "Kid's World School"),
    38: ('Liceo Bicentenario de Excelencia Colegio Particular Miguel de Cervantes', 'Camino Callejón Las Parcelas 405, San Ramón', 'Tierras Blancas y Peñuelas Alto', 'Liceo Miguel de Cervantes'),
    39: ('Amazing Grace English School Peñuelas', 'Av. El Rosario 3870, Rosario de Peñuelas', 'La Cantera – Peñuelas', 'Amazing Grace English School'),
    40: ('Colegio Conquistadores Coquimbo', 'Las Azucenas 690, Sindempart', 'La Herradura – Sindempart', 'Colegio Conquistadores'),
    41: ('Colegio Saint Mary School', 'Av. El Sauce 1049, Sindempart', 'La Herradura – Sindempart', 'Saint Mary School'),
    42: ('Colegio del Alba', 'Micaela Godoy 275, El Agrado de Peñuelas', 'Tierras Blancas y Peñuelas Alto', 'Colegio del Alba'),
    43: ('Colegio Los Carrera', 'Abtao 190', 'Península', 'Colegio Los Carrera'),
}

DEP_COLOR = {'Pública (SLEP Puerto Cordillera)': '#007C99',
             'Particular subvencionado': '#D98E00',
             'Particular pagado': '#8A4F9E'}
DEP_CORTA = {'Pública (SLEP Puerto Cordillera)': 'Pública SLEP Puerto Cordillera',
             'Particular subvencionado': 'Particular subvencionado',
             'Particular pagado': 'Particular pagado'}

def _fix_director(s):
    return s.replace('Perez-cueto', 'Pérez-Cueto')

def registros():
    out = []
    for n, b in _base.items():
        nombre, dir_, sector, short = LIMPIO[n]
        out.append(dict(n=n, nombre=nombre, dir=dir_, sector=sector, short=short,
                        dep=b['dep'], dep_corta=DEP_CORTA[b['dep']], color=DEP_COLOR[b['dep']],
                        director=_fix_director(b['director']), fono=b['fono'], email=b['email'],
                        niveles=b['niveles'], mat=b['mat'], lat=b['lat'], lon=b['lon'], obs=b['obs']))
    out.sort(key=lambda r: (SECTORES.index(r['sector']), r['nombre'].lower()))
    return out

def numerar(rs):
    for i, r in enumerate(rs, 1):
        r['id'] = i
    return rs
