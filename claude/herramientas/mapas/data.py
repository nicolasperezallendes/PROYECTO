import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
_base = {e['n']: e for e in json.load(open(os.path.join(HERE, 'base.json')))}

# Delegaciones en el orden pedido. Subsectores según PLADECO 2024-2028 (Tabla 20).
DELEG = [
    dict(key='TB', nombre='Tierras Blancas', color='#007C99',
         sub='Tierras Blancas, Villa Potrerillos, San Ramón, Bosque San Carlos y Huachalalume, más Peñuelas Alto'),
    dict(key='RU', nombre='Rural', color='#4C7A2A',
         sub='Rural Cordillera: Pan de Azúcar, Tambillos, El Peñón, Las Barrancas, Las Cardas y El Caiceo'),
    dict(key='TO', nombre='Tongoy', color='#2F4C8F',
         sub='Tongoy y El Tangue'),
    dict(key='GU', nombre='Guanaqueros', color='#8A4F9E',
         sub='Guanaqueros'),
    dict(key='PA', nombre='Parte Alta', color='#C77D00',
         sub='Parte Alta (sector Península)'),
]
DCOLOR = {d['key']: d['color'] for d in DELEG}
DNAME = {d['key']: d['nombre'] for d in DELEG}

# n = N° en la base; nombre y dirección con tildes corregidas; short = etiqueta en el mapa
SEL = [
    # Tierras Blancas (orden alfabético)
    dict(n=20, d='TB', nombre='Colegio María Educa', short='Colegio María Educa',
         dir='Fray Jorge 850, Bosque San Carlos'),
    dict(n=23, d='TB', nombre='Colegio Particular Calasanz', short='Colegio Calasanz',
         dir='Valdivia 951, Tierras Blancas'),
    dict(n=34, d='TB', nombre='Colegio Técnico Profesional Altue', short='CTP Altue',
         dir='Cabo Exequiel Aroca 1340, Tierras Blancas'),
    dict(n=35, d='TB', nombre='Escuela Diego de Almeyda', short='Escuela Diego de Almeyda',
         dir='Santiago 1244, Tierras Blancas'),
    dict(n=9, d='TB', nombre='Liceo Fernando Binvignat Marín', short='Liceo Fernando Binvignat',
         dir='Arauco 1050, Tierras Blancas'),
    dict(n=38, d='TB', nombre='Liceo Bicentenario de Excelencia Colegio Particular Miguel de Cervantes',
         short='Liceo Miguel de Cervantes', dir='Camino Callejón Las Parcelas 405, San Ramón'),
    # Peñuelas Alto, incorporado a Tierras Blancas a pedido (28.10.2026)
    dict(n=13, d='TB', nombre='Colegio Altazor', short='Colegio Altazor',
         dir='Regimiento Arica 700, Peñuelas Alto'),
    dict(n=25, d='TB', nombre='Colegio Particular Leonardo Da Vinci', short='Colegio Leonardo Da Vinci',
         dir='Juan Barrera Cortés 2050, El Agrado de Peñuelas'),
    dict(n=42, d='TB', nombre='Colegio del Alba', short='Colegio del Alba',
         dir='Micaela Godoy 275, El Agrado de Peñuelas'),
    # Rural
    dict(n=2, d='RU', nombre='Colegio Pablo Neruda', short='Colegio Pablo Neruda',
         dir='Ruta D-409 km 18, Camino Interior 9505, Pan de Azúcar'),
    # Tongoy
    dict(n=7, d='TO', nombre='Liceo Carmen Aurora Rodríguez Henríquez', short='Liceo Carmen Aurora Rodríguez',
         dir='Dolores Endeiza 185, Tongoy'),
    # Parte Alta
    dict(n=21, d='PA', nombre='Colegio Metodista de Coquimbo', short='Colegio Metodista',
         dir='San Martín 1598'),
    dict(n=29, d='PA', nombre='Colegio San Luis', short='Colegio San Luis',
         dir='Av. Bernardo Ossandón 350'),
    dict(n=33, d='PA', nombre='Colegio Santa Marta', short='Colegio Santa Marta',
         dir='Manuel Rodríguez 2110'),
]

DEP_CORTA = {
    'Pública (SLEP Puerto Cordillera)': 'Pública (SLEP Puerto Cordillera)',
    'Particular subvencionado': 'Particular subvencionado',
    'Particular pagado': 'Particular pagado',
}

_ord = [x['key'] for x in DELEG]
SEL.sort(key=lambda s: (_ord.index(s['d']), s['nombre'].lower()))
for i, s in enumerate(SEL, 1):
    b = _base[s['n']]
    s['id'] = i
    s['lat'], s['lon'] = b['lat'], b['lon']
    s['director'] = b['director']
    s['fono'] = b['fono']
    s['email'] = b['email']
    s['dep'] = DEP_CORTA.get(b['dep'], b['dep'])
    s['niveles'] = b['niveles']
    s['mat'] = b['mat']
    s['rbd'] = b['rbd']

# Referencias de localidad (OpenStreetMap / Nominatim)
GUANAQUEROS = (-30.1977, -71.4220)
TONGOY = (-30.2572, -71.4928)
PAN_DE_AZUCAR = (-30.0745, -71.2305)
