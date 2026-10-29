from collections import defaultdict
import re

class ParseTreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []

    def to_dict(self):
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children]
        }

class LL1ParserEngine:
    def __init__(self, raw_grammar):
        self.raw_grammar = raw_grammar
        self.productions = [] # List of (LHS, [RHS symbols])
        self.non_terminals = []
        self.terminals = set()
        self.start_symbol = None
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.table = {}
        self.is_ll1 = True
        self.conflict_message = ""
        self._parse_grammar()
        self._compute_first()
        self._compute_follow()
        self._build_table()

    def _parse_grammar(self):
        # Normalize arrows like '->', '→', and separators
        lines = [line.strip() for line in self.raw_grammar.strip().split('\n') if line.strip()]
        for line in lines:
            normalized = line.replace('→', '->').replace('::=', '->')
            if '->' not in normalized:
                continue
            lhs, rhs_all = normalized.split('->', 1)
            lhs = lhs.strip()
            if not lhs:
                continue
            if not self.start_symbol:
                self.start_symbol = lhs
            if lhs not in self.non_terminals:
                self.non_terminals.append(lhs)

            alternatives = rhs_all.split('|')
            for alt in alternatives:
                symbols = alt.strip().split()
                if not symbols:
                    symbols = ['epsilon']
                # Normalize eps / epsilon / ε
                symbols = ['epsilon' if s in ['ε', 'eps', 'null', 'λ'] else s for s in symbols]
                self.productions.append((lhs, symbols))

        if not self.non_terminals:
            raise ValueError("No valid grammar productions found.")

        all_symbols = set()
        for lhs, rhs in self.productions:
            for sym in rhs:
                all_symbols.add(sym)
        self.terminals = {s for s in all_symbols if s not in self.non_terminals and s != 'epsilon'}
        self.terminals.add('$')

    def _compute_first(self):
        for t in self.terminals:
            self.first[t] = {t}
        self.first['epsilon'] = {'epsilon'}

        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.productions:
                cur_first = self._first_of_sequence(rhs)
                before_size = len(self.first[lhs])
                self.first[lhs].update(cur_first)
                if len(self.first[lhs]) > before_size:
                    changed = True

    def _first_of_sequence(self, symbols):
        result = set()
        for sym in symbols:
            sym_first = self.first.get(sym, {sym})
            result.update(sym_first - {'epsilon'})
            if 'epsilon' not in sym_first:
                break
        else:
            result.add('epsilon')
        return result

    def _compute_follow(self):
        self.follow[self.start_symbol].add('$')
        changed = True
        while changed:
            changed = False
            for lhs, rhs in self.productions:
                for i, sym in enumerate(rhs):
                    if sym in self.non_terminals:
                        follow_addition = self._first_of_sequence(rhs[i+1:])
                        before_len = len(self.follow[sym])
                        self.follow[sym].update(follow_addition - {'epsilon'})

                        if 'epsilon' in follow_addition or i + 1 == len(rhs):
                            self.follow[sym].update(self.follow[lhs])

                        if len(self.follow[sym]) > before_len:
                            changed = True

    def _build_table(self):
        for nt in self.non_terminals:
            self.table[nt] = {}

        for idx, (lhs, rhs) in enumerate(self.productions):
            first_rhs = self._first_of_sequence(rhs)
            for terminal in first_rhs - {'epsilon'}:
                if terminal in self.table[lhs]:
                    self.is_ll1 = False
                    self.conflict_message = f"Conflict detected at M[{lhs}, {terminal}]"
                self.table[lhs][terminal] = rhs

            if 'epsilon' in first_rhs:
                for terminal in self.follow[lhs]:
                    if terminal in self.table[lhs]:
                        self.is_ll1 = False
                        self.conflict_message = f"Conflict detected at M[{lhs}, {terminal}]"
                    self.table[lhs][terminal] = rhs

    def parse_input(self, input_string):
        tokens = input_string.strip().split()
        tokens.append('$')

        stack = ['$', self.start_symbol]
        root = ParseTreeNode(self.start_symbol)
        node_stack = [None, root]

        steps = []
        token_idx = 0
        accepted = False
        error_msg = ""
        max_steps = 1000
        step_count = 0

        while len(stack) > 0 and step_count < max_steps:
            step_count += 1
            top = stack[-1]
            curr_token = tokens[token_idx] if token_idx < len(tokens) else '$'

            stack_str = " ".join(stack)
            input_str = " ".join(tokens[token_idx:])

            if top == curr_token:
                if top == '$':
                    steps.append({"stack": stack_str, "input": input_str, "action": "Accept"})
                    stack.pop()
                    node_stack.pop()
                    accepted = True
                    break
                else:
                    steps.append({"stack": stack_str, "input": input_str, "action": f"Match '{curr_token}'"})
                    stack.pop()
                    node_stack.pop()
                    token_idx += 1
            elif top in self.terminals or top == '$':
                error_msg = f"Syntax Error: Expected '{top}', found '{curr_token}'"
                steps.append({"stack": stack_str, "input": input_str, "action": f"Error: {error_msg}"})
                break
            else:
                if curr_token in self.table[top]:
                    rhs = self.table[top][curr_token]
                    rule_str = f"{top} -> {' '.join(rhs)}"
                    steps.append({"stack": stack_str, "input": input_str, "action": f"Apply {rule_str}"})

                    stack.pop()
                    parent_node = node_stack.pop()

                    if rhs == ['epsilon']:
                        child = ParseTreeNode("ε")
                        parent_node.children.append(child)
                    else:
                        child_nodes = [ParseTreeNode(s) for s in rhs]
                        parent_node.children.extend(child_nodes)
                        for s, node in zip(reversed(rhs), reversed(child_nodes)):
                            stack.append(s)
                            node_stack.append(node)
                else:
                    error_msg = f"Syntax Error: No valid transition for M[{top}, {curr_token}]"
                    steps.append({"stack": stack_str, "input": input_str, "action": f"Error: {error_msg}"})
                    break

        if step_count >= max_steps:
            error_msg = "Parse terminated: Infinite loop detected or exceeded step limit."

        return {
            "accepted": accepted,
            "error": error_msg,
            "steps": steps,
            "tree": root.to_dict() if accepted else None
        }