function loadSampleGrammar() {
    document.getElementById('grammarInput').value =
        `E -> T E'
E' -> + T E' | epsilon
T -> id`;
    document.getElementById('stringInput').value = "id + id";
}

async function executeAnalysis() {
    const grammar = document.getElementById('grammarInput').value;
    const inputStr = document.getElementById('stringInput').value;
    const statusBadge = document.getElementById('statusBadge');
    const outputContainer = document.getElementById('outputContainer');

    statusBadge.className = 'status-indicator';
    statusBadge.innerText = 'Analyzing Grammar...';

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grammar, input: inputStr })
        });
        const data = await res.json();

        if (!res.ok) {
            statusBadge.className = 'status-indicator error';
            statusBadge.innerText = data.error || 'Syntax error in grammar';
            return;
        }

        outputContainer.classList.remove('hidden');

        if (data.parse_result && data.parse_result.accepted) {
            statusBadge.className = 'status-indicator success';
            statusBadge.innerText = 'String Accepted & Parse Tree Generated!';
        } else if (data.parse_result) {
            statusBadge.className = 'status-indicator error';
            statusBadge.innerText = data.parse_result.error || 'String Rejected';
        } else {
            statusBadge.className = 'status-indicator ready';
            statusBadge.innerText = 'Grammar compiled. Enter input string to parse.';
        }

        renderFirstFollow(data.first, data.follow);
        renderTable(data.non_terminals, data.terminals, data.table);

        if (data.parse_result) {
            renderTrace(data.parse_result.steps);
            if (data.parse_result.tree) {
                drawParseTree(data.parse_result.tree);
            }
        }
    } catch (err) {
        statusBadge.className = 'status-indicator error';
        statusBadge.innerText = 'Network error: ' + err.message;
    }
}

function renderFirstFollow(first, follow) {
    const grid = document.getElementById('firstFollowGrid');
    grid.innerHTML = '';
    for (const nt of Object.keys(first)) {
        const card = document.createElement('div');
        card.style = 'background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; font-family: monospace; font-size: 0.85rem; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 6px;';
        card.innerHTML = `<strong>${nt}</strong><br>FIRST = { ${first[nt].join(', ')} }<br>FOLLOW = { ${follow[nt].join(', ')} }`;
        grid.appendChild(card);
    }
}

function renderTable(nts, terminals, table) {
    const t = document.getElementById('parsingTable');
    const validTerms = terminals.filter(x => x !== 'epsilon');
    let html = `<thead><tr><th>Non-Terminal</th>${validTerms.map(x => `<th>${x}</th>`).join('')}</tr></thead><tbody>`;

  for (const nt of nts) {
    html += `<tr><td><strong>${nt}</strong></td>`;
    for (const term of validTerms) {
      const prod = table[nt] && table[nt][term] ? `${nt} -> ${table[nt][term]}` : '—';
      html += `<td>${prod}</td>`;
    }
    html += `</tr>`;
  }
  html += `</tbody>`;
  t.innerHTML = html;
}

function renderTrace(steps) {
  const tbody = document.querySelector('#traceTable tbody');
  tbody.innerHTML = '';
  steps.forEach((step, idx) => {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${idx + 1}</td><td><code>${step.stack}</code></td><td><code>${step.input}</code></td><td>${step.action}</td>`;
    tbody.appendChild(row);
  });
}

function drawParseTree(treeData) {
  const canvas = document.getElementById('treeCanvas');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  let leafIndex = 0;
  function computePositions(node, depth) {
    if (!node.children || node.children.length === 0) {
      node.x = 80 + leafIndex * 90;
      node.y = 60 + depth * 70;
      leafIndex++;
      return;
    }
    node.children.forEach(c => computePositions(c, depth + 1));
    const firstX = node.children[0].x;
    const lastX = node.children[node.children.length - 1].x;
    node.x = (firstX + lastX) / 2;
    node.y = 60 + depth * 70;
  }

  computePositions(treeData, 0);

  function drawEdges(node) {
    if (!node.children) return;
    for (const child of node.children) {
      ctx.beginPath();
      ctx.moveTo(node.x, node.y);
      ctx.lineTo(child.x, child.y);
      ctx.strokeStyle = '#4B5563';
      ctx.lineWidth = 2;
      ctx.stroke();
      drawEdges(child);
    }
  }

  function drawNodes(node) {
    ctx.beginPath();
    ctx.arc(node.x, node.y, 18, 0, 2 * Math.PI);
    ctx.fillStyle = node.children && node.children.length > 0 ? '#4F46E5' : '#10B981';
    ctx.fill();
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 12px JetBrains Mono';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(node.name, node.x, node.y);

    if (node.children) {
      node.children.forEach(drawNodes);
    }
  }

  drawEdges(treeData);
  drawNodes(treeData);
}