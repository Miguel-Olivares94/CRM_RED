/**
 * CRM Forms Enhanced — Mejoras inteligentes de formularios
 * Incluye: RUT, regiones/comunas, teléfonos, slider probabilidad, Select2
 */

// ─── MAPA GLOBAL COMUNA → PROVINCIA (accesible desde onchange inline) ────────
window.CRM_COMUNAS_PROVINCIA = {
    "Arica":"Arica","Camarones":"Arica","Putre":"Parinacota","General Lagos":"Parinacota",
    "Iquique":"Iquique","Alto Hospicio":"Iquique","Pozo Almonte":"Tamarugal","Camiña":"Tamarugal",
    "Colchane":"Tamarugal","Huara":"Tamarugal","Pica":"Tamarugal",
    "Antofagasta":"Antofagasta","Mejillones":"Antofagasta","Sierra Gorda":"Antofagasta","Taltal":"Antofagasta",
    "Calama":"El Loa","Ollagüe":"El Loa","San Pedro de Atacama":"El Loa",
    "Tocopilla":"Tocopilla","María Elena":"Tocopilla",
    "Copiapó":"Copiapó","Caldera":"Copiapó","Tierra Amarilla":"Copiapó",
    "Chañaral":"Chañaral","Diego de Almagro":"Chañaral",
    "Vallenar":"Huasco","Alto del Carmen":"Huasco","Freirina":"Huasco","Huasco":"Huasco",
    "La Serena":"Elqui","Coquimbo":"Elqui","Andacollo":"Elqui","La Higuera":"Elqui","Paihuano":"Elqui","Vicuña":"Elqui",
    "Illapel":"Choapa","Canela":"Choapa","Los Vilos":"Choapa","Salamanca":"Choapa",
    "Ovalle":"Limarí","Combarbalá":"Limarí","Monte Patria":"Limarí","Punitaqui":"Limarí","Río Hurtado":"Limarí",
    "Valparaíso":"Valparaíso","Casablanca":"Valparaíso","Concón":"Valparaíso","Juan Fernández":"Valparaíso",
    "Puchuncaví":"Valparaíso","Quintero":"Valparaíso","Viña del Mar":"Valparaíso","Isla de Pascua":"Isla de Pascua",
    "Los Andes":"Los Andes","Calle Larga":"Los Andes","Rinconada":"Los Andes","San Esteban":"Los Andes",
    "La Ligua":"Petorca","Cabildo":"Petorca","Papudo":"Petorca","Petorca":"Petorca","Zapallar":"Petorca",
    "Quillota":"Quillota","Calera":"Quillota","Hijuelas":"Quillota","La Cruz":"Quillota","Nogales":"Quillota",
    "San Antonio":"San Antonio","Algarrobo":"San Antonio","Cartagena":"San Antonio",
    "El Quisco":"San Antonio","El Tabo":"San Antonio","Santo Domingo":"San Antonio",
    "San Felipe":"San Felipe de Aconcagua","Catemu":"San Felipe de Aconcagua","Llaillay":"San Felipe de Aconcagua",
    "Panquehue":"San Felipe de Aconcagua","Putaendo":"San Felipe de Aconcagua","Santa María":"San Felipe de Aconcagua",
    "Santiago":"Santiago","Cerrillos":"Santiago","Cerro Navia":"Santiago","Conchalí":"Santiago",
    "El Bosque":"Santiago","Estación Central":"Santiago","Huechuraba":"Santiago","Independencia":"Santiago",
    "La Cisterna":"Santiago","La Florida":"Santiago","La Granja":"Santiago","La Pintana":"Santiago",
    "La Reina":"Santiago","Las Condes":"Santiago","Lo Barnechea":"Santiago","Lo Espejo":"Santiago",
    "Lo Prado":"Santiago","Macul":"Santiago","Maipú":"Santiago","Ñuñoa":"Santiago",
    "Pedro Aguirre Cerda":"Santiago","Peñalolén":"Santiago","Providencia":"Santiago","Pudahuel":"Santiago",
    "Quilicura":"Santiago","Quinta Normal":"Santiago","Recoleta":"Santiago","Renca":"Santiago",
    "San Joaquín":"Santiago","San Miguel":"Santiago","San Ramón":"Santiago","Vitacura":"Santiago",
    "Puente Alto":"Cordillera","Pirque":"Cordillera","San José de Maipo":"Cordillera",
    "Colina":"Chacabuco","Lampa":"Chacabuco","Tiltil":"Chacabuco",
    "San Bernardo":"Maipo","Buin":"Maipo","Calera de Tango":"Maipo","Paine":"Maipo",
    "Melipilla":"Melipilla","Alhué":"Melipilla","Curacaví":"Melipilla","María Pinto":"Melipilla","San Pedro":"Melipilla",
    "Talagante":"Talagante","El Monte":"Talagante","Isla de Maipo":"Talagante","Padre Hurtado":"Talagante","Peñaflor":"Talagante",
    "Rancagua":"Cachapoal","Codegua":"Cachapoal","Coinco":"Cachapoal","Coltauco":"Cachapoal",
    "Doñihue":"Cachapoal","Graneros":"Cachapoal","Las Cabras":"Cachapoal","Machalí":"Cachapoal",
    "Malloa":"Cachapoal","Mostazal":"Cachapoal","Olivar":"Cachapoal","Peumo":"Cachapoal",
    "Pichidegua":"Cachapoal","Quinta de Tilcoco":"Cachapoal","Rengo":"Cachapoal","Requínoa":"Cachapoal","San Vicente":"Cachapoal",
    "Pichilemu":"Cardenal Caro","La Estrella":"Cardenal Caro","Litueche":"Cardenal Caro",
    "Marchihue":"Cardenal Caro","Navidad":"Cardenal Caro","Paredones":"Cardenal Caro",
    "San Fernando":"Colchagua","Chépica":"Colchagua","Chimbarongo":"Colchagua","Lolol":"Colchagua",
    "Nancagua":"Colchagua","Palmilla":"Colchagua","Peralillo":"Colchagua","Placilla":"Colchagua",
    "Pumanque":"Colchagua","Santa Cruz":"Colchagua",
    "Talca":"Talca","Constitución":"Talca","Curepto":"Talca","Empedrado":"Talca",
    "Maule":"Talca","Pelarco":"Talca","Pencahue":"Talca","Río Claro":"Talca","San Clemente":"Talca","San Rafael":"Talca",
    "Cauquenes":"Cauquenes","Chanco":"Cauquenes","Pelluhue":"Cauquenes",
    "Curicó":"Curicó","Hualañé":"Curicó","Licantén":"Curicó","Molina":"Curicó",
    "Rauco":"Curicó","Romeral":"Curicó","Sagrada Familia":"Curicó","Teno":"Curicó","Vichuquén":"Curicó",
    "Linares":"Linares","Colbún":"Linares","Longaví":"Linares","Parral":"Linares",
    "Retiro":"Linares","San Javier":"Linares","Villa Alegre":"Linares","Yerbas Buenas":"Linares",
    "Chillán":"Diguillín","Bulnes":"Diguillín","Chillán Viejo":"Diguillín","El Carmen":"Diguillín",
    "Pemuco":"Diguillín","Pinto":"Diguillín","Quillón":"Diguillín","San Ignacio":"Diguillín","Yungay":"Diguillín",
    "Ñiquén":"Itata","Coihueco":"Punilla","San Carlos":"Punilla","San Fabián":"Punilla","San Nicolás":"Punilla",
    "Concepción":"Concepción","Coronel":"Concepción","Chiguayante":"Concepción","Florida":"Concepción",
    "Hualpén":"Concepción","Hualqui":"Concepción","Lota":"Concepción","Penco":"Concepción",
    "San Pedro de la Paz":"Concepción","Santa Juana":"Concepción","Talcahuano":"Concepción","Tomé":"Concepción",
    "Los Ángeles":"Biobío","Antuco":"Biobío","Cabrero":"Biobío","Laja":"Biobío",
    "Mulchén":"Biobío","Nacimiento":"Biobío","Negrete":"Biobío","Quilaco":"Biobío",
    "Quilleco":"Biobío","San Rosendo":"Biobío","Santa Bárbara":"Biobío","Tucapel":"Biobío","Yumbel":"Biobío","Alto Biobío":"Biobío",
    "Arauco":"Arauco","Cañete":"Arauco","Contulmo":"Arauco","Curanilahue":"Arauco",
    "Lebu":"Arauco","Los Álamos":"Arauco","Tirúa":"Arauco",
    "Temuco":"Cautín","Carahue":"Cautín","Cunco":"Cautín","Curarrehue":"Cautín",
    "Freire":"Cautín","Galvarino":"Cautín","Gorbea":"Cautín","Lautaro":"Cautín",
    "Loncoche":"Cautín","Melipeuco":"Cautín","Nueva Imperial":"Cautín","Padre las Casas":"Cautín",
    "Perquenco":"Cautín","Pitrufquén":"Cautín","Pucón":"Cautín","Saavedra":"Cautín",
    "Teodoro Schmidt":"Cautín","Toltén":"Cautín","Vilcún":"Cautín","Villarrica":"Cautín","Cholchol":"Cautín",
    "Angol":"Malleco","Collipulli":"Malleco","Curacautín":"Malleco","Ercilla":"Malleco",
    "Lonquimay":"Malleco","Los Sauces":"Malleco","Lumaco":"Malleco","Purén":"Malleco",
    "Renaico":"Malleco","Traiguén":"Malleco","Victoria":"Malleco",
    "Valdivia":"Valdivia","Corral":"Valdivia","Futrono":"Valdivia","La Unión":"Valdivia",
    "Lago Ranco":"Valdivia","Lanco":"Valdivia","Los Lagos":"Valdivia","Máfil":"Valdivia",
    "Mariquina":"Valdivia","Paillaco":"Valdivia","Panguipulli":"Valdivia","Río Bueno":"Ranco",
    "Puerto Montt":"Llanquihue","Calbuco":"Llanquihue","Cochamó":"Llanquihue","Fresia":"Llanquihue",
    "Frutillar":"Llanquihue","Los Muermos":"Llanquihue","Llanquihue":"Llanquihue","Maullín":"Llanquihue","Puerto Varas":"Llanquihue",
    "Castro":"Chiloé","Ancud":"Chiloé","Chonchi":"Chiloé","Curaco de Vélez":"Chiloé",
    "Dalcahue":"Chiloé","Puqueldón":"Chiloé","Queilén":"Chiloé","Quellón":"Chiloé","Quemchi":"Chiloé","Quinchao":"Chiloé",
    "Osorno":"Osorno","Puerto Octay":"Osorno","Purranque":"Osorno","Puyehue":"Osorno",
    "Río Negro":"Osorno","San Juan de la Costa":"Osorno","San Pablo":"Osorno",
    "Chaitén":"Palena","Futaleufú":"Palena","Hualaihué":"Palena","Palena":"Palena",
    "Coihaique":"Coihaique","Lago Verde":"Coihaique",
    "Aysén":"Aysén","Cisnes":"Aysén","Guaitecas":"Aysén",
    "Cochrane":"Capitán Prat","Tortel":"Capitán Prat",
    "Chile Chico":"General Carrera","Río Ibáñez":"General Carrera",
    "Punta Arenas":"Magallanes","Laguna Blanca":"Magallanes","Río Verde":"Magallanes","San Gregorio":"Magallanes",
    "Cabo de Hornos":"Antártica Chilena","Antártica":"Antártica Chilena",
    "Porvenir":"Tierra del Fuego","Primavera":"Tierra del Fuego","Timaukel":"Tierra del Fuego",
    "Natales":"Última Esperanza","Torres del Paine":"Última Esperanza"
};

window.CRM_actualizarProvincia = function(comunaVal) {
    var pi = document.getElementById('id_provincia');
    if (!pi || !comunaVal) return;
    var prov = window.CRM_COMUNAS_PROVINCIA[comunaVal];
    if (prov) pi.value = prov;
};

document.addEventListener('DOMContentLoaded', function () {

    // ─── 1. RUT CHILENO ─────────────────────────────────────────────────────
    const rutInput = document.querySelector('input[name="rut"]');
    const dvInput  = document.querySelector('input[name="dv"]');

    function calcularDV(rut) {
        let suma = 0, multiplo = 2;
        for (let i = rut.toString().length - 1; i >= 0; i--) {
            suma += parseInt(rut.toString()[i]) * multiplo;
            multiplo = multiplo < 7 ? multiplo + 1 : 2;
        }
        const dv = 11 - (suma % 11);
        if (dv === 11) return '0';
        if (dv === 10) return 'K';
        return dv.toString();
    }

    function formatearRUT(valor) {
        let rut = valor.replace(/[^0-9kK]/g, '').toUpperCase();
        if (rut.length <= 1) return rut;
        const dv   = rut.slice(-1);
        let cuerpo = rut.slice(0, -1);
        // Agregar puntos: 12.345.678
        cuerpo = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return cuerpo + '-' + dv;
    }

    if (rutInput) {
        // Crear indicador visual de validación
        const wrapper = rutInput.parentElement;
        const badge = document.createElement('small');
        badge.id = 'rut-badge';
        badge.style.cssText = 'display:block;margin-top:4px;font-size:12px;font-weight:600;';
        wrapper.appendChild(badge);

        rutInput.addEventListener('input', function () {
            const raw = this.value.replace(/[^0-9kK]/g, '').toUpperCase();
            if (raw.length > 1) {
                this.value = formatearRUT(raw);
                const cuerpo = raw.slice(0, -1);
                const dvIngresado = raw.slice(-1).toUpperCase();
                const dvCalculado = calcularDV(cuerpo);

                if (dvIngresado === dvCalculado) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    badge.style.color = '#28a745';
                    badge.textContent = '✓ RUT válido';
                    if (dvInput) { dvInput.value = dvIngresado; }
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                    badge.style.color = '#dc3545';
                    badge.textContent = '✗ RUT inválido — DV correcto: ' + dvCalculado;
                }
            } else {
                this.classList.remove('is-valid', 'is-invalid');
                badge.textContent = '';
            }
        });

        // Formatear si ya tiene valor al cargar
        if (rutInput.value) {
            rutInput.dispatchEvent(new Event('input'));
        }
    }

    // ─── 2. COMUNAS SEGÚN REGIÓN ─────────────────────────────────────────────
    const regionSelect = document.querySelector('select[name="region"]');
    const comunaSelect = document.querySelector('select[name="comuna"]');
    const provinciaInput = document.querySelector('input[name="provincia"]');

    if (regionSelect && comunaSelect) {
        const comunaActual = comunaSelect.dataset.current || comunaSelect.value || '';

        const comunaHint = document.getElementById('comuna-hint');

        function setHint(mostrar) {
            if (comunaHint) comunaHint.style.display = mostrar ? '' : 'none';
        }

        function s2Disable(el, dis) {
            if (window.jQuery && $(el).data('select2')) {
                $(el).prop('disabled', dis).trigger('change');
            } else {
                el.disabled = dis;
            }
        }

        function cargarComunas(region) {
            comunaSelect.innerHTML = '<option value="">-- Selecciona Región primero --</option>';
            if (!region) {
                s2Disable(comunaSelect, true);
                setHint(true);
                if (provinciaInput) provinciaInput.value = '';
                return;
            }
            comunaSelect.innerHTML = '<option value="">Cargando comunas...</option>';
            setHint(false);
            fetch('/api/comunas/?region=' + encodeURIComponent(region))
                .then(r => r.json())
                .then(data => {
                    comunaSelect.innerHTML = '<option value="">-- Selecciona comuna --</option>';
                    data.comunas.forEach(c => {
                        const opt = document.createElement('option');
                        opt.value = c;
                        opt.textContent = c;
                        if (c === comunaActual) opt.selected = true;
                        comunaSelect.appendChild(opt);
                    });
                    // Habilitar y refrescar Select2 (re-lee opciones del select nativo)
                    s2Disable(comunaSelect, false);
                    if (comunaActual) actualizarProvincia(comunaActual);
                })
                .catch(() => {
                    comunaSelect.innerHTML = '<option value="">Error al cargar comunas</option>';
                    s2Disable(comunaSelect, false);
                });
        }

        // Escuchar cambios tanto nativos como jQuery/Select2
        if (window.jQuery) {
            $(regionSelect).on('change select2:select select2:unselect', function () {
                cargarComunas($(this).val() || this.value);
            });
            $(document).on('select2:select', 'select[name="comuna"]', function () {
                actualizarProvincia($(this).val());
            });
            $(comunaSelect).on('change', function () {
                if (this.value) actualizarProvincia(this.value);
            });
        } else {
            regionSelect.addEventListener('change', function () {
                cargarComunas(this.value);
            });
        }
        // Listener nativo directo (respaldo independiente de jQuery)
        comunaSelect.addEventListener('change', function () {
            if (this.value) actualizarProvincia(this.value);
        });

        // Cargar comunas al entrar si ya hay región seleccionada
        if (regionSelect.value) {
            cargarComunas(regionSelect.value);
        } else {
            comunaSelect.innerHTML = '<option value="">-- Selecciona Región primero --</option>';
            comunaSelect.disabled = true;
            setHint(true);
        }
    }

    // ─── 3. FORMATO TELÉFONO CHILENO ─────────────────────────────────────────
    function formatearTelefono(input) {
        // Solo dígitos, máximo 9 (norma chilena: 9 XXXX XXXX / 2 XXXX XXXX)
        let val = input.value.replace(/[^0-9]/g, '').slice(0, 9);

        if (val.length > 0) {
            // Formato: X XXXX XXXX
            val = val.replace(/^(\d{1})(\d{0,4})(\d{0,4})$/, function (_, a, b, c) {
                return [a, b, c].filter(Boolean).join(' ');
            });
        }

        // Validación visual: móvil debe empezar en 9, fijo en 2
        const digits = input.value.replace(/[^0-9]/g, '');
        const esMov = input.name === 'telefono_movil';
        const esFij = input.name === 'telefono_fijo';
        if (digits.length === 9) {
            const valido = (esMov && digits.startsWith('9')) ||
                           (esFij && (digits.startsWith('2') || digits.startsWith('3') ||
                                      digits.startsWith('4') || digits.startsWith('5') ||
                                      digits.startsWith('6') || digits.startsWith('7')));
            input.classList.toggle('is-valid',   valido);
            input.classList.toggle('is-invalid', !valido);
        } else {
            input.classList.remove('is-valid', 'is-invalid');
        }

        input.value = val;
    }

    document.querySelectorAll('input[name="telefono_movil"], input[name="telefono_fijo"]').forEach(input => {
        input.placeholder = input.name === 'telefono_movil' ? '9 XXXX XXXX' : '2 XXXX XXXX';
        input.addEventListener('input', () => formatearTelefono(input));
    });

    // ─── 4. SLIDER DE PROBABILIDAD ───────────────────────────────────────────
    const probInput = document.querySelector('input[name="probabilidad"]');
    if (probInput) {
        // Crear slider
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = 0;
        slider.max = 100;
        slider.step = 5;
        slider.value = probInput.value || 0;
        slider.style.cssText = 'width:100%;accent-color:#D63031;margin-bottom:6px;';

        const display = document.createElement('div');
        display.style.cssText = 'display:flex;justify-content:space-between;align-items:center;';

        const badge = document.createElement('span');
        badge.style.cssText = 'font-size:1.4rem;font-weight:700;color:#D63031;';
        badge.textContent = (probInput.value || 0) + '%';

        // Colores según probabilidad
        function colorProbabilidad(val) {
            if (val < 30) return '#dc3545';
            if (val < 60) return '#f0ad4e';
            if (val < 80) return '#5bc0de';
            return '#28a745';
        }

        // Sugerencias automáticas por etapa
        const etapaSelect = document.querySelector('select[name="etapa"]');
        const PROB_ETAPA = {
            'LEAD': 10, 'CONTACTO': 20, 'CALIFICADO': 35,
            'PROPUESTA': 50, 'NEGOCIACION': 70, 'CIERRE': 85,
            'GANADA': 100, 'PERDIDA': 0, 'DORMIDA': 5
        };

        function actualizarSlider(val) {
            const color = colorProbabilidad(parseInt(val));
            badge.textContent = val + '%';
            badge.style.color = color;
            slider.style.accentColor = color;
            probInput.value = val;
        }

        slider.addEventListener('input', () => actualizarSlider(slider.value));
        probInput.addEventListener('change', () => { slider.value = probInput.value; actualizarSlider(probInput.value); });

        if (etapaSelect) {
            etapaSelect.addEventListener('change', function () {
                const sugerida = PROB_ETAPA[this.value];
                if (sugerida !== undefined && probInput.value == '0') {
                    slider.value = sugerida;
                    actualizarSlider(sugerida);
                }
            });
        }

        // Labels debajo del slider
        const labels = document.createElement('div');
        labels.style.cssText = 'display:flex;justify-content:space-between;font-size:11px;color:#999;margin-top:2px;';
        labels.innerHTML = '<span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>';

        display.appendChild(badge);

        const wrapper = probInput.parentElement;
        probInput.style.display = 'none';
        wrapper.insertBefore(slider, probInput);
        wrapper.insertBefore(display, probInput);
        wrapper.appendChild(labels);

        actualizarSlider(probInput.value || 0);
    }

    // ─── 5. SELECT2 PARA DROPDOWNS LARGOS ────────────────────────────────────
    if (window.jQuery && $.fn.select2) {
        $('select').not('[data-no-select2]').select2({
            theme: 'bootstrap-5',
            language: {
                noResults: function () { return 'Sin resultados'; },
                searching: function () { return 'Buscando...'; }
            },
            width: '100%',
        });
    }

    // ─── 6. ATAJOS DE FECHA ──────────────────────────────────────────────────
    document.querySelectorAll('input[type="date"][name="fecha_cierre_estimada"], input[type="date"][name="proximo_contacto"]').forEach(input => {
        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;';

        const atajos = [
            { label: 'Hoy', days: 0 },
            { label: '+15d', days: 15 },
            { label: '+30d', days: 30 },
            { label: '+60d', days: 60 },
            { label: '+90d', days: 90 },
        ];

        atajos.forEach(({ label, days }) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = label;
            btn.style.cssText = 'font-size:11px;padding:2px 8px;border:1px solid #dee2e6;border-radius:12px;background:#f8f9fa;cursor:pointer;color:#555;';
            btn.addEventListener('mouseenter', () => btn.style.background = '#D63031', btn.style.color = '#fff');
            btn.addEventListener('mouseleave', () => { btn.style.background = '#f8f9fa'; btn.style.color = '#555'; });
            btn.addEventListener('click', () => {
                const d = new Date();
                d.setDate(d.getDate() + days);
                input.value = d.toISOString().split('T')[0];
            });
            wrapper.appendChild(btn);
        });

        input.parentElement.appendChild(wrapper);
    });

    // ─── 7. BOTONES RÁPIDOS DE DURACIÓN ──────────────────────────────────────
    const durInput = document.querySelector('input[name="duracion_minutos"]');
    if (durInput) {
        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;';
        [5, 10, 15, 20, 30, 45, 60].forEach(min => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = min + ' min';
            btn.style.cssText = 'font-size:11px;padding:2px 10px;border:1px solid #dee2e6;border-radius:12px;background:#f8f9fa;cursor:pointer;color:#555;';
            btn.addEventListener('click', () => { durInput.value = min; });
            wrapper.appendChild(btn);
        });
        durInput.parentElement.appendChild(wrapper);
    }

    // ─── 8. FEEDBACK VISUAL EN CAMPOS OBLIGATORIOS ───────────────────────────
    document.querySelectorAll('input[required], select[required], textarea[required]').forEach(el => {
        el.addEventListener('blur', function () {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    });

});
