import os
import sys
import subprocess
from pathlib import Path

def rebuild_all():
    """
    Script maestro de reconstrucción desde cero para la Release v1.0.
    """
    root_dir = Path(__file__).resolve().parent.parent
    os.chdir(root_dir)

    print("==========================================================================")
    print(" RECONSTRUCCIÓN COMPLETA Y VALIDACIÓN DESDE CERO (Release v1.0)")
    print("==========================================================================")

    # 1. Limpieza de resultados previos
    print("\n[Paso 1/3] Limpiando resultados previos...")
    clean_script = root_dir / "scripts" / "clean_results.py"
    res_clean = subprocess.run([sys.executable, str(clean_script)], capture_output=True, text=True)
    if res_clean.returncode != 0:
        print(f"ERROR al limpiar resultados: {res_clean.stderr}")
        sys.exit(1)
    print(res_clean.stdout.strip())

    # 2. Ejecución de la suite completa
    print("\n[Paso 2/3] Ejecutando suite de experimentos y auditorías (run_all_experiments.py)...")
    runner_script = root_dir / "run_all_experiments.py"
    res_run = subprocess.run([sys.executable, str(runner_script)], capture_output=True, text=True)
    print(res_run.stdout)
    if res_run.returncode != 0:
        print(f"ERROR durante la ejecución: {res_run.stderr}")
        sys.exit(1)

    # 3. Verificación de artefactos generados
    print("\n[Paso 3/3] Verificando integridad de artefactos exportados...")
    results_dir = root_dir / "results"
    required_files = [
        "final_table.csv",
        "kyber_transform_table.csv",
        "dsa_transform_table.csv",
        "summary_report.md"
    ]

    missing = []
    for req in required_files:
        fpath = results_dir / req
        if not fpath.exists() or fpath.stat().st_size == 0:
            missing.append(req)

    if missing:
        print(f"ERROR: Los siguientes artefactos requeridos no fueron generados correctamente: {missing}")
        sys.exit(1)

    print("SUCCESS: Todos los artefactos fueron verificados e inspeccionados correctamente.")
    print("==========================================================================")
    print(" RECONSTRUCCIÓN COMPLETA CONCLUIDA EXITOSAMENTE (Release v1.0 Listo)")
    print("==========================================================================")

if __name__ == '__main__':
    rebuild_all()
