import random


class Grammar:
    """
    Represents a formal Regular Grammar defined by the tuple {V_N, V_T, P, S}.

    Variant 2:
        VN = {S, R, L}
        VT = {a, b, c, d, e, f}
        P  = {
            S → aS | bS | cR | dL
            R → dL | e
            L → fL | eL | d
        }
    """

    def __init__(self, vn: set, vt: set, productions: dict, start: str):
        """
        Args:
            vn:          Set of non-terminal symbols, e.g. {'S', 'R', 'L'}
            vt:          Set of terminal symbols,     e.g. {'a','b','c','d','e','f'}
            productions: Dict mapping each non-terminal to a list of right-hand sides.
                         Each RHS is a string where uppercase = non-terminal, lowercase = terminal.
                         e.g. {'S': ['aS', 'bS', 'cR', 'dL'], ...}
            start:       The start symbol, e.g. 'S'
        """
        self.vn = vn
        self.vt = vt
        self.productions = productions
        self.start = start

    def generate_string(self) -> str:
        """
        Randomly derives a string from the grammar by repeatedly replacing
        the current non-terminal with one of its productions until no
        non-terminal remains (i.e. a terminal-only string is produced).

        Returns:
            A valid string belonging to the language L(G).
        """
        current = self.start          # begin at the start symbol

        while True:
            # Find the first non-terminal character still present in current
            nt = None
            for ch in current:
                if ch in self.vn:
                    nt = ch
                    break

            if nt is None:
                # No non-terminals left → we have a complete terminal string
                break

            # Pick a random production for that non-terminal and apply it
            chosen_rhs = random.choice(self.productions[nt])
            # Replace only the FIRST occurrence of this non-terminal
            current = current.replace(nt, chosen_rhs, 1)

        return current

    def to_finite_automaton(self):
        """
        Converts this regular grammar to an equivalent Finite Automaton.

        For a right-linear grammar the conversion rules are:
          • Each non-terminal  →  a state
          • A new accepting state  'X'  is added (represents successful termination)
          • Production  A → aB   adds transition  δ(A, a) = B
          • Production  A → a    adds transition  δ(A, a) = X   (terminal production)
          • The start state is the grammar's start symbol
          • The only accepting state is  'X'

        Returns:
            A FiniteAutomaton object equivalent to this grammar.
        """
        from finite_automaton import FiniteAutomaton

        # States = one per non-terminal + one extra accepting state
        accepting_state = "X"
        states = self.vn | {accepting_state}

        transitions = {}   # { (state, symbol): next_state }

        for non_terminal, rules in self.productions.items():
            for rhs in rules:
                if len(rhs) == 1:
                    # A → a  (pure terminal) → go to accepting state
                    terminal = rhs[0]
                    transitions[(non_terminal, terminal)] = accepting_state

                elif len(rhs) == 2:
                    # A → aB  (terminal + non-terminal)
                    terminal, next_state = rhs[0], rhs[1]
                    transitions[(non_terminal, terminal)] = next_state

                else:
                    raise ValueError(
                        f"Production '{non_terminal} → {rhs}' is not in right-linear form "
                        "(expected length 1 or 2)."
                    )

        return FiniteAutomaton(
            states=states,
            alphabet=self.vt,
            transitions=transitions,
            start_state=self.start,
            accept_states={accepting_state},
        )

    def classify_chomsky(self) -> str:
        """
        Classifies the grammar according to the Chomsky hierarchy:

          Type 3 - Regular:
            Every production is of the form  A -> a  or  A -> aB  (right-linear),
            where A, B in VN and a in VT.

          Type 2 - Context-Free:
            Every production has a single non-terminal on the left-hand side.

          Type 1 - Context-Sensitive:
            Every production satisfies |rhs| >= |lhs| (no shrinking rules).

          Type 0 - Unrestricted:
            No constraints.

        Returns:
            A string describing the grammar type, e.g. 'Type 3 (Regular)'.
        """
        is_type3 = True
        is_type2 = True
        is_type1 = True

        for lhs, rules in self.productions.items():
            for rhs in rules:
                # Type 2 check: LHS must be a single non-terminal
                if len(lhs) != 1 or lhs not in self.vn:
                    is_type3 = False
                    is_type2 = False

                # Type 1 check: |rhs| >= |lhs|
                if len(rhs) < len(lhs):
                    is_type3 = False
                    is_type2 = False
                    is_type1 = False

                # Type 3 check: RHS must be  a  or  aB  (right-linear)
                # Non-terminals may be multi-char names (e.g. Q1, Q3),
                # so split off first char as terminal, rest as non-terminal.
                if is_type3:
                    if rhs in self.vt:
                        pass   # A -> a
                    elif len(rhs) > 1 and rhs[0] in self.vt and rhs[1:] in self.vn:
                        pass   # A -> aB
                    else:
                        is_type3 = False

        if is_type3:
            return "Type 3 (Regular)"
        elif is_type2:
            return "Type 2 (Context-Free)"
        elif is_type1:
            return "Type 1 (Context-Sensitive)"
        else:
            return "Type 0 (Unrestricted)"

    def __repr__(self) -> str:
        rules = []
        for nt, rhss in self.productions.items():
            for rhs in rhss:
                rules.append(f"  {nt} → {rhs}")
        return (
            f"Grammar(\n"
            f"  VN={self.vn},\n"
            f"  VT={self.vt},\n"
            f"  S='{self.start}',\n"
            f"  Productions=[\n" + "\n".join(rules) + "\n  ]\n)"
        )
