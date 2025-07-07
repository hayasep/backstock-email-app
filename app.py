from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Backstock Email Generator</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        textarea { width: 100%; height: 200px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #999; padding: 8px; text-align: left; }
        .email-preview { background: #f4f4f4; padding: 15px; margin-top: 20px; white-space: pre-wrap; }
        button { padding: 10px 20px; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Backstock Email Generator</h2>
    <form method="post">
        <textarea name="raw_text" placeholder="Paste your backstock/push message here">{{ raw_text }}</textarea>
        <br>
        <button type="submit">Generate Email Table</button>
    </form>

    {% if table_html %}
    <div class="email-preview">
        <strong>Subject:</strong> Backstock Report – {{ date }}<br><br>
        {{ table_html|safe }}
    </div>
    {% endif %}
</body>
</html>
"""

def parse_text_to_table(raw_text):
    sections = re.split(r'\n\s*\n', raw_text.strip())
    rows = []

    for section in sections:
        lines = section.strip().split('\n')
        if not lines: continue
        category = lines[0].strip(':')
        for line in lines[1:]:
            if ' - ' in line:
                section_name, leftover = map(str.strip, line.split(' - ', 1))
                rows.append((category, section_name, leftover))

    if not rows:
        return ""

    table = '<table><tr><th>Category</th><th>Section</th><th>Leftover</th></tr>'
    for cat, sec, left in rows:
        table += f'<tr><td>{cat}</td><td>{sec}</td><td>{left}</td></tr>'
    table += '</table>'
    return table

from datetime import datetime

@app.route('/', methods=['GET', 'POST'])
def index():
    table_html = ""
    raw_text = ""
    if request.method == 'POST':
        raw_text = request.form.get('raw_text', '')
        table_html = parse_text_to_table(raw_text)
    date = datetime.now().strftime('%b %d, %Y')
    return render_template_string(HTML_TEMPLATE, table_html=table_html, raw_text=raw_text, date=date)

if __name__ == '__main__':
    app.run(debug=True)
