import os
import shutil
from pathlib import Path

def clean_results():
    """
    Limpia todos los archivos dentro de la carpeta results/, manteniendo la carpeta lista.
    """
    root_dir = Path(__file__).resolve().parent.parent
    results_dir = root_dir / "results"
    
    if results_dir.exists():
        print(f"Limpiando directorio de resultados en: {results_dir}")
        for item in results_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    else:
        results_dir.mkdir(parents=True, exist_ok=True)
        
    print("SUCCESS: Directorio 'results/' limpiado exitosamente.")

if __name__ == '__main__':
    clean_results()
