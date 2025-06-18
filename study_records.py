import csv
import json
import os
from datetime import datetime
from io import StringIO # Importar StringIO para exportação CSV em memória

DATA_FILE_CSV = 'study_records.csv'
DATA_FILE_JSON = 'study_records.json'

def _get_data_file_path(file_type='csv'):
    """Retorna o caminho completo para o arquivo de dados."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if file_type == 'csv':
        return os.path.join(base_dir, DATA_FILE_CSV)
    elif file_type == 'json':
        return os.path.join(base_dir, DATA_FILE_JSON)
    return None

def add_study_record(subject: str, duration_minutes: int, quality: int, notes: str = "") -> bool:
    """
    Adiciona um novo registro de estudo.
    Retorna True se o registro foi adicionado com sucesso, False caso contrário.
    """
    timestamp = datetime.now().isoformat()
    record = {
        "timestamp": timestamp,
        "subject": subject,
        "duration_minutes": duration_minutes,
        "quality": quality,
        "notes": notes
    }

    # Salvar em CSV
    try:
        file_exists = os.path.exists(_get_data_file_path('csv'))
        with open(_get_data_file_path('csv'), 'a', newline='', encoding='utf-8') as f:
            fieldnames = ["timestamp", "subject", "duration_minutes", "quality", "notes"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)
    except IOError as e:
        print(f"Erro ao salvar em CSV: {e}")
        return False

    # Salvar em JSON (opcional)
    try:
        records_json = []
        if os.path.exists(_get_data_file_path('json')):
            with open(_get_data_file_path('json'), 'r', encoding='utf-8') as f:
                try:
                    records_json = json.load(f)
                except json.JSONDecodeError:
                    records_json = [] # Arquivo vazio ou corrompido
        records_json.append(record)
        with open(_get_data_file_path('json'), 'w', encoding='utf-8') as f:
            json.dump(records_json, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Erro ao salvar em JSON: {e}")
        return False

    return True

def _write_records_to_csv(records: list):
    """Função auxiliar para reescrever todos os registros no CSV."""
    file_path = _get_data_file_path('csv')
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["timestamp", "subject", "duration_minutes", "quality", "notes"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        return True
    except IOError as e:
        print(f"Erro ao reescrever CSV: {e}")
        return False

def _write_records_to_json(records: list):
    """Função auxiliar para reescrever todos os registros no JSON."""
    file_path = _get_data_file_path('json')
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Erro ao reescrever JSON: {e}")
        return False

def get_all_study_records() -> list:
    """
    Carrega e retorna todos os registros de estudo do arquivo CSV.
    """
    records = []
    file_path = _get_data_file_path('csv')
    if not os.path.exists(file_path):
        return records

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row['duration_minutes'] = int(row['duration_minutes'])
                except (ValueError, TypeError):
                    row['duration_minutes'] = 0

                if 'quality' in row and row['quality'].isdigit():
                    row['quality'] = int(row['quality'])
                else:
                    row['quality'] = 0
                records.append(row)
    except IOError as e:
        print(f"Erro ao carregar registros: {e}")
    return records

def get_record_by_timestamp(timestamp: str) -> dict:
    """
    Busca um único registro pelo seu timestamp.
    """
    records = get_all_study_records()
    for record in records:
        if record['timestamp'] == timestamp:
            return record
    return None

def update_study_record(timestamp: str, new_subject: str, new_duration_minutes: int, new_quality: int, new_notes: str = "") -> bool:
    """
    Atualiza um registro de estudo existente.
    Retorna True se a atualização foi bem-sucedida, False caso contrário.
    """
    records = get_all_study_records()
    found = False
    for i, record in enumerate(records):
        if record['timestamp'] == timestamp:
            records[i]['subject'] = new_subject
            records[i]['duration_minutes'] = new_duration_minutes
            records[i]['quality'] = new_quality
            records[i]['notes'] = new_notes
            found = True
            break
    
    if found:
        if _write_records_to_csv(records) and _write_records_to_json(records):
            return True
    return False

def delete_study_record(timestamp: str) -> bool:
    """
    Exclui um registro de estudo.
    Retorna True se a exclusão foi bem-sucedida, False caso contrário.
    """
    records = get_all_study_records()
    initial_count = len(records)
    records = [record for record in records if record['timestamp'] != timestamp]
    
    if len(records) < initial_count:
        if _write_records_to_csv(records) and _write_records_to_json(records):
            return True
    return False

def get_records_by_subject(subject: str) -> list:
    """
    Retorna registros filtrados por matéria.
    """
    all_records = get_all_study_records()
    return [r for r in all_records if r['subject'].lower() == subject.lower()]

def get_total_study_duration(subject: str = None) -> int:
    """
    Calcula a duração total de estudo, opcionalmente por matéria.
    Retorna a duração total em minutos.
    """
    records = get_all_study_records()
    total_minutes = 0
    for record in records:
        if subject is None or record['subject'].lower() == subject.lower():
            total_minutes += record.get('duration_minutes', 0)
    return total_minutes

def get_average_quality(subject: str = None) -> float:
    """
    Calcula a média da qualidade de estudo, opcionalmente por matéria.
    Retorna a média como float.
    """
    records = get_all_study_records()
    total_quality = 0
    count = 0
    for record in records:
        if subject is None or record['subject'].lower() == subject.lower():
            quality = record.get('quality', 0)
            if quality > 0:
                total_quality += quality
                count += 1
    return total_quality / count if count > 0 else 0.0

def export_records_to_csv_string() -> str:
    """
    Exporta todos os registros para uma string CSV.
    """
    records = get_all_study_records()
    output = StringIO()
    fieldnames = ["timestamp", "subject", "duration_minutes", "quality", "notes"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
    
    writer.writeheader()
    writer.writerows(records)
    
    return output.getvalue()

def export_records_to_json_string() -> str:
    """
    Exporta todos os registros para uma string JSON formatada.
    """
    records = get_all_study_records()
    return json.dumps(records, indent=4, ensure_ascii=False)