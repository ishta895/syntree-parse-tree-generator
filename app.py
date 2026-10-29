from flask import Flask, render_template, request, jsonify
from compiler_engine import LL1ParserEngine

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    grammar_text = data.get('grammar', '')
    input_text = data.get('input', '')

    if not grammar_text.strip():
        return jsonify({"error": "Please provide a valid Context-Free Grammar."}), 400

    try:
        engine = LL1ParserEngine(grammar_text)

        first_formatted = {k: sorted(list(v)) for k, v in engine.first.items() if k in engine.non_terminals}
        follow_formatted = {k: sorted(list(v)) for k, v in engine.follow.items()}

        table_formatted = {}
        for nt, row in engine.table.items():
            table_formatted[nt] = {t: " ".join(rhs) for t, rhs in row.items()}

        parse_result = engine.parse_input(input_text) if input_text.strip() else None

        return jsonify({
            "is_ll1": engine.is_ll1,
            "conflict_message": engine.conflict_message,
            "non_terminals": engine.non_terminals,
            "terminals": sorted(list(engine.terminals)),
            "first": first_formatted,
            "follow": follow_formatted,
            "table": table_formatted,
            "parse_result": parse_result
        })
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)