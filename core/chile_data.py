"""Datos geográficos de Chile: regiones y comunas."""

REGIONES_COMUNAS = {
    "Arica y Parinacota": ["Arica", "Camarones", "Putre", "General Lagos"],
    "Tarapacá": ["Iquique", "Alto Hospicio", "Pozo Almonte", "Camiña", "Colchane", "Huara", "Pica"],
    "Antofagasta": ["Antofagasta", "Mejillones", "Sierra Gorda", "Taltal", "Calama", "Ollagüe", "San Pedro de Atacama", "Tocopilla", "María Elena"],
    "Atacama": ["Copiapó", "Caldera", "Tierra Amarilla", "Chañaral", "Diego de Almagro", "Vallenar", "Alto del Carmen", "Freirina", "Huasco"],
    "Coquimbo": ["La Serena", "Coquimbo", "Andacollo", "La Higuera", "Paihuano", "Vicuña", "Illapel", "Canela", "Los Vilos", "Salamanca", "Ovalle", "Combarbalá", "Monte Patria", "Punitaqui", "Río Hurtado"],
    "Valparaíso": ["Valparaíso", "Casablanca", "Concón", "Juan Fernández", "Puchuncaví", "Quintero", "Viña del Mar", "Isla de Pascua", "Los Andes", "Calle Larga", "Rinconada", "San Esteban", "La Ligua", "Cabildo", "Papudo", "Petorca", "Zapallar", "Quillota", "Calera", "Hijuelas", "La Cruz", "Nogales", "San Antonio", "Algarrobo", "Cartagena", "El Quisco", "El Tabo", "Santo Domingo", "San Felipe", "Catemu", "Llaillay", "Panquehue", "Putaendo", "Santa María"],
    "Metropolitana": ["Santiago", "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central", "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "Ñuñoa", "Pedro Aguirre Cerda", "Peñalolén", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Joaquín", "San Miguel", "San Ramón", "Vitacura", "Puente Alto", "Pirque", "San José de Maipo", "Colina", "Lampa", "Tiltil", "San Bernardo", "Buin", "Calera de Tango", "Paine", "Melipilla", "Alhué", "Curacaví", "María Pinto", "San Pedro", "Talagante", "El Monte", "Isla de Maipo", "Padre Hurtado", "Peñaflor"],
    "O'Higgins": ["Rancagua", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros", "Las Cabras", "Machalí", "Malloa", "Mostazal", "Olivar", "Peumo", "Pichidegua", "Quinta de Tilcoco", "Rengo", "Requínoa", "San Vicente", "Pichilemu", "La Estrella", "Litueche", "Marchihue", "Navidad", "Paredones", "San Fernando", "Chépica", "Chimbarongo", "Lolol", "Nancagua", "Palmilla", "Peralillo", "Placilla", "Pumanque", "Santa Cruz"],
    "Maule": ["Talca", "Constitución", "Curepto", "Empedrado", "Maule", "Pelarco", "Pencahue", "Río Claro", "San Clemente", "San Rafael", "Cauquenes", "Chanco", "Pelluhue", "Curicó", "Hualañé", "Licantén", "Molina", "Rauco", "Romeral", "Sagrada Familia", "Teno", "Vichuquén", "Linares", "Colbún", "Longaví", "Parral", "Retiro", "San Javier", "Villa Alegre", "Yerbas Buenas"],
    "Ñuble": ["Chillán", "Bulnes", "Chillán Viejo", "El Carmen", "Pemuco", "Pinto", "Quillón", "San Ignacio", "Yungay", "Coihueco", "Ñiquén", "San Carlos", "San Fabián", "San Nicolás"],
    "Biobío": ["Concepción", "Coronel", "Chiguayante", "Florida", "Hualpén", "Hualqui", "Lota", "Penco", "San Pedro de la Paz", "Santa Juana", "Talcahuano", "Tomé", "Los Ángeles", "Antuco", "Cabrero", "Laja", "Mulchén", "Nacimiento", "Negrete", "Quilaco", "Quilleco", "San Rosendo", "Santa Bárbara", "Tucapel", "Yumbel", "Alto Biobío", "Arauco", "Cañete", "Contulmo", "Curanilahue", "Lebu", "Los Álamos", "Tirúa"],
    "La Araucanía": ["Temuco", "Carahue", "Cunco", "Curarrehue", "Freire", "Galvarino", "Gorbea", "Lautaro", "Loncoche", "Melipeuco", "Nueva Imperial", "Padre las Casas", "Perquenco", "Pitrufquén", "Pucón", "Saavedra", "Teodoro Schmidt", "Toltén", "Vilcún", "Villarrica", "Cholchol", "Angol", "Collipulli", "Curacautín", "Ercilla", "Lonquimay", "Los Sauces", "Lumaco", "Purén", "Renaico", "Traiguén", "Victoria"],
    "Los Ríos": ["Valdivia", "Corral", "Futrono", "La Unión", "Lago Ranco", "Lanco", "Los Lagos", "Máfil", "Mariquina", "Paillaco", "Panguipulli", "Río Bueno"],
    "Los Lagos": ["Puerto Montt", "Calbuco", "Cochamó", "Fresia", "Frutillar", "Los Muermos", "Llanquihue", "Maullín", "Puerto Varas", "Castro", "Ancud", "Chonchi", "Curaco de Vélez", "Dalcahue", "Puqueldón", "Queilén", "Quellón", "Quemchi", "Quinchao", "Osorno", "Puerto Octay", "Purranque", "Puyehue", "Río Negro", "San Juan de la Costa", "San Pablo", "Chaitén", "Futaleufú", "Hualaihué", "Palena"],
    "Aysén": ["Coihaique", "Lago Verde", "Aysén", "Cisnes", "Guaitecas", "Cochrane", "O'Higgins", "Tortel", "Chile Chico", "Río Ibáñez"],
    "Magallanes": ["Punta Arenas", "Laguna Blanca", "Río Verde", "San Gregorio", "Cabo de Hornos", "Antártica", "Porvenir", "Primavera", "Timaukel", "Natales", "Torres del Paine"],
}

REGIONES = sorted(REGIONES_COMUNAS.keys())

REGIONES_CHOICES = [('', '-- Selecciona región --')] + [(r, r) for r in REGIONES]

# Mapa comuna → provincia (para auto-completar el campo Provincia)
COMUNAS_PROVINCIA = {
    # Arica y Parinacota
    "Arica": "Arica", "Camarones": "Arica",
    "Putre": "Parinacota", "General Lagos": "Parinacota",
    # Tarapacá
    "Iquique": "Iquique", "Alto Hospicio": "Iquique",
    "Pozo Almonte": "Tamarugal", "Camiña": "Tamarugal", "Colchane": "Tamarugal", "Huara": "Tamarugal", "Pica": "Tamarugal",
    # Antofagasta
    "Antofagasta": "Antofagasta", "Mejillones": "Antofagasta", "Sierra Gorda": "Antofagasta", "Taltal": "Antofagasta",
    "Calama": "El Loa", "Ollagüe": "El Loa", "San Pedro de Atacama": "El Loa",
    "Tocopilla": "Tocopilla", "María Elena": "Tocopilla",
    # Atacama
    "Copiapó": "Copiapó", "Caldera": "Copiapó", "Tierra Amarilla": "Copiapó",
    "Chañaral": "Chañaral", "Diego de Almagro": "Chañaral",
    "Vallenar": "Huasco", "Alto del Carmen": "Huasco", "Freirina": "Huasco", "Huasco": "Huasco",
    # Coquimbo
    "La Serena": "Elqui", "Coquimbo": "Elqui", "Andacollo": "Elqui", "La Higuera": "Elqui", "Paihuano": "Elqui", "Vicuña": "Elqui",
    "Illapel": "Choapa", "Canela": "Choapa", "Los Vilos": "Choapa", "Salamanca": "Choapa",
    "Ovalle": "Limarí", "Combarbalá": "Limarí", "Monte Patria": "Limarí", "Punitaqui": "Limarí", "Río Hurtado": "Limarí",
    # Valparaíso
    "Valparaíso": "Valparaíso", "Casablanca": "Valparaíso", "Concón": "Valparaíso", "Juan Fernández": "Valparaíso",
    "Puchuncaví": "Valparaíso", "Quintero": "Valparaíso", "Viña del Mar": "Valparaíso",
    "Isla de Pascua": "Isla de Pascua",
    "Los Andes": "Los Andes", "Calle Larga": "Los Andes", "Rinconada": "Los Andes", "San Esteban": "Los Andes",
    "La Ligua": "Petorca", "Cabildo": "Petorca", "Papudo": "Petorca", "Petorca": "Petorca", "Zapallar": "Petorca",
    "Quillota": "Quillota", "Calera": "Quillota", "Hijuelas": "Quillota", "La Cruz": "Quillota", "Nogales": "Quillota",
    "San Antonio": "San Antonio", "Algarrobo": "San Antonio", "Cartagena": "San Antonio",
    "El Quisco": "San Antonio", "El Tabo": "San Antonio", "Santo Domingo": "San Antonio",
    "San Felipe": "San Felipe de Aconcagua", "Catemu": "San Felipe de Aconcagua", "Llaillay": "San Felipe de Aconcagua",
    "Panquehue": "San Felipe de Aconcagua", "Putaendo": "San Felipe de Aconcagua", "Santa María": "San Felipe de Aconcagua",
    # Metropolitana
    "Santiago": "Santiago", "Cerrillos": "Santiago", "Cerro Navia": "Santiago", "Conchalí": "Santiago",
    "El Bosque": "Santiago", "Estación Central": "Santiago", "Huechuraba": "Santiago", "Independencia": "Santiago",
    "La Cisterna": "Santiago", "La Florida": "Santiago", "La Granja": "Santiago", "La Pintana": "Santiago",
    "La Reina": "Santiago", "Las Condes": "Santiago", "Lo Barnechea": "Santiago", "Lo Espejo": "Santiago",
    "Lo Prado": "Santiago", "Macul": "Santiago", "Maipú": "Santiago", "Ñuñoa": "Santiago",
    "Pedro Aguirre Cerda": "Santiago", "Peñalolén": "Santiago", "Providencia": "Santiago", "Pudahuel": "Santiago",
    "Quilicura": "Santiago", "Quinta Normal": "Santiago", "Recoleta": "Santiago", "Renca": "Santiago",
    "San Joaquín": "Santiago", "San Miguel": "Santiago", "San Ramón": "Santiago", "Vitacura": "Santiago",
    "Puente Alto": "Cordillera", "Pirque": "Cordillera", "San José de Maipo": "Cordillera",
    "Colina": "Chacabuco", "Lampa": "Chacabuco", "Tiltil": "Chacabuco",
    "San Bernardo": "Maipo", "Buin": "Maipo", "Calera de Tango": "Maipo", "Paine": "Maipo",
    "Melipilla": "Melipilla", "Alhué": "Melipilla", "Curacaví": "Melipilla", "María Pinto": "Melipilla", "San Pedro": "Melipilla",
    "Talagante": "Talagante", "El Monte": "Talagante", "Isla de Maipo": "Talagante", "Padre Hurtado": "Talagante", "Peñaflor": "Talagante",
    # O'Higgins
    "Rancagua": "Cachapoal", "Codegua": "Cachapoal", "Coinco": "Cachapoal", "Coltauco": "Cachapoal",
    "Doñihue": "Cachapoal", "Graneros": "Cachapoal", "Las Cabras": "Cachapoal", "Machalí": "Cachapoal",
    "Malloa": "Cachapoal", "Mostazal": "Cachapoal", "Olivar": "Cachapoal", "Peumo": "Cachapoal",
    "Pichidegua": "Cachapoal", "Quinta de Tilcoco": "Cachapoal", "Rengo": "Cachapoal", "Requínoa": "Cachapoal", "San Vicente": "Cachapoal",
    "Pichilemu": "Cardenal Caro", "La Estrella": "Cardenal Caro", "Litueche": "Cardenal Caro",
    "Marchihue": "Cardenal Caro", "Navidad": "Cardenal Caro", "Paredones": "Cardenal Caro",
    "San Fernando": "Colchagua", "Chépica": "Colchagua", "Chimbarongo": "Colchagua", "Lolol": "Colchagua",
    "Nancagua": "Colchagua", "Palmilla": "Colchagua", "Peralillo": "Colchagua", "Placilla": "Colchagua",
    "Pumanque": "Colchagua", "Santa Cruz": "Colchagua",
    # Maule
    "Talca": "Talca", "Constitución": "Talca", "Curepto": "Talca", "Empedrado": "Talca",
    "Maule": "Talca", "Pelarco": "Talca", "Pencahue": "Talca", "Río Claro": "Talca", "San Clemente": "Talca", "San Rafael": "Talca",
    "Cauquenes": "Cauquenes", "Chanco": "Cauquenes", "Pelluhue": "Cauquenes",
    "Curicó": "Curicó", "Hualañé": "Curicó", "Licantén": "Curicó", "Molina": "Curicó",
    "Rauco": "Curicó", "Romeral": "Curicó", "Sagrada Familia": "Curicó", "Teno": "Curicó", "Vichuquén": "Curicó",
    "Linares": "Linares", "Colbún": "Linares", "Longaví": "Linares", "Parral": "Linares",
    "Retiro": "Linares", "San Javier": "Linares", "Villa Alegre": "Linares", "Yerbas Buenas": "Linares",
    # Ñuble
    "Chillán": "Diguillín", "Bulnes": "Diguillín", "Chillán Viejo": "Diguillín", "El Carmen": "Diguillín",
    "Pemuco": "Diguillín", "Pinto": "Diguillín", "Quillón": "Diguillín", "San Ignacio": "Diguillín", "Yungay": "Diguillín",
    "Ñiquén": "Itata",
    "Coihueco": "Punilla", "San Carlos": "Punilla", "San Fabián": "Punilla", "San Nicolás": "Punilla",
    # Biobío
    "Concepción": "Concepción", "Coronel": "Concepción", "Chiguayante": "Concepción", "Florida": "Concepción",
    "Hualpén": "Concepción", "Hualqui": "Concepción", "Lota": "Concepción", "Penco": "Concepción",
    "San Pedro de la Paz": "Concepción", "Santa Juana": "Concepción", "Talcahuano": "Concepción", "Tomé": "Concepción",
    "Los Ángeles": "Biobío", "Antuco": "Biobío", "Cabrero": "Biobío", "Laja": "Biobío",
    "Mulchén": "Biobío", "Nacimiento": "Biobío", "Negrete": "Biobío", "Quilaco": "Biobío",
    "Quilleco": "Biobío", "San Rosendo": "Biobío", "Santa Bárbara": "Biobío", "Tucapel": "Biobío", "Yumbel": "Biobío", "Alto Biobío": "Biobío",
    "Arauco": "Arauco", "Cañete": "Arauco", "Contulmo": "Arauco", "Curanilahue": "Arauco",
    "Lebu": "Arauco", "Los Álamos": "Arauco", "Tirúa": "Arauco",
    # La Araucanía
    "Temuco": "Cautín", "Carahue": "Cautín", "Cunco": "Cautín", "Curarrehue": "Cautín",
    "Freire": "Cautín", "Galvarino": "Cautín", "Gorbea": "Cautín", "Lautaro": "Cautín",
    "Loncoche": "Cautín", "Melipeuco": "Cautín", "Nueva Imperial": "Cautín", "Padre las Casas": "Cautín",
    "Perquenco": "Cautín", "Pitrufquén": "Cautín", "Pucón": "Cautín", "Saavedra": "Cautín",
    "Teodoro Schmidt": "Cautín", "Toltén": "Cautín", "Vilcún": "Cautín", "Villarrica": "Cautín", "Cholchol": "Cautín",
    "Angol": "Malleco", "Collipulli": "Malleco", "Curacautín": "Malleco", "Ercilla": "Malleco",
    "Lonquimay": "Malleco", "Los Sauces": "Malleco", "Lumaco": "Malleco", "Purén": "Malleco",
    "Renaico": "Malleco", "Traiguén": "Malleco", "Victoria": "Malleco",
    # Los Ríos
    "Valdivia": "Valdivia", "Corral": "Valdivia", "Futrono": "Valdivia", "La Unión": "Valdivia",
    "Lago Ranco": "Valdivia", "Lanco": "Valdivia", "Los Lagos": "Valdivia", "Máfil": "Valdivia",
    "Mariquina": "Valdivia", "Paillaco": "Valdivia", "Panguipulli": "Valdivia",
    "Río Bueno": "Ranco",
    # Los Lagos
    "Puerto Montt": "Llanquihue", "Calbuco": "Llanquihue", "Cochamó": "Llanquihue", "Fresia": "Llanquihue",
    "Frutillar": "Llanquihue", "Los Muermos": "Llanquihue", "Llanquihue": "Llanquihue", "Maullín": "Llanquihue", "Puerto Varas": "Llanquihue",
    "Castro": "Chiloé", "Ancud": "Chiloé", "Chonchi": "Chiloé", "Curaco de Vélez": "Chiloé",
    "Dalcahue": "Chiloé", "Puqueldón": "Chiloé", "Queilén": "Chiloé", "Quellón": "Chiloé", "Quemchi": "Chiloé", "Quinchao": "Chiloé",
    "Osorno": "Osorno", "Puerto Octay": "Osorno", "Purranque": "Osorno", "Puyehue": "Osorno",
    "Río Negro": "Osorno", "San Juan de la Costa": "Osorno", "San Pablo": "Osorno",
    "Chaitén": "Palena", "Futaleufú": "Palena", "Hualaihué": "Palena", "Palena": "Palena",
    # Aysén
    "Coihaique": "Coihaique", "Lago Verde": "Coihaique",
    "Aysén": "Aysén", "Cisnes": "Aysén", "Guaitecas": "Aysén",
    "Cochrane": "Capitán Prat", "Tortel": "Capitán Prat",
    "Chile Chico": "General Carrera", "Río Ibáñez": "General Carrera",
    # Magallanes
    "Punta Arenas": "Magallanes", "Laguna Blanca": "Magallanes", "Río Verde": "Magallanes", "San Gregorio": "Magallanes",
    "Cabo de Hornos": "Antártica Chilena", "Antártica": "Antártica Chilena",
    "Porvenir": "Tierra del Fuego", "Primavera": "Tierra del Fuego", "Timaukel": "Tierra del Fuego",
    "Natales": "Última Esperanza", "Torres del Paine": "Última Esperanza",
}

SECTORES_CHOICES = [
    ('', '-- Selecciona sector --'),
    ('Retail / Comercio', 'Retail / Comercio'),
    ('Tecnología / TI', 'Tecnología / TI'),
    ('Salud / Clínica', 'Salud / Clínica'),
    ('Educación', 'Educación'),
    ('Finanzas / Banca', 'Finanzas / Banca'),
    ('Construcción / Inmobiliario', 'Construcción / Inmobiliario'),
    ('Transporte / Logística', 'Transporte / Logística'),
    ('Manufactura / Industria', 'Manufactura / Industria'),
    ('Servicios Profesionales', 'Servicios Profesionales'),
    ('Minería', 'Minería'),
    ('Agricultura / Agroindustria', 'Agricultura / Agroindustria'),
    ('Turismo / Hotelería', 'Turismo / Hotelería'),
    ('Energía', 'Energía'),
    ('Telecomunicaciones', 'Telecomunicaciones'),
    ('Entretenimiento / Medios', 'Entretenimiento / Medios'),
    ('Gobierno / Público', 'Gobierno / Público'),
    ('Seguros', 'Seguros'),
    ('Automotriz', 'Automotriz'),
    ('Farmacéutico', 'Farmacéutico'),
    ('Otro', 'Otro'),
]

TIPO_CLIENTE_CHOICES = [
    ('', '-- Selecciona tipo --'),
    ('Cliente Directo', 'Cliente Directo'),
    ('Canal / Revendedor', 'Canal / Revendedor'),
    ('Gobierno', 'Gobierno'),
    ('Corporativo', 'Corporativo'),
    ('PyME', 'PyME'),
    ('Startup', 'Startup'),
    ('ONG / Fundación', 'ONG / Fundación'),
]

SI_NO_CHOICES = [
    ('', '--'),
    ('SI', 'Sí'),
    ('NO', 'No'),
]

PRODUCTOS_CLARO_CHOICES = [
    ('Portabilidad', 'Portabilidad'),
    ('Línea Nueva', 'Línea Nueva'),
    ('M2M / IoT', 'M2M / IoT'),
    ('BAM / Internet Móvil', 'BAM / Internet Móvil'),
    ('Telefonía Fija', 'Telefonía Fija'),
    ('Internet Fijo', 'Internet Fijo'),
    ('Pack Fijo+Móvil', 'Pack Fijo+Móvil'),
    ('Cloud / Hosting', 'Cloud / Hosting'),
    ('Seguridad', 'Seguridad'),
    ('Centralita / PBX', 'Centralita / PBX'),
]
