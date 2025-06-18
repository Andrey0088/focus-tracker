from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from study_records import (
    add_study_record,
    get_all_study_records,
    get_total_study_duration,
    get_average_quality,
    get_record_by_timestamp,
    update_study_record,
    delete_study_record,
    export_records_to_csv_string,
    export_records_to_json_string
)
from datetime import datetime, timedelta
from collections import defaultdict
from io import BytesIO

def format_duration(minutes: int) -> str:
    """Formata minutos em horas e minutos."""
    if minutes is None:
        return "0min"
    hours = minutes // 60
    remaining_minutes = minutes % 60 # Variável definida aqui
    if hours > 0:
        return f"{hours}h {remaining_minutes}min"
    return f"{remaining_minutes}min" # <--- CORRIGIDO: usa remaining_minutes

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_segura_e_longa_para_flash_messages'

# Configuração do banco de dados SQLite (local ou nuvem)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///study_records.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para os registros de estudo
class StudyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    quality = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    timestamp = db.Column(db.String(30), nullable=False)

# Rotas existentes (index, register, records, edit, delete, summary, export_csv, export_json)
# Permanecem as mesmas, não vou repetir aqui para concisão.
# Apenas a rota /analytics será alterada e uma nova /api/analytics_data será adicionada.

# -----------------------------------------------------------------------------
# Rotas anteriores (mantidas como estão, não copie se já as tiver)
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    all_records = get_all_study_records()
    total_duration = get_total_study_duration()
    overall_avg_quality = get_average_quality()
    
    subject_durations_raw = defaultdict(int)
    subject_qualities_raw = defaultdict(lambda: {'total': 0, 'count': 0})
    daily_study_data = defaultdict(int)
    today_date_obj = datetime.now().date()
    
    for record in all_records:
        subject = record['subject'].lower()
        duration = record.get('duration_minutes', 0)
        quality = record.get('quality', 0)

        subject_durations_raw[subject] += duration
        if quality > 0:
            subject_qualities_raw[subject]['total'] += quality
            subject_qualities_raw[subject]['count'] += 1

        try:
            record_date = datetime.fromisoformat(record['timestamp']).date()
            daily_study_data[record_date] += duration
        except ValueError:
            pass

    formatted_total_duration = format_duration(total_duration)
    formatted_subject_durations = {}
    for subject, duration in sorted(subject_durations_raw.items()):
        avg_quality = subject_qualities_raw[subject]['total'] / subject_qualities_raw[subject]['count'] if subject_qualities_raw[subject]['count'] > 0 else 0.0
        formatted_subject_durations[subject.capitalize()] = {
            'duration': format_duration(duration),
            'avg_quality': f"{avg_quality:.1f}" if avg_quality > 0 else "N/A"
        }

    chart_subject_labels = [s.capitalize() for s in sorted(subject_durations_raw.keys())]
    chart_subject_data = [subject_durations_raw[s] for s in sorted(subject_durations_raw.keys())]

    daily_chart_labels = []
    daily_chart_data = []
    for i in range(30):
        date = today_date_obj - timedelta(days=29 - i)
        daily_chart_labels.append(date.strftime("%d/%m"))
        daily_chart_data.append(daily_study_data.get(date, 0))

    return render_template('index.html', 
                           total_duration=formatted_total_duration,
                           overall_avg_quality=f"{overall_avg_quality:.1f}" if overall_avg_quality > 0 else "N/A",
                           subject_summary=formatted_subject_durations,
                           chart_subject_labels=chart_subject_labels,
                           chart_subject_data=chart_subject_data,
                           daily_chart_labels=daily_chart_labels,
                           daily_chart_data=daily_chart_data)

@app.route('/register', methods=['GET', 'POST'])
def register_session():
    all_records = get_all_study_records()
    unique_subjects = sorted(list(set(r['subject'] for r in all_records)))
    
    standard_durations = [30, 60, 90, 120] 

    if request.method == 'POST':
        subject = request.form['subject'].strip()
        duration_minutes_str = request.form['duration'].strip()
        quality_str = request.form['quality'].strip()
        notes = request.form.get('notes', '').strip()

        if not subject or not duration_minutes_str or not quality_str:
            flash('Matéria, Duração e Qualidade são campos obrigatórios!', 'error')
        else:
            try:
                duration_minutes = int(duration_minutes_str)
                quality = int(quality_str)
                
                if duration_minutes <= 0:
                    flash('A duração deve ser um número positivo.', 'error')
                elif not (1 <= quality <= 5):
                    flash('A qualidade deve ser um número entre 1 e 5.', 'error')
                else:
                    if add_study_record(subject, duration_minutes, quality, notes): 
                        flash(f'Sessão de {subject} ({format_duration(duration_minutes)}) registrada com sucesso!', 'success')
                        return redirect(url_for('view_records'))
                    else:
                        flash('Erro ao registrar a sessão de estudo.', 'error')
            except ValueError:
                flash('Duração e/ou Qualidade inválida(s). Por favor, insira números inteiros válidos.', 'error')
        
        return render_template('register.html', 
                               subject=subject, 
                               duration=duration_minutes_str, 
                               quality=quality_str, 
                               notes=notes,
                               unique_subjects=unique_subjects,
                               standard_durations=standard_durations)
    
    return render_template('register.html', 
                           unique_subjects=unique_subjects,
                           standard_durations=standard_durations)

@app.route('/records')
def view_records():
    all_records = get_all_study_records()

    subject_filter = request.args.get('subject_filter', '').strip()
    sort_by = request.args.get('sort_by', 'timestamp').strip()
    sort_order = request.args.get('sort_order', 'desc').strip()

    filtered_records = all_records

    if subject_filter:
        filtered_records = [r for r in filtered_records if subject_filter.lower() in r['subject'].lower()]
    
    if sort_by == 'duration':
        filtered_records.sort(key=lambda x: x.get('duration_minutes', 0), reverse=(sort_order == 'desc'))
    elif sort_by == 'subject':
        filtered_records.sort(key=lambda x: x.get('subject', '').lower(), reverse=(sort_order == 'desc'))
    elif sort_by == 'quality':
        filtered_records.sort(key=lambda x: x.get('quality', 0), reverse=(sort_order == 'desc'))
    else:
        filtered_records.sort(key=lambda x: x.get('timestamp', ''), reverse=(sort_order == 'desc'))

    for record in filtered_records:
        try:
            dt_object = datetime.fromisoformat(record['timestamp'])
            record['formatted_date'] = dt_object.strftime("%d/%m/%Y")
            record['formatted_time'] = dt_object.strftime("%H:%M")
        except ValueError:
            record['formatted_date'] = "Data Inválida"
            record['formatted_time'] = "Hora Inválida"
        record['formatted_duration'] = format_duration(record.get('duration_minutes', 0))
        record['display_quality'] = record.get('quality', 0) if record.get('quality', 0) > 0 else "N/A"

    unique_subjects = sorted(list(set(r['subject'] for r in all_records)))
    
    return render_template('records.html', 
                           records=filtered_records,
                           unique_subjects=unique_subjects,
                           current_subject_filter=subject_filter,
                           current_sort_by=sort_by,
                           current_sort_order=sort_order)

@app.route('/edit/<path:timestamp>', methods=['GET', 'POST'])
def edit_record(timestamp):
    record = get_record_by_timestamp(timestamp)
    if not record:
        flash('Registro não encontrado.', 'error')
        return redirect(url_for('view_records'))
    
    all_records = get_all_study_records()
    unique_subjects = sorted(list(set(r['subject'] for r in all_records)))
    standard_durations = [30, 60, 90, 120]

    if request.method == 'POST':
        new_subject = request.form['subject'].strip()
        new_duration_minutes_str = request.form['duration'].strip()
        new_quality_str = request.form['quality'].strip()
        new_notes = request.form.get('notes', '').strip()

        if not new_subject or not new_duration_minutes_str or not new_quality_str:
            flash('Matéria, Duração e Qualidade são campos obrigatórios!', 'error')
        else:
            try:
                new_duration_minutes = int(new_duration_minutes_str)
                new_quality = int(new_quality_str)
                
                if new_duration_minutes <= 0:
                    flash('A duração deve ser um número positivo.', 'error')
                elif not (1 <= new_quality <= 5):
                    flash('A qualidade deve ser um número entre 1 e 5.', 'error')
                else:
                    if update_study_record(timestamp, new_subject, new_duration_minutes, new_quality, new_notes):
                        flash('Registro atualizado com sucesso!', 'success')
                        return redirect(url_for('view_records'))
                    else:
                        flash('Erro ao atualizar o registro.', 'error')
            except ValueError:
                flash('Duração e/ou Qualidade inválida(s). Por favor, insira números inteiros válidos.', 'error')
        
        return render_template('edit.html', 
                               record=record,
                               subject=new_subject, 
                               duration=new_duration_minutes_str, 
                               quality=new_quality_str, 
                               notes=new_notes,
                               unique_subjects=unique_subjects,
                               standard_durations=standard_durations)
    
    return render_template('edit.html', 
                           record=record,
                           unique_subjects=unique_subjects,
                           standard_durations=standard_durations)

@app.route('/delete/<path:timestamp>', methods=['POST'])
def delete_record(timestamp):
    if delete_study_record(timestamp):
        flash('Registro excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir o registro.', 'error')
    return redirect(url_for('view_records'))

@app.route('/summary')
def view_detailed_summary():
    all_records = get_all_study_records()
    total_duration = get_total_study_duration()
    overall_avg_quality = get_average_quality()
    
    subject_durations = defaultdict(int)
    subject_qualities = defaultdict(lambda: {'total': 0, 'count': 0})
    
    for record in all_records:
        subject = record['subject'].lower()
        duration = record.get('duration_minutes', 0)
        quality = record.get('quality', 0)
        
        subject_durations[subject] += duration
        if quality > 0:
            subject_qualities[subject]['total'] += quality
            subject_qualities[subject]['count'] += 1
    
    summary_data = []
    for subject, duration in sorted(subject_durations.items()):
        subject_records = [r for r in all_records if r['subject'].lower() == subject.lower()]
        formatted_subject_duration = format_duration(duration)
        
        subject_records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        formatted_subject_records = []
        for r in subject_records:
            try:
                dt_object = datetime.fromisoformat(r['timestamp'])
                r['formatted_date'] = dt_object.strftime("%d/%m/%Y")
                r['formatted_time'] = dt_object.strftime("%H:%M")
            except ValueError:
                r['formatted_date'] = "Data Inválida"
                r['formatted_time'] = "Hora Inválida"
            r['formatted_duration'] = format_duration(r.get('duration_minutes', 0))
            r['display_quality'] = r.get('quality', 0) if r.get('quality', 0) > 0 else "N/A"
            formatted_subject_records.append(r)

        avg_quality_subject = subject_qualities[subject]['total'] / subject_qualities[subject]['count'] if subject_qualities[subject]['count'] > 0 else 0.0
        
        summary_data.append({
            'subject': subject.capitalize(),
            'total_duration': formatted_subject_duration,
            'avg_quality': f"{avg_quality_subject:.1f}" if avg_quality_subject > 0 else "N/A",
            'records': formatted_subject_records
        })

    return render_template('summary.html', 
                           total_duration=format_duration(total_duration),
                           summary_data=summary_data,
                           overall_avg_quality=f"{overall_avg_quality:.1f}" if overall_avg_quality > 0 else "N/A")

# ROTA: Analytics (agora apenas renderiza o template HTML)
@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

# NOVA ROTA: API para dados do Analytics (retorna JSON)
@app.route('/api/analytics_data')
def api_analytics_data():
    all_records = get_all_study_records()

    # --- Dados para Gráfico de Qualidade Média por Matéria (Barra) ---
    subject_quality_avg_raw = defaultdict(lambda: {'total': 0, 'count': 0})
    for record in all_records:
        subject = record['subject'].lower()
        quality = record.get('quality', 0)
        if quality > 0:
            subject_quality_avg_raw[subject]['total'] += quality
            subject_quality_avg_raw[subject]['count'] += 1
    
    analytics_quality_labels = []
    analytics_quality_data = []
    for s in sorted(subject_quality_avg_raw.keys()):
        if subject_quality_avg_raw[s]['count'] > 0:
            analytics_quality_labels.append(s.capitalize())
            analytics_quality_data.append(
                round(subject_quality_avg_raw[s]['total'] / subject_quality_avg_raw[s]['count'], 1)
            )

    # --- Dados para Gráfico de Tempo de Estudo por Dia da Semana (Barra) ---
    days_of_week = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    daily_weekday_study = defaultdict(int)
    for record in all_records:
        try:
            record_datetime = datetime.fromisoformat(record['timestamp'])
            weekday_index = record_datetime.weekday()
            daily_weekday_study[weekday_index] += record.get('duration_minutes', 0)
        except ValueError:
            pass
    
    analytics_weekday_labels = days_of_week
    analytics_weekday_data = [daily_weekday_study[i] for i in range(7)]

    # --- Dados para Gráfico de Contagem de Sessões por Matéria (Barra) ---
    subject_session_counts = defaultdict(int)
    for record in all_records:
        subject_session_counts[record['subject'].lower()] += 1
    
    analytics_session_labels = [s.capitalize() for s in sorted(subject_session_counts.keys())]
    analytics_session_data = [subject_session_counts[s] for s in sorted(subject_session_counts.keys())]

    # Retorna todos os dados como JSON
    return jsonify({
        'quality': {
            'labels': analytics_quality_labels,
            'data': analytics_quality_data
        },
        'weekday': {
            'labels': analytics_weekday_labels,
            'data': analytics_weekday_data
        },
        'sessions': {
            'labels': analytics_session_labels,
            'data': analytics_session_data
        }
    })


@app.route('/export/csv')
def export_csv():
    csv_string = export_records_to_csv_string()
    csv_buffer = BytesIO(csv_string.encode('utf-8'))
    
    timestamp_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"life_organizer_studies_{timestamp_now}.csv"
    
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=file_name
    )

@app.route('/export/json')
def export_json():
    json_string = export_records_to_json_string()
    json_buffer = BytesIO(json_string.encode('utf-8'))
    
    timestamp_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"life_organizer_studies_{timestamp_now}.json"

    return send_file(
        json_buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=file_name
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')