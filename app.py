from flask import Flask, request, render_template_string
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Backstock Email Generator (AI)</title>
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
    <h2>Backstock Email Generator (AI)</h2>
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

def parse_text_to_table_ai(raw_text):
    prompt = f"""
You are a helpful assistant. Convert the following text into an HTML table with three columns: Category, Section, and Leftover.

- The input is a list of leftover stock and push items, categorized by location (like 'upstairs backstock', 'downstairs push', etc.).
- Each item line includes a section name and leftover type/count (like 'hba 5 carts' or 'CD 1 furniture pallet').
- Use the last section header as the 'Category' for the following lines.
- Format the result in clean HTML using <table>, <tr>, and <td>.

Text:
{raw_text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"<p style='color:red;'>Error generating table: {e}</p>"

@app.route('/', methods=['GET', 'POST'])
def index():
    table_html = ""
    raw_text = ""
    if request.method == 'POST':
        raw_text = request.form.get('raw_text', '')
        table_html = parse_text_to_table_ai(raw_text)
    date = datetime.now().strftime('%b %d, %Y')
    return render_template_string(HTML_TEMPLATE, table_html=table_html, raw_text=raw_text, date=date)

if __name__ == '__main__':
    app.run(debug=True)
