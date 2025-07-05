import os
from flask import Flask, request, send_file, render_template_string, jsonify
from google.cloud import translate_v3 as translate
import fitz  # PyMuPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

PROJECT_ID = 'ninth-cubist-465001-s2'  # <-- Replace with your Project ID
LOCATION = 'us-central1'  # or 'global'

client = translate.TranslationServiceClient()

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document Translator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { 
            box-sizing: border-box; 
            margin: 0; 
            padding: 0; 
        }
        
        html, body { 
            height: 100vh; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #000000;
            color: #ffffff;
            overflow-x: hidden;
        }
        
        body {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 16px;
        }
        
        .main-container {
            width: 100%;
            max-width: 480px;
            background: #000000;
            border: 1px solid #292929;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 4px 24px rgba(255, 255, 255, 0.05);
            position: relative;
        }
        
        .title {
            color: #ffffff;
            font-weight: 600;
            font-size: 24px;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        
        .subtitle {
            color: #767676;
            text-align: center;
            font-size: 14px;
            font-weight: 400;
            margin-bottom: 24px;
            line-height: 1.4;
        }
        
        .note-box {
            background: #292929;
            border: 1px solid #3d3d3d;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            color: #e5e5e5;
            font-size: 13px;
            line-height: 1.5;
        }
        
        .drag-area {
            border: 2px dashed #525252;
            border-radius: 12px;
            background: #292929;
            padding: 24px 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-bottom: 20px;
        }
        
        .drag-area:hover, .drag-area.dragover {
            border-color: #ffffff;
            background: #3d3d3d;
        }
        
        .drag-icon {
            font-size: 24px;
            color: #767676;
            margin-bottom: 12px;
            transition: color 0.2s ease;
        }
        
        .drag-area:hover .drag-icon {
            color: #ffffff;
        }
        
        .drag-text {
            color: #ffffff;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .drag-subtext {
            color: #767676;
            font-size: 12px;
        }
        
        .file-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
            margin-top: 12px;
            max-height: 60px;
            overflow-y: auto;
        }
        
        .file-badge {
            background: #3d3d3d;
            color: #ffffff;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 500;
            border: 1px solid #525252;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .form-control {
            border-radius: 8px;
            border: 1px solid #525252;
            background: #292929;
            color: #ffffff;
            padding: 12px 14px;
            font-size: 14px;
            font-weight: 400;
            transition: all 0.2s ease;
        }
        
        .form-control::placeholder {
            color: #767676;
        }
        
        .form-control:focus {
            background: #3d3d3d;
            border-color: #ffffff;
            box-shadow: none;
            color: #ffffff;
            outline: none;
        }
        
        .btn-primary {
            background: #ffffff;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 14px 20px;
            font-size: 14px;
            color: #000000;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .btn-primary:hover {
            background: #e5e5e5;
            color: #000000;
        }
        
        .btn-outline-secondary {
            border: 1px solid #525252;
            color: #ffffff;
            background: transparent;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 13px;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .btn-outline-secondary:hover {
            background: #292929;
            border-color: #767676;
            color: #ffffff;
        }
        
        .btn-success {
            background: #ffffff;
            border: none;
            border-radius: 8px;
            color: #000000;
            font-weight: 500;
            font-size: 13px;
            padding: 12px 16px;
            margin-bottom: 8px;
            transition: all 0.2s ease;
            width: 100%;
        }
        
        .btn-success:hover {
            background: #e5e5e5;
            color: #000000;
        }
        
        .alert {
            border-radius: 8px;
            border: none;
            font-size: 13px;
            font-weight: 500;
            padding: 12px 16px;
            margin-bottom: 12px;
        }
        
        .alert-success {
            background: #292929;
            color: #ffffff;
            border: 1px solid #525252;
        }
        
        .alert-warning {
            background: #3d3d3d;
            color: #ffffff;
            border: 1px solid #767676;
        }
        
        .alert-danger {
            background: #3d3d3d;
            color: #ffffff;
            border: 1px solid #767676;
        }
        
        .download-area {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .footer-text {
            color: #525252;
            font-size: 11px;
            text-align: center;
            margin-top: 20px;
            font-weight: 400;
        }
        
        .hide { display: none !important; }
        
        /* Custom scrollbar */
        .file-badges::-webkit-scrollbar, .download-area::-webkit-scrollbar {
            width: 4px;
        }
        .file-badges::-webkit-scrollbar-track, .download-area::-webkit-scrollbar-track {
            background: #292929;
            border-radius: 2px;
        }
        .file-badges::-webkit-scrollbar-thumb, .download-area::-webkit-scrollbar-thumb {
            background: #525252;
            border-radius: 2px;
        }
        
        /* Responsive - Ensure everything fits */
        @media (max-height: 700px) {
            body { align-items: flex-start; padding-top: 20px; }
            .main-container { margin-bottom: 20px; }
        }
        
        @media (max-width: 576px) {
            body { padding: 12px; }
            .main-container { 
                padding: 24px; 
                max-width: 100%;
                margin-bottom: 20px;
            }
            .title { font-size: 20px; }
            .drag-area { padding: 20px 12px; }
        }
        
        @media (max-height: 600px) {
            .main-container { padding: 20px; }
            .drag-area { padding: 16px 12px; }
            .note-box { padding: 12px; margin-bottom: 16px; }
            .subtitle { margin-bottom: 16px; }
        }
        
        /* Ensure download area is always visible */
        .download-area {
            max-height: calc(100vh - 500px);
            min-height: auto;
        }
        
        @media (max-height: 700px) {
            .download-area {
                max-height: 150px;
            }
        }
    </style>
</head>
<body>
<div class="main-container">
    <h1 class="title">
        Document Translator
    </h1>
    <p class="subtitle">
        AI-powered translation with perfect formatting preservation
    </p>
    
    <div class="note-box">
        <i class="fas fa-info-circle me-2"></i>
        <strong>Note:</strong> Upload DOCX for best table formatting. PDFs limited to 20 pages.
    </div>
    
    <form id="uploadForm" enctype="multipart/form-data">
        <div id="dropArea" class="drag-area">
            <input type="file" id="fileInput" name="file" accept=".pdf,.docx" class="d-none" multiple required>
            <div class="drag-icon">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <div class="drag-text">Drop files or click to browse</div>
            <div class="drag-subtext">PDF & DOCX • Max 5 files</div>
            <div id="fileBadges" class="file-badges"></div>
        </div>
        
        <div class="row g-2 mb-3">
            <div class="col">
                <input type="text" class="form-control" id="source_language" name="source_language" value="en" placeholder="From (e.g., en)" required>
            </div>
            <div class="col">
                <input type="text" class="form-control" id="target_language" name="target_language" value="hi" placeholder="To (e.g., hi)" required>
            </div>
        </div>
        
        <div class="d-grid gap-2">
            <button type="submit" id="translateBtn" class="btn btn-primary">
                <i class="fas fa-language me-2"></i>Translate Documents
            </button>
            <button type="button" id="resetBtn" class="btn btn-outline-secondary btn-sm hide">
                <i class="fas fa-redo me-2"></i>Clear All
            </button>
        </div>
    </form>
    
    <div id="statusArea" class="mt-3"></div>
    <div id="downloadArea" class="download-area mt-2"></div>
    
    <div class="footer-text">
        Powered by Google Cloud Translation API
    </div>
</div>

<!-- Loading Modal -->
<div class="modal fade" id="loadingModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content" style="background: #000000; border: 1px solid #525252; border-radius: 12px;">
            <div class="modal-body text-center p-4">
                <div class="spinner-border mb-3" style="width: 2.5rem; height: 2.5rem; color: #ffffff;" role="status"></div>
                <h5 class="fw-bold text-white mb-2">Translating Documents</h5>
                <p class="text-white-50 mb-0" style="color: #767676 !important;">Processing your files...</p>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const dropArea = document.getElementById('dropArea');
const fileInput = document.getElementById('fileInput');
const fileBadges = document.getElementById('fileBadges');
const resetBtn = document.getElementById('resetBtn');
const statusArea = document.getElementById('statusArea');
const downloadArea = document.getElementById('downloadArea');
const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'), {backdrop: 'static', keyboard: false});

dropArea.addEventListener('click', () => fileInput.click());
dropArea.addEventListener('dragover', e => { e.preventDefault(); dropArea.classList.add('dragover'); });
dropArea.addEventListener('dragleave', e => { e.preventDefault(); dropArea.classList.remove('dragover'); });
dropArea.addEventListener('drop', e => {
    e.preventDefault();
    dropArea.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        showFiles();
    }
});
fileInput.addEventListener('change', showFiles);

function showFiles() {
    fileBadges.innerHTML = '';
    if (fileInput.files.length) {
        for (let i = 0; i < Math.min(fileInput.files.length, 5); i++) {
            const badge = document.createElement('div');
            badge.className = 'file-badge';
            const icon = fileInput.files[i].name.toLowerCase().endsWith('.pdf') ? 'fa-file-pdf' : 'fa-file-word';
            badge.innerHTML = `<i class="fas ${icon}"></i>${fileInput.files[i].name}`;
            fileBadges.appendChild(badge);
        }
        resetBtn.classList.remove('hide');
    } else {
        resetBtn.classList.add('hide');
    }
}

resetBtn.onclick = function() {
    fileInput.value = '';
    fileBadges.innerHTML = '';
    statusArea.innerHTML = '';
    downloadArea.innerHTML = '';
    resetBtn.classList.add('hide');
}

document.getElementById('uploadForm').onsubmit = async function(e) {
    e.preventDefault();
    if (!fileInput.files.length) {
        statusArea.innerHTML = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i>Please select files to translate.</div>';
        return;
    }
    if (fileInput.files.length > 5) {
        statusArea.innerHTML = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i>Maximum 5 files allowed.</div>';
        return;
    }
    
    statusArea.innerHTML = '';
    downloadArea.innerHTML = '';
    loadingModal.show();
    
    let formData = new FormData();
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append('files', fileInput.files[i]);
    }
    formData.append('source_language', document.getElementById('source_language').value);
    formData.append('target_language', document.getElementById('target_language').value);
    
    try {
        const response = await fetch('/batch', {method: 'POST', body: formData});
        loadingModal.hide();
        
        if (response.ok) {
            const data = await response.json();
            if (data.downloads && data.downloads.length) {
                let html = '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i><strong>Translation Complete!</strong></div>';
                data.downloads.forEach(f => {
                    const icon = f.toLowerCase().includes('.pdf') ? 'fa-file-pdf' : 'fa-file-word';
                    html += `<a href="/download/${f}" class="btn btn-success" download><i class="fas ${icon} me-2"></i>${f.replace(/^translated_/, '')}</a>`;
                });
                html += '<button onclick="location.reload()" class="btn btn-outline-secondary mt-2"><i class="fas fa-plus me-2"></i>Translate More</button>';
                downloadArea.innerHTML = html;
            } else {
                statusArea.innerHTML = '<div class="alert alert-danger"><i class="fas fa-times-circle me-2"></i>No files were translated.</div>';
            }
        } else {
            const error = await response.text();
            statusArea.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>${error}</div>`;
        }
    } catch (err) {
        loadingModal.hide();
        statusArea.innerHTML = `<div class="alert alert-danger"><i class="fas fa-bug me-2"></i>Error: ${err.message}</div>`;
    }
}
</script>
</body>
</html>
'''

def get_mime_type(filename):
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        return 'application/pdf'
    elif ext == 'docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif ext == 'pptx':
        return 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    else:
        return 'application/octet-stream'

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/batch', methods=['POST'])
def batch_translate():
    files = request.files.getlist('files')
    src_lang = request.form.get('source_language', 'en')
    tgt_lang = request.form.get('target_language', 'hi')
    if not files:
        return "No files uploaded.", 400
    if len(files) > 5:
        return "You can upload up to 5 files at once.", 400
    downloads = []
    for file in files:
        filename = file.filename
        ext = filename.lower().split('.')[-1]
        if ext not in ['pdf', 'docx']:
            continue
        local_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_path)
        # For PDFs, check page count
        if ext == 'pdf':
            doc = fitz.open(local_path)
            if len(doc) > 20:
                continue  # Skip files over 20 pages
        try:
            with open(local_path, "rb") as document_file:
                document_input_config = {
                    "content": document_file.read(),
                    "mime_type": get_mime_type(filename)
                }
            response = client.translate_document(
                request={
                    "parent": f"projects/{PROJECT_ID}/locations/{LOCATION}",
                    "source_language_code": src_lang,
                    "target_language_code": tgt_lang,
                    "document_input_config": document_input_config,
                }
            )
            output_filename = f"translated_{filename}"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(output_path, "wb") as out:
                out.write(response.document_translation.byte_stream_outputs[0])
            downloads.append(output_filename)
        except Exception as e:
            continue  # Skip file on error
    if not downloads:
        return "No files were translated. (Check page limits and file types)", 400
    return jsonify({'downloads': downloads})

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
