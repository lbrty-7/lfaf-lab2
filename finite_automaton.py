class FiniteAutomaton:
    """
    Represents a Finite Automaton (deterministic OR non-deterministic)
    defined by the tuple {Q, Sigma, delta, q0, F}.

    For a DFA:  transitions = { (state, symbol): "next_state" }
    For an NDFA: transitions = { (state, symbol): {"next_state1", "next_state2", ...} }
    """

    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def _get_next_states(self, state, symbol) -> set:
        """Normalise transition target to a set (works for both DFA and NDFA)."""
        value = self.transitions.get((state, symbol))
        if value is None:
            return set()
        if isinstance(value, set):
            return value
        return {value}

    # ------------------------------------------------------------------
    # 1. String membership  (DFA + NDFA)
    # ------------------------------------------------------------------
    def string_belongs_to_language(self, input_string: str) -> bool:
        """
        Simulates the automaton using subset tracking so it handles
        both DFA and NDFA transparently.
        Returns True if any active state at the end is accepting.
        """
        current_states = {self.start_state}

        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            next_states = set()
            for state in current_states:
                next_states |= self._get_next_states(state, symbol)
            if not next_states:
                return False
            current_states = next_states

        return bool(current_states & self.accept_states)

    # ------------------------------------------------------------------
    # 2. FA -> Regular Grammar
    # ------------------------------------------------------------------
    def to_regular_grammar(self):
        """
        Converts this FA to an equivalent right-linear Regular Grammar.

          - Each state becomes a non-terminal (start state -> 'S')
          - delta(A, a) = B  ->  A -> aB
          - If B is accepting: also add  A -> a
          - If the start state is accepting: add  S -> '' (epsilon)
        """
        from grammar import Grammar

        def state_to_nt(state):
            return "S" if state == self.start_state else state.upper()

        vn = {state_to_nt(s) for s in self.states}
        vt = set(self.alphabet)
        productions = {nt: [] for nt in vn}
        start = state_to_nt(self.start_state)

        for (state, symbol), targets in self.transitions.items():
            nt_from = state_to_nt(state)
            if isinstance(targets, str):
                targets = {targets}

            for target in targets:
                nt_to = state_to_nt(target)
                productions[nt_from].append(symbol + nt_to)   # A -> aB
                if target in self.accept_states:
                    productions[nt_from].append(symbol)        # A -> a

        if self.start_state in self.accept_states:
            productions[start].append("")   # epsilon

        productions = {k: v for k, v in productions.items() if v}
        return Grammar(vn=vn, vt=vt, productions=productions, start=start)

    # ------------------------------------------------------------------
    # 3. Is deterministic?
    # ------------------------------------------------------------------
    def is_deterministic(self) -> bool:
        """
        Returns True (DFA) if every (state, symbol) maps to at most one state.
        Returns False (NDFA) if any (state, symbol) maps to multiple states.
        """
        for (state, symbol), targets in self.transitions.items():
            if isinstance(targets, set) and len(targets) > 1:
                return False
        return True

    # ------------------------------------------------------------------
    # 4. NDFA -> DFA  (subset / powerset construction)
    # ------------------------------------------------------------------
    def to_dfa(self):
        """
        Converts this NDFA to an equivalent DFA using subset construction.

        Each DFA state = a frozenset of NDFA states.
        Start state    = {ndfa_start_state}
        Accepting      = any DFA state containing an NDFA accepting state.
        """
        start_set = frozenset({self.start_state})
        unvisited = [start_set]
        visited = set()

        dfa_transitions = {}
        dfa_states = set()
        dfa_accept = set()

        while unvisited:
            current_set = unvisited.pop()
            if current_set in visited:
                continue
            visited.add(current_set)
            dfa_states.add(current_set)

            if current_set & self.accept_states:
                dfa_accept.add(current_set)

            for symbol in self.alphabet:
                reachable = set()
                for ndfa_state in current_set:
                    reachable |= self._get_next_states(ndfa_state, symbol)

                if not reachable:
                    continue  # dead state — omit for cleanliness

                next_set = frozenset(reachable)
                dfa_transitions[(current_set, symbol)] = next_set

                if next_set not in visited:
                    unvisited.append(next_set)

        def fmt(fs):
            return "{" + ",".join(sorted(fs)) + "}"

        return FiniteAutomaton(
            states={fmt(s) for s in dfa_states},
            alphabet=self.alphabet,
            transitions={(fmt(s), sym): fmt(t) for (s, sym), t in dfa_transitions.items()},
            start_state=fmt(start_set),
            accept_states={fmt(s) for s in dfa_accept},
        )

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        trans_lines = "\n".join(
            f"    delta({str(state)!r}, {sym!r}) = {str(next_s)!r}"
            for (state, sym), next_s in sorted(
                self.transitions.items(), key=lambda x: (str(x[0][0]), x[0][1])
            )
        )
        return (
            f"FiniteAutomaton(\n"
            f"  Q     = {sorted(self.states)},\n"
            f"  Sigma = {sorted(self.alphabet)},\n"
            f"  q0    = '{self.start_state}',\n"
            f"  F     = {self.accept_states},\n"
            f"  delta =\n{trans_lines}\n)"
        )
