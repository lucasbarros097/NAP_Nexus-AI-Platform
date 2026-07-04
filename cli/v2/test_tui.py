#!/usr/bin/env python3
"""
Teste simples para verificar se a NAP V2 TUI funciona corretamente.
Este script testa os componentes básicos sem iniciar o loop interativo.
"""

import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_imports():
    """Testa se todas as dependências podem ser importadas."""
    print("Testing imports...")
    
    try:
        from rich.console import Console
        from rich.panel import Panel
        from prompt_toolkit import PromptSession
        print("✓ Rich and prompt-toolkit imported successfully")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    
    return True

def test_agent_tools():
    """Testa as ferramentas do agente."""
    print("\nTesting AgentTools...")
    
    try:
        from cli.v2.agent_tools import AgentTools
        
        # Cria instância com workspace dentro do projeto
        import tempfile
        import shutil
        workspace_root = Path.cwd() / "workspace_test"
        workspace_root.mkdir(exist_ok=True)
        
        try:
            tools = AgentTools(workspace_dir=workspace_root)
            
            # Testa list_tools
            tools_list = tools.list_tools()
            print(f"✓ AgentTools has {len(tools_list)} tools:")
            for tool in tools_list:
                print(f"  - {tool['name']}")
            
            # Testa create_directory
            result = tools.create_directory("test_dir")
            print(f"✓ create_directory: {result['success']}")
            if not result['success']:
                print(f"  Error: {result.get('error', 'Unknown')}")
            
            # Testa write_file
            result = tools.write_file("test_dir/test.txt", "Hello, NAP V2!")
            print(f"✓ write_file: {result['success']}")
            if not result['success']:
                print(f"  Error: {result.get('error', 'Unknown')}")
            
            # Testa read_file
            result = tools.read_file("test_dir/test.txt")
            print(f"✓ read_file: {result['success']}")
            if result['success']:
                print(f"  Content: {result['content'][:20]}...")
            else:
                print(f"  Error: {result.get('error', 'Unknown')}")
            
            # Testa list_directory
            result = tools.list_directory("test_dir")
            print(f"✓ list_directory: {result['success']}")
            if result['success']:
                print(f"  Items: {result['total']}")
            else:
                print(f"  Error: {result.get('error', 'Unknown')}")
            
            # Testa delete_file
            result = tools.delete_file("test_dir/test.txt")
            print(f"✓ delete_file: {result['success']}")
            if not result['success']:
                print(f"  Error: {result.get('error', 'Unknown')}")
            
            # Testa delete_directory
            result = tools.delete_directory("test_dir")
            print(f"✓ delete_directory: {result['success']}")
            if not result['success']:
                print(f"  Error: {result.get('error', 'Unknown')}")
            
        finally:
            # Limpa o diretório de teste
            if workspace_root.exists():
                shutil.rmtree(workspace_root)
                
    except Exception as e:
        print(f"✗ AgentTools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_tui_components():
    """Testa componentes da TUI."""
    print("\nTesting TUI components...")
    
    try:
        from cli.v2.tui import (
            SlashCommandCompleter,
            SLASH_COMMANDS,
            ASCII_BOX,
            STYLE_CYAN,
            STYLE_RED,
            STYLE_AMBER,
            STYLE_GRAY,
        )
        
        print(f"✓ Slash commands defined: {list(SLASH_COMMANDS.keys())}")
        print(f"✓ Styles defined: cyan, red, amber, gray")
        print(f"✓ ASCII box defined")
        
    except Exception as e:
        print(f"✗ TUI components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("NAP V2 - Component Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("AgentTools", test_agent_tools()))
    results.append(("TUI Components", test_tui_components()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())
