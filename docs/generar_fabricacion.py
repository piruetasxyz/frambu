#!/usr/bin/env python3
"""Genera los archivos para fabricar y ensamblar la placa en JLCPCB (PCB + PCBA),
con la misma estructura que tacto48:

    <REVISION>-fab/    gerbers, taladros (PTH y NPTH), gbrjob y <REVISION>-gerb.zip
    <REVISION>-pcba/   <REVISION>-bom.csv y <REVISION>-cpl.csv

En JLCPCB: subir el zip de -fab/ como "Gerber file" y, al activar "PCB Assembly",
subir el bom y el cpl de -pcba/.

Solo entran al ensamblado (bom y cpl) los componentes con el campo "LCSC" lleno
en el esquemático y que no estén marcados como DNP; el resto (por ejemplo los
conectores de 2,54 mm) se suelda a mano.

Uso: python3 docs/generar_fabricacion.py
Requiere kicad-cli (KiCad 10) en el PATH, o la variable de entorno KICAD_CLI
con el comando completo (igual que docs/generar_bom.py).
"""
import csv
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import OrderedDict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REVISION = "frambu-v-0-rev-a"
KICAD_PCB = f"{REVISION}/{REVISION}.kicad_pcb"
KICAD_SCH = f"{REVISION}/{REVISION}.kicad_sch"
FAB_DIR = f"{REVISION}-fab"
PCBA_DIR = f"{REVISION}-pcba"

# capas de una placa de 2 capas, las mismas que se mandaron para tacto48
CAPAS = "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts"


def kicad_cli():
    return shlex.split(os.environ.get("KICAD_CLI", "kicad-cli"))


def correr(*args):
    cmd = kicad_cli() + list(args)
    r = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        sys.exit(f"falló: {' '.join(cmd)}")


def generar_fab():
    fab = REPO_ROOT / FAB_DIR
    if fab.exists():
        shutil.rmtree(fab)
    fab.mkdir()
    # --no-protel-ext deja extensiones .gbr (como en tacto48);
    # --check-zones rellena las zonas antes de exportar
    correr("pcb", "export", "gerbers", "--layers", CAPAS, "--no-protel-ext",
           "--check-zones", "--output", f"{FAB_DIR}/", KICAD_PCB)
    correr("pcb", "export", "drill", "--format", "excellon", "--drill-origin", "absolute",
           "--excellon-units", "mm", "--excellon-zeros-format", "decimal",
           "--excellon-oval-format", "alternate", "--excellon-separate-th",
           "--output", f"{FAB_DIR}/", KICAD_PCB)
    archivos = sorted(p for p in fab.iterdir() if p.suffix in (".gbr", ".drl", ".gbrjob"))
    with zipfile.ZipFile(fab / f"{REVISION}-gerb.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in archivos:
            z.write(p, p.name)
    return archivos


def leer_esquematico(tmp):
    """Referencia -> (valor, huella, lcsc, dnp), según el esquemático."""
    salida = Path(tmp) / "bom.csv"
    correr("sch", "export", "bom", "--fields", "Reference,Value,Footprint,LCSC,${DNP}",
           "--labels", "Reference,Value,Footprint,LCSC,DNP", "--group-by", "",
           "--output", str(salida), KICAD_SCH)
    with open(salida, newline="", encoding="utf-8") as f:
        return {r["Reference"]: r for r in csv.DictReader(f)}


def leer_posiciones(tmp):
    salida = Path(tmp) / "pos.csv"
    correr("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
           "--output", str(salida), KICAD_PCB)
    with open(salida, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generar_pcba():
    pcba = REPO_ROOT / PCBA_DIR
    pcba.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp:
        partes = leer_esquematico(tmp)
        posiciones = leer_posiciones(tmp)

    ensamblar = {ref for ref, p in partes.items() if p["LCSC"].strip() and not p["DNP"].strip()}
    sin_lcsc = sorted(ref for ref in partes if ref not in ensamblar)

    cpl = []
    en_placa = set()
    for p in posiciones:
        ref = p["Ref"]
        if ref not in ensamblar:
            continue
        en_placa.add(ref)
        lado = "Top" if p["Side"].lower() == "top" else "Bottom"
        cpl.append([ref, f"{float(p['PosX']):.6f}", f"{float(p['PosY']):.6f}", lado,
                    f"{float(p['Rot']):.6f}"])
    faltan = sorted(ensamblar - en_placa)
    if faltan:
        sys.exit(f"están en el esquemático pero no en la placa: {', '.join(faltan)}")

    grupos = OrderedDict()
    for ref in sorted(ensamblar, key=orden_ref):
        p = partes[ref]
        grupos.setdefault((p["Value"], p["Footprint"], p["LCSC"].strip()), []).append(ref)

    with open(pcba / f"{REVISION}-bom.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (valor, huella, lcsc), refs in grupos.items():
            w.writerow([valor, ",".join(refs), huella, lcsc])

    with open(pcba / f"{REVISION}-cpl.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writerows(sorted(cpl, key=lambda r: orden_ref(r[0])))

    return len(grupos), len(cpl), sin_lcsc


def orden_ref(ref):
    letras = ref.rstrip("0123456789")
    numero = ref[len(letras):]
    return (letras, int(numero) if numero else 0)


def main():
    archivos = generar_fab()
    lineas, piezas, sin_lcsc = generar_pcba()
    print(f"{FAB_DIR}/: {len(archivos)} archivos + {REVISION}-gerb.zip")
    print(f"{PCBA_DIR}/: bom con {lineas} líneas, cpl con {piezas} piezas")
    if sin_lcsc:
        print(f"sin ensamblar (sin LCSC o DNP): {', '.join(sin_lcsc)}")


if __name__ == "__main__":
    main()
