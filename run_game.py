"""Script para executar o jogo Snake."""

import sys
import os

# Adicionar o diretório do projeto ao path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Verificar estrutura de pastas
expected_structure = {
    "src/main.py": "src/main.py",
    "src/configs/config.py": "src/configs/config.py",
    "src/utils/utils.py": "src/utils/utils.py",
    "src/handlers/managers.py": "src/handlers/managers.py",
    "src/interfaces/entities.py": "src/interfaces/entities.py",
}

missing_files = []
for file_path in expected_structure:
    full_path = os.path.join(project_dir, file_path)
    if not os.path.exists(full_path):
        missing_files.append(file_path)

if missing_files:
    print("Arquivos faltando:")
    for file in missing_files:
        print(f"  - {file}")
    print("\nEstrutura esperada:")
    print("├── src/")
    print("│   ├── main.py")
    print("│   ├── configs/")
    print("│   │   └── config.py")
    print("│   ├── utils/")
    print("│   │   └── utils.py")
    print("│   ├── handlers/")
    print("│   │   └── managers.py")
    print("│   └── interfaces/")
    print("│       └── entities.py")
    sys.exit(1)

# Importar e executar o jogo
try:
    from src.main import main

    main()
except ImportError as e:
    print(f"Erro de importação: {e}")
    print("Tentando execução direta...")
    try:
        # Adicionar diretório src ao path
        src_dir = os.path.join(project_dir, "src")
        sys.path.insert(0, src_dir)
        import main

        main.main()
    except Exception as e2:
        print(f"Erro na execução direta: {e2}")
        sys.exit(1)
except Exception as e:
    print(f"Erro ao executar o jogo: {e}")
    sys.exit(1)
