from flask import Flask, render_template_string
import sqlite3
import pandas as pd

app = Flask(__name__)

HTML = """
<h2>👑 Admin Dashboard</h2>
<table border="1">
<tr><th>Name</th><th>Action</th><th>Minutes</th><th>Time</th></tr>
{% for row in data %}
<tr>
<td>{{row[2]}}</td>
<td>{{row[3]}}</td>
<td>{{row[4]}}</td>
<td>{{row[5]}}</td>
</tr>
{% endfor %}
</table>
"""

@app.route("/")
def home():
    conn = sqlite3.connect("office.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 50")
    data = cursor.fetchall()
    conn.close()
    return render_template_string(HTML, data=data)

@app.route("/export")
def export():
    conn = sqlite3.connect("office.db")
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    df.to_excel("report.xlsx", index=False)
    return "Excel exported!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
