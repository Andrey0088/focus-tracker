from colorama import Fore, Style, init
import os # <--- Adicione esta linha

# Inicializa o colorama para que funcione em diferentes terminais
init(autoreset=True)

def print_header(text: str):
    """Imprime um cabeçalho formatado."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- {text.upper()} ---{Style.RESET_ALL}\n")

def print_success(text: str):
    """Imprime uma mensagem de sucesso."""
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")

def print_info(text: str):
    """Imprime uma mensagem informativa."""
    print(f"{Fore.BLUE}{text}{Style.RESET_ALL}")

def print_warning(text: str):
    """Imprime uma mensagem de aviso."""
    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")

def print_error(text: str):
    """Imprime uma mensagem de erro."""
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")

def get_input(prompt: str, type_cast=str):
    """Pega uma entrada do usuário com formatação."""
    while True:
        try:
            value = input(f"{Fore.MAGENTA}{prompt}{Style.RESET_ALL}").strip()
            if not value and type_cast != str: # Permite string vazia para notas, etc.
                raise ValueError("A entrada não pode ser vazia.")
            return type_cast(value)
        except ValueError:
            print_error("Entrada inválida. Tente novamente.")
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            return None

def format_duration(minutes: int) -> str:
    """Formata minutos em horas e minutos."""
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours > 0:
        return f"{hours}h {remaining_minutes}min"
    return f"{remaining_minutes}min"

def display_menu(options: dict):
    """Exibe um menu de opções."""
    print_header("MENU")
    for key, value in options.items():
        print(f"  {Fore.YELLOW}[{key}]{Style.RESET_ALL} {value}")
    print()

def clear_screen():
    """Limpa a tela do terminal."""
    # Para sistemas Unix/macOS/Linux
    if os.name == 'posix':
        os.system('clear')
    # Para Windows
    elif os.name == 'nt':
        os.system('cls')