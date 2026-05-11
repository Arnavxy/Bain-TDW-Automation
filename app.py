import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from werkzeug.utils import secure_filename
import pandas as pd
from config import APP_NAME, SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE, L1_CATEGORIES
from modules.data_loader import DataLoader
from modules.l1_l2_parser import L1L2Parser
from modules.cut_generator import CutGenerator
from modules.excel_formatter import FormulaExcelFormatter
from modules.validator import DataValidator

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    return render_template('landing.html', app_name=APP_NAME)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save file with unique name
            filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store in session
            session['uploaded_file'] = filepath
            session['original_filename'] = file.filename
            
            # Load and get sheet names
            try:
                loader = DataLoader(filepath)
                sheets = loader.get_sheet_names()
                session['sheets'] = sheets
                return redirect(url_for('select_sheet'))
            except Exception as e:
                flash(f'Error reading file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload an Excel file (.xlsx or .xls)', 'error')
            return redirect(request.url)
    
    return render_template('upload.html', app_name=APP_NAME)

@app.route('/select_sheet', methods=['GET', 'POST'])
def select_sheet():
    if 'uploaded_file' not in session:
        flash('Please upload a file first', 'error')
        return redirect(url_for('upload'))
    
    sheets = session.get('sheets', [])
    
    if request.method == 'POST':
        selected_sheet = request.form.get('sheet')
        if not selected_sheet:
            flash('Please select a sheet', 'error')
            return redirect(request.url)
        
        session['selected_sheet'] = selected_sheet
        
        # Load sheet and get columns
        try:
            loader = DataLoader(session['uploaded_file'])
            loader.load_sheet(selected_sheet)
            columns = loader.get_columns()
            session['columns'] = columns
            return redirect(url_for('validation'))
        except Exception as e:
            flash(f'Error loading sheet: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('select_sheet.html', app_name=APP_NAME, sheets=sheets)

@app.route('/validation', methods=['GET', 'POST'])
def validation():
    if 'selected_sheet' not in session:
        flash('Please select a sheet first', 'error')
        return redirect(url_for('upload'))
    
    if request.method == 'POST':
        # Apply selected fixes
        validator = DataValidator(session['uploaded_file'])
        validator.validate_file()
        validator.validate_sheet(session['selected_sheet'])
        
        # Get selected fixes from form
        for key, value in request.form.items():
            if key.startswith('fix_') and value != 'ignore':
                validator.apply_fix(value)
        
        # Save cleaned data
        cleaned_df = validator.get_dataframe()
        cleaned_file = os.path.join(app.config['UPLOAD_FOLDER'], 'cleaned_' + str(uuid.uuid4()) + '.pkl')
        cleaned_df.to_pickle(cleaned_file)
        session['cleaned_file'] = cleaned_file
        
        return redirect(url_for('mapping'))
    
    # GET - show validation results
    validator = DataValidator(session['uploaded_file'])
    success, file_issues = validator.validate_file()
    
    if not success:
        return render_template('validation.html', 
                             app_name=APP_NAME,
                             errors=file_issues,
                             warnings=[])
    
    success, sheet_issues = validator.validate_sheet(session['selected_sheet'])
    
    errors = [i for i in sheet_issues if i['type'] == 'error']
    warnings = [i for i in sheet_issues if i['type'] != 'error']
    
    return render_template('validation.html',
                         app_name=APP_NAME,
                         errors=errors,
                         warnings=warnings)

@app.route('/mapping', methods=['GET', 'POST'])
def mapping():
    if 'columns' not in session:
        flash('Please upload a file first', 'error')
        return redirect(url_for('upload'))
    
    columns = session.get('columns', [])
    
    if request.method == 'POST':
        l2_column = request.form.get('l2_column')
        demo1 = request.form.get('demo1')
        demo2 = request.form.get('demo2')
        demo3 = request.form.get('demo3')
        include_pct = request.form.get('include_percentages') == 'on'
        
        if not all([l2_column, demo1, demo2, demo3]):
            flash('Please select all columns', 'error')
            return redirect(request.url)
        
        if len(set([demo1, demo2, demo3])) != 3:
            flash('Please select three different demographic columns', 'error')
            return redirect(request.url)
        
        session['l2_column'] = l2_column
        session['demo1'] = demo1
        session['demo2'] = demo2
        session['demo3'] = demo3
        session['include_percentages'] = include_pct
        
        return redirect(url_for('review'))
    
    return render_template('mapping.html', app_name=APP_NAME, columns=columns)

@app.route('/review', methods=['GET', 'POST'])
def review():
    if 'l2_column' not in session:
        flash('Please complete column mapping first', 'error')
        return redirect(url_for('mapping'))
    
    # Load data and parse L1/L2
    try:
        # Use cleaned data if available
        if 'cleaned_file' in session and os.path.exists(session['cleaned_file']):
            df = pd.read_pickle(session['cleaned_file'])
        else:
            loader = DataLoader(session['uploaded_file'])
            df = loader.load_sheet(session['selected_sheet'])
        
        parser = L1L2Parser(df, session['l2_column'])
        parsed_df = parser.parse()
        
        # Store parsed data temporarily
        parsed_file = os.path.join(app.config['UPLOAD_FOLDER'], 'parsed_' + str(uuid.uuid4()) + '.pkl')
        parsed_df.to_pickle(parsed_file)
        session['parsed_file'] = parsed_file
        
        anomalies = parser.get_anomalies()
        session['anomalies'] = anomalies
        
        if request.method == 'POST':
            # Handle anomaly overrides
            for anomaly in anomalies:
                row_idx = anomaly['row_index']
                l1_override = request.form.get(f'l1_override_{row_idx}')
                l2_override = request.form.get(f'l2_override_{row_idx}')
                
                if l1_override and l2_override:
                    parser.update_anomaly(row_idx, l1_override, l2_override)
            
            # Save updated parsed data
            parsed_df = parser.get_parsed_df()
            parsed_df.to_pickle(parsed_file)
            
            return redirect(url_for('processing'))
        
        return render_template('anomalies.html', 
                             app_name=APP_NAME,
                             anomalies=anomalies,
                             has_anomalies=parser.has_anomalies(),
                             l1_categories=L1_CATEGORIES)
    
    except Exception as e:
        flash(f'Error parsing data: {str(e)}', 'error')
        return redirect(url_for('mapping'))

@app.route('/processing')
def processing():
    if 'parsed_file' not in session:
        flash('Please complete anomaly review first', 'error')
        return redirect(url_for('review'))
    
    try:
        # Load parsed data
        parsed_df = pd.read_pickle(session['parsed_file'])
        
        # Generate cuts
        generator = CutGenerator(
            parsed_df,
            'L1_Parsed',
            'L2_Parsed',
            session['demo1'],
            session['demo2'],
            session['demo3']
        )
        cuts = generator.generate_all_cuts()
        
        # Add L2_Full column for cross-cut formulas (needed by formatter)
        parsed_df['L2_Full'] = parsed_df['L1_Parsed'] + ' | ' + parsed_df['L2_Parsed']
        
        # Format Excel with formulas
        include_pct = session.get('include_percentages', False)
        formatter = FormulaExcelFormatter(include_percentages=include_pct)
        
        # Add Raw_Data sheet with all original columns + parsed L1/L2
        formatter.add_raw_data(parsed_df)
        
        # Add TDW_Cuts sheet with formulas
        demo_columns = [session['demo1'], session['demo2'], session['demo3']]
        formatter.add_cuts(cuts, demo_columns)
        
        # Save output
        output_filename = 'TDW_Cuts_' + str(uuid.uuid4())[:8] + '.xlsx'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        formatter.save(output_path)
        
        session['output_file'] = output_path
        
        # Convert cuts to JSON-serializable format for preview
        cuts_preview = {}
        for key, cut in cuts.items():
            cuts_preview[key] = {
                'title': str(cut['title']),
                'total': int(cut['total']),
                'is_demographic': bool(cut.get('is_demographic', False))
            }
            if 'column_name' in cut:
                cuts_preview[key]['column_name'] = str(cut['column_name'])
            if 'categories' in cut:
                cuts_preview[key]['categories'] = [str(c) for c in cut['categories']]
                cuts_preview[key]['values'] = [int(v) for v in cut['values']]
            if 'rows' in cut:
                cuts_preview[key]['rows'] = [str(r) for r in cut['rows']]
                cuts_preview[key]['columns'] = [str(c) for c in cut['columns']]
                cuts_preview[key]['data'] = [[int(v) for v in row] for row in cut['data']]
        
        # Save to pickle file instead of session (too large for JSON)
        preview_file = os.path.join(app.config['UPLOAD_FOLDER'], 'preview_' + str(uuid.uuid4())[:8] + '.pkl')
        import pickle
        with open(preview_file, 'wb') as f:
            pickle.dump(cuts_preview, f)
        session['preview_file'] = preview_file
        
        return redirect(url_for('results'))
    
    except Exception as e:
        flash(f'Error generating cuts: {str(e)}', 'error')
        import traceback
        app.logger.error(traceback.format_exc())
        return redirect(url_for('review'))

@app.route('/results')
def results():
    if 'output_file' not in session:
        flash('Please complete processing first', 'error')
        return redirect(url_for('upload'))
    
    # Load cuts preview from pickle file
    cuts = {}
    if 'preview_file' in session and os.path.exists(session['preview_file']):
        import pickle
        with open(session['preview_file'], 'rb') as f:
            cuts = pickle.load(f)
    
    # Pre-zip data for template (Jinja2 can't do variable indexing)
    for key, cut in cuts.items():
        if 'categories' in cut and 'values' in cut:
            cut['zipped'] = list(zip(cut['categories'], cut['values']))
        if 'rows' in cut and 'data' in cut:
            cut['zipped_rows'] = list(zip(cut['rows'], cut['data']))
    
    original_filename = session.get('original_filename', 'data.xlsx')
    
    return render_template('results.html',
                         app_name=APP_NAME,
                         cuts=cuts,
                         original_filename=original_filename)

@app.route('/download')
def download():
    if 'output_file' not in session:
        flash('No file to download', 'error')
        return redirect(url_for('upload'))
    
    output_path = session['output_file']
    original_name = session.get('original_filename', 'data.xlsx')
    # Proper filename construction
    base_name = original_name.rsplit('.', 1)[0]  # Remove original extension
    download_name = f"{base_name}_TDW_Cuts.xlsx"
    
    if os.path.exists(output_path):
        response = send_file(output_path, 
                        as_attachment=True,
                        download_name=download_name,
                        mimetype='application/octet-stream')
        # Force Excel download with proper headers
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.headers["Content-Disposition"] = f'attachment; filename="{download_name}"'
        response.headers["Cache-Control"] = "no-cache"
        return response
    else:
        flash('File not found', 'error')
        return redirect(url_for('results'))

@app.route('/new')
def new_analysis():
    # Clear session but keep uploaded file for now
    keys_to_remove = ['output_file', 'preview_file', 'parsed_file', 'anomalies',
                      'l2_column', 'demo1', 'demo2', 'demo3', 'include_percentages']
    for key in keys_to_remove:
        session.pop(key, None)
    
    return redirect(url_for('mapping'))

@app.route('/clear')
def clear_all():
    # Remove uploaded files
    if 'uploaded_file' in session:
        try:
            os.remove(session['uploaded_file'])
        except:
            pass
    
    if 'parsed_file' in session:
        try:
            os.remove(session['parsed_file'])
        except:
            pass
    
    if 'preview_file' in session:
        try:
            os.remove(session['preview_file'])
        except:
            pass
    
    if 'cleaned_file' in session:
        try:
            os.remove(session['cleaned_file'])
        except:
            pass
    
    if 'output_file' in session:
        try:
            os.remove(session['output_file'])
        except:
            pass
    
    session.clear()
    return redirect(url_for('upload'))

@app.route('/guide')
def guide():
    return render_template('guide.html', app_name=APP_NAME)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)