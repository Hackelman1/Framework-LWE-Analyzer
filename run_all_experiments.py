import logging
import sys
from pathlib import Path
import pandas as pd
from transformations.dsa.audit_utils import apply_fdr_control
from src.experiments_lwe import run_lwe_suite          # Experimentos A a P (LWE - 16)
from transformations.kem.audit_kem import run_kem_suite # Experimentos T a W (ML-KEM - 4)
from transformations.dsa.audit_dsa import run_dsa_suite # Auditoría ML-DSA (FIPS 204 - 3)


def save_suite_table(results_list: list[dict], relative_csv_path: str):
    if not results_list:
        return
    out_path = Path(relative_csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    records = []
    for r in results_list:
        flat_r = {k: v for k, v in r.items() if not isinstance(v, (dict, list))}
        records.append(flat_r)
    
    df = pd.DataFrame(records)
    df.to_csv(out_path, index=False)
    logging.info(f"Tabla guardada en '{out_path}' ({len(records)} registros).")


def generate_summary_reports(adjusted_results: list[dict]):
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    summary_file = results_dir / "summary_report.md"
    lines = [
        "# Reporte Consolidado de Auditoría Estadística Global (BH-FDR, M=23)",
        "\n## Resultados Globales de Auditoría de Fuga (BH-FDR Ajustado)\n",
        "| ID Experimento | Suite | p-valor Empírico | FDR q-valor | Estado |",
        "|:---|:---:|:---:|:---:|:---:|"
    ]

    for r in adjusted_results:
        exp_id = r.get("experiment_id", "?")
        suite = r.get("suite", "?")
        p_val = r.get("empirical_p_value", 0.0)
        q_val = r.get("fdr_q_value", 0.0)
        status = r.get("status", "PASS")
        lines.append(f"| **{exp_id}** | `{suite}` | `{p_val:.6f}` | `{q_val:.6f}` | **{status}** |")

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logging.info(f"Reporte resumen generado en '{summary_file}'.")


def main():
    # 1. Logger para consola
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logging.info("Iniciando pipeline de ejecución global (23 Experimentos)...")
    
    global_results_pool = []
    
    # 2. Recolección y etiquetado explícito de procedencia
    lwe_results = run_lwe_suite()
    for r in lwe_results:
        r["suite"] = "lwe"
    global_results_pool.extend(lwe_results)
    
    kem_results = run_kem_suite()
    for r in kem_results:
        r["suite"] = "kem"
    global_results_pool.extend(kem_results)
    
    dsa_results = run_dsa_suite()
    for r in dsa_results:
        r["suite"] = "dsa"
    global_results_pool.extend(dsa_results)
    
    # 3. Sanity Check: Confirmar exactamente 23 experimentos
    assert len(global_results_pool) == 23, (
        f"Error de integridad: Se esperaban 23 experimentos, se obtuvieron {len(global_results_pool)}"
    )
    
    # 4. Chequeo de Esquema: Validar clave 'empirical_p_value'
    missing_keys = [
        r.get("experiment_id", f"idx_{i}") 
        for i, r in enumerate(global_results_pool) 
        if "empirical_p_value" not in r
    ]
    if missing_keys:
        raise ValueError(f"Error de esquema: Entradas sin 'empirical_p_value': {missing_keys}")

    # 5. Invocación Única de BH-FDR sobre el pool global de M=23
    adjusted_global_results = apply_fdr_control(
        global_results_pool, 
        alpha=0.05, 
        family_scope="leakage_global",
        p_value_key="empirical_p_value"
    )
    
    # 6. Persistencia filtrada por 'suite'
    save_suite_table([r for r in adjusted_global_results if r["suite"] == "lwe"], "results/final_table.csv")
    save_suite_table([r for r in adjusted_global_results if r["suite"] == "kem"], "results/kyber_transform_table.csv")
    save_suite_table([r for r in adjusted_global_results if r["suite"] == "dsa"], "results/dsa_transform_table.csv")
    
    generate_summary_reports(adjusted_global_results)
    logging.info("Pipeline completado exitosamente. Se aplicó BH-FDR sobre la familia de M=23 hipótesis.")

if __name__ == "__main__":
    main()
