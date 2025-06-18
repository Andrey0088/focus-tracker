from study_records import add_study_record, get_all_study_records, get_total_study_duration, get_records_by_subject
from utils import print_header, print_success, print_info, print_error, get_input, format_duration, display_menu, clear_screen
from datetime import datetime

def register_study_session():
    """Função para registrar uma nova sessão de estudo."""
    print_header("REGISTRAR SESSÃO DE ESTUDO")
    subject = get_input("Qual matéria você estudou? ")
    if subject is None: return

    duration_str = get_input("Por quanto tempo você estudou (em minutos)? ", int)
    if duration_str is None: return

    notes = get_input("Alguma anotação (opcional)? ")
    if notes is None: notes = "" # Garante que notas é string vazia se cancelado

    if add_study_record(subject, duration_str, notes):
        print_success(f"\nSessão de {subject} ({format_duration(duration_str)}) registrada com sucesso!")
    else:
        print_error("Erro ao registrar a sessão de estudo.")

def view_all_records():
    """Função para visualizar todos os registros."""
    print_header("TODOS OS REGISTROS DE ESTUDO")
    records = get_all_study_records()
    if not records:
        print_info("Nenhum registro de estudo encontrado ainda.")
        return

    # Encontrar a largura máxima para cada coluna para um bom alinhamento
    max_timestamp = max(len(r['timestamp']) for r in records) if records else len("Data/Hora")
    max_subject = max(len(r['subject']) for r in records) if records else len("Matéria")
    max_duration = max(len(format_duration(r['duration_minutes'])) for r in records) if records else len("Duração")
    max_notes = max(len(r['notes']) for r in records) if records else len("Notas")

    print(f"{'Data/Hora'.ljust(max_timestamp)} | {'Matéria'.ljust(max_subject)} | {'Duração'.ljust(max_duration)} | Notas")
    print("-" * (max_timestamp + max_subject + max_duration + max_notes + 9)) # Ajuste para os separadores

    for record in records:
        try:
            dt_object = datetime.fromisoformat(record['timestamp'])
            formatted_timestamp = dt_object.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            formatted_timestamp = record['timestamp'] # Caso não seja um formato ISO válido

        print(
            f"{formatted_timestamp.ljust(max_timestamp)} | "
            f"{record['subject'].ljust(max_subject)} | "
            f"{format_duration(record['duration_minutes']).ljust(max_duration)} | "
            f"{record['notes'].ljust(max_notes)}"
        )
    print_info(f"\nTotal de sessões: {len(records)}")

def view_summary():
    """Função para visualizar um resumo dos estudos."""
    print_header("RESUMO DOS ESTUDOS")
    total_duration = get_total_study_duration()
    print_info(f"Tempo total de estudo registrado: {format_duration(total_duration)}\n")

    records = get_all_study_records()
    if not records:
        print_info("Nenhum registro para resumir.")
        return

    subjects = sorted(list(set(r['subject'] for r in records)))
    if subjects:
        print_info("Tempo de estudo por matéria:")
        for subject in subjects:
            subject_duration = get_total_study_duration(subject)
            print(f"  - {subject}: {format_duration(subject_duration)}")
    else:
        print_info("Nenhuma matéria encontrada nos registros.")

def main_menu():
    """Exibe o menu principal e lida com as escolhas do usuário."""
    while True:
        clear_screen()
        print_header("APLICATIVO REGISTRO DE ESTUDOS")
        options = {
            "1": "Registrar nova sessão",
            "2": "Ver todos os registros",
            "3": "Ver resumo dos estudos",
            "4": "Sair"
        }
        display_menu(options)

        choice = get_input("Escolha uma opção: ")

        if choice == '1':
            register_study_session()
        elif choice == '2':
            view_all_records()
        elif choice == '3':
            view_summary()
        elif choice == '4':
            print_info("Saindo do aplicativo. Bons estudos!")
            break
        else:
            print_error("Opção inválida. Por favor, tente novamente.")

        get_input("\nPressione ENTER para continuar...", str) # Pausa para o usuário ler a saída

if __name__ == "__main__":
    main_menu()