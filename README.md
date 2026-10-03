# frambuesa-pcb

placa de desarrollo abierta basada en el microcontrolador **RP2040** de Raspberry Pi,
diseñada en [KiCad](https://www.kicad.org/) para fabricarse y ensamblarse en
[JLCPCB](https://jlcpcb.com/).

este repositorio se usa para trabajo colaborativo y también como material de
enseñanza: la idea es que cualquier persona pueda clonarlo, abrirlo, entender cómo
está hecho y modificarlo.

## contenidos

- [estado del proyecto](#estado-del-proyecto)
- [características de la placa](#características-de-la-placa)
- [estructura del repositorio](#estructura-del-repositorio)
- [requisitos](#requisitos)
- [cómo abrir el proyecto](#cómo-abrir-el-proyecto)
- [biblioteca local de KiCad](#biblioteca-local-de-kicad)
- [cómo trabajar en conjunto](#cómo-trabajar-en-conjunto)
- [pendientes conocidos](#pendientes-conocidos)
- [glosario](#glosario)
- [recursos para aprender](#recursos-para-aprender)
- [licencia](#licencia)

## estado del proyecto

**revisión A, en diseño.** el esquemático está avanzado y la placa tiene los
componentes ubicados, pero todavía no tiene pistas ruteadas. no está lista para
fabricar.

| revisión | carpeta | estado |
| --- | --- | --- |
| A | [`frambuesa-rev-a/`](frambuesa-rev-a/) | en diseño |

## características de la placa

| bloque | componente | notas |
| --- | --- | --- |
| microcontrolador | RP2040 (U1), LQFN-56 7×7 mm | doble núcleo ARM Cortex-M0+, hasta 133 MHz |
| memoria flash | W25Q128JVS (U3), SOIC-8 | 128 Mbit (16 MB), conectada por QSPI |
| reloj | cristal Y1 + condensadores de 15 pF (C16, C17) | señales `XIN` / `XOUT` |
| USB | conector USB-C 16 pines (J5) | USB 2.0; resistencias de 5,1 kΩ en CC1/CC2 (R6, R7) para que el cable entregue 5 V; resistencias en serie de 27,4 Ω en `USB_D+`/`USB_D-` (R1, R2) |
| alimentación | regulador lineal AMS1117 (U2) | de `VBUS` (5 V del USB) a `+3V3`; el RP2040 genera internamente `+1V1` para su núcleo |
| botón | SW1 (PTS636) | botón de arranque (BOOTSEL), en la línea `QSPI_SS` |
| pines | J3 y J4, conectores hembra de 2,54 mm | exponen `GPIO00`–`GPIO29` (`GPIO26`–`GPIO29` también son entradas analógicas `ADC0`–`ADC3`), más `RUN`, `SWCLK` y `SWD` para depuración |
| fijación | H1–H4 | agujeros para tornillos M3 |
| placa | 50 × 60 mm, 2 capas de cobre (`F.Cu`, `B.Cu`) | |

el diseño sigue de cerca la guía oficial
[Hardware design with RP2040](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf),
que es la mejor referencia para entender por qué cada componente está ahí.

## estructura del repositorio

```text
frambuesa-pcb/
├── README.md                     este archivo
├── LICENSE                       licencia MIT
├── .gitignore                    ignora archivos temporales y de respaldo de KiCad
└── frambuesa-rev-a/              una carpeta por revisión de la placa
    ├── frambuesa-rev-a.kicad_pro proyecto de KiCad (abrir este)
    ├── frambuesa-rev-a.kicad_sch esquemático
    ├── frambuesa-rev-a.kicad_pcb diseño de la placa (PCB)
    ├── bom.csv                   lista de partes de JLCPCB, escrita a mano
    ├── sym-lib-table             registra la biblioteca local de símbolos
    ├── fp-lib-table              registra la biblioteca local de huellas
    └── bibliotecas/              biblioteca local generada desde bom.csv
        ├── frambuesa-rev-a.kicad_sym   símbolos
        ├── frambuesa-rev-a.pretty/     huellas (footprints)
        └── frambuesa-rev-a.3dshapes/   modelos 3D (.step y .wrl)
```

cada revisión vive en su propia carpeta para poder comparar versiones y no perder
el diseño de una placa ya fabricada.

## requisitos

- **KiCad 10** o superior. los archivos se guardaron con KiCad 10.0 y no se
  pueden abrir en versiones anteriores.
- **git**, para clonar y colaborar.
- opcional, solo para regenerar la biblioteca local: **Python 3** y el
  repositorio [partes-jlcpcb](https://github.com/piruetasxyz/partes-jlcpcb).

## cómo abrir el proyecto

```bash
git clone https://github.com/piruetasxyz/frambuesa-pcb.git
cd frambuesa-pcb
```

luego, en KiCad: **Archivo → Abrir proyecto** y elegir
`frambuesa-rev-a/frambuesa-rev-a.kicad_pro`. desde ahí se abren el esquemático y
la placa.

no hace falta configurar nada más: los archivos `sym-lib-table` y `fp-lib-table`
del proyecto ya apuntan a la biblioteca local usando `${KIPRJMOD}`, que KiCad
reemplaza por la carpeta del proyecto. por eso funciona en cualquier computador,
sin importar dónde se clone el repositorio.

## biblioteca local de KiCad

las partes que usamos de JLCPCB se listan en `bom.csv` dentro de cada revisión
(por ejemplo `frambuesa-rev-a/bom.csv`). tiene las mismas columnas que el
inventario de [partes-jlcpcb](https://github.com/piruetasxyz/partes-jlcpcb):

| columna | significado |
| --- | --- |
| `Category` | tipo de componente |
| `Value` | valor (ej. `10kΩ`, `100nF`) o número de parte |
| `Footprint` | encapsulado (ej. `0402`, `SOIC-8`) |
| `JLCPCB Part #` | código LCSC, empieza con `C` (ej. `C25744`) |
| `Description` | descripción de JLCPCB |
| `Qty (fecha)` | cantidad en nuestro inventario en esa fecha; vacía si no la tenemos |

a partir de ese archivo se genera la biblioteca local (símbolos, huellas y
modelos 3D):

```bash
cd frambuesa-rev-a
python3 /ruta/a/partes-jlcpcb/generar_biblioteca.py --bom bom.csv --output bibliotecas/frambuesa-rev-a
```

ajusta `/ruta/a/partes-jlcpcb` a donde tengas clonado ese repositorio. requiere
su entorno virtual activado (ver su README).

### agregar una parte nueva

1. buscar la parte en [jlcpcb.com/parts](https://jlcpcb.com/parts) y anotar su
   código LCSC (`C…`). preferir partes **básicas** (*basic*) antes que
   **extendidas** (*extended*): las extendidas cobran un recargo de montaje por
   cada tipo de parte.
2. agregar una fila a `bom.csv`.
3. regenerar la biblioteca con el comando de arriba.
4. en el esquemático, usar el símbolo de la biblioteca `frambuesa-rev-a` o
   asignar la huella nueva al símbolo existente, y llenar su campo `LCSC` con el
   código de la parte.
5. hacer commit de `bom.csv` **y** de los archivos nuevos en `bibliotecas/`
   juntos, para que la otra persona no abra el proyecto con huellas faltantes.

## cómo trabajar en conjunto

los archivos de KiCad son texto, así que git los guarda bien, pero **no se
pueden fusionar (merge) de forma confiable**: si dos personas editan el mismo
`.kicad_sch` o `.kicad_pcb` a la vez, el conflicto casi siempre hay que
resolverlo a mano rehaciendo uno de los cambios. para evitarlo:

1. **avisar antes de editar.** decir quién está trabajando en el esquemático o
   en la placa, y no editar el mismo archivo al mismo tiempo.
2. **traer cambios antes de abrir KiCad:** `git pull`.
3. **cerrar KiCad antes de hacer commit**, para que todo esté guardado.
4. **commits pequeños y con mensajes claros**, en español y en minúsculas,
   describiendo el cambio (ej. `agregar cristal, mounting holes`).
5. **subir los cambios pronto:** `git push`, para que la otra persona los tenga.
6. para cambios grandes o experimentales, usar una rama y un pull request.

el `.gitignore` ya ignora lo que KiCad genera localmente y no debe subirse:
respaldos (`*-backups`), archivos de bloqueo (`~*.lck`), cachés,
`*.kicad_prl` (preferencias de ventana de cada persona) y archivos exportados
(`*.csv`, `*.xml`, `*.net`). la excepción es `bom.csv`, que sí se sube porque
lo escribimos a mano.

si KiCad dice que un archivo está bloqueado por otro usuario, probablemente
quedó un `~*.lck` de una sesión que se cerró mal; se puede borrar con KiCad
cerrado.

### antes de dar por terminada una revisión

- [ ] el esquemático pasa el **ERC** (Inspeccionar → Verificador de reglas
      eléctricas) sin errores.
- [ ] la placa pasa el **DRC** (Inspeccionar → Verificador de reglas de diseño)
      sin errores, usando las reglas de fabricación de JLCPCB.
- [ ] todos los componentes a ensamblar tienen código LCSC y huella que
      coincide con esa parte.
- [ ] la placa coincide con el esquemático (Herramientas → Actualizar PCB desde
      el esquemático, sin cambios pendientes).
- [ ] revisado en el visor 3D.

## pendientes conocidos

revisión A, a la fecha de este documento:

- la placa no tiene pistas ruteadas todavía (sí tiene una zona de cobre).
- el símbolo de U2 en el esquemático es `AMS1117-5.0` con huella SOT-223, pero
  `bom.csv` y su código LCSC (`C880752`) corresponden a un `AMS1117-3.3` en
  SOT-89-3. hay que alinearlos: la placa necesita **3,3 V**.
- R3 tiene el código LCSC `C11702` (resistencia 0402) pero huella 0805.
- R1, R2 (27,4 Ω), C16, C17 (15 pF) y Y1 (cristal) no tienen huella ni código
  LCSC asignado.
- J3 y J4 usan el símbolo de 2×18 pines pero la huella de 1×20 pines.
- varios condensadores 0805 (C1–C11) aún no tienen código LCSC en el
  esquemático, aunque sus partes ya están en `bom.csv`.

## glosario

| término | significado |
| --- | --- |
| **esquemático** | el dibujo de qué está conectado con qué, sin importar la posición física |
| **PCB** | *printed circuit board*, placa de circuito impreso; también el archivo con el diseño físico |
| **huella** (*footprint*) | la forma de cobre en la placa donde se suelda un componente |
| **símbolo** | cómo se dibuja un componente en el esquemático |
| **net** | una conexión eléctrica: todos los pines unidos por un mismo cable lógico |
| **pista** (*track*) | línea de cobre que conecta pines en la placa |
| **ERC / DRC** | verificaciones automáticas de reglas eléctricas / de diseño |
| **BOM** | *bill of materials*, lista de materiales |
| **LCSC** | distribuidor asociado a JLCPCB; sus códigos `C…` identifican cada parte |
| **SMD** | componente de montaje superficial (sin patitas que atraviesan la placa) |
| **0402, 0805, 1206** | tamaños estándar de componentes SMD en pulgadas (0805 = 0,08 × 0,05 in) |
| **QSPI** | bus de 4 líneas de datos con el que el RP2040 lee su memoria flash |
| **SWD** | *serial wire debug*, interfaz para programar y depurar el microcontrolador |
| **BOOTSEL** | modo en que el RP2040 aparece como unidad USB para cargarle programas |
| **LDO** | regulador lineal de baja caída; aquí baja 5 V a 3,3 V |

## recursos para aprender

- [documentación de KiCad](https://docs.kicad.org/) (disponible en español).
- [Hardware design with RP2040](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf):
  guía oficial con un diseño mínimo de referencia, muy parecido a esta placa.
- [hoja de datos del RP2040](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf).
- [capacidades de fabricación de JLCPCB](https://jlcpcb.com/capabilities/pcb-capabilities):
  tamaños mínimos de pista, separación y perforaciones para configurar el DRC.

## licencia

[MIT](LICENSE), © 2026 piruetas.
