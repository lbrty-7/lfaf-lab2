from grammar import Grammar
from finite_automaton import FiniteAutomaton

SEP = "=" * 60

# -----------------------------------------------------------------------
# Lab 1 grammar (Variant 2)
# -----------------------------------------------------------------------
grammar = Grammar(
    vn={"S", "R", "L"},
    vt={"a", "b", "c", "d", "e", "f"},
    productions={
        "S": ["aS", "bS", "cR", "dL"],
        "R": ["dL", "e"],
        "L": ["fL", "eL", "d"],
    },
    start="S",
)

print(SEP)
print("LAB 1 GRAMMAR — Chomsky Classification")
print(SEP)
print(grammar)
print(f"\n  Classification: {grammar.classify_chomsky()}")

print("\n" + SEP)
print("GENERATED STRINGS (Lab 1 grammar)")
print(SEP)
for i in range(5):
    print(f"  String {i+1}: '{grammar.generate_string()}'")

# -----------------------------------------------------------------------
# Lab 2 — Variant 2 NDFA
#
# Q  = {q0, q1, q2, q3, q4}
# Σ  = {a, b, c}
# F  = {q4}
# δ(q0,a) = q1
# δ(q1,b) = q2  }  same (state, symbol) -> two destinations = NDFA
# δ(q1,b) = q3  }
# δ(q2,c) = q3
# δ(q3,a) = q3
# δ(q3,b) = q4
# -----------------------------------------------------------------------
ndfa = FiniteAutomaton(
    states={"q0", "q1", "q2", "q3", "q4"},
    alphabet={"a", "b", "c"},
    transitions={
        ("q0", "a"): {"q1"},
        ("q1", "b"): {"q2", "q3"},   # <-- non-deterministic
        ("q2", "c"): {"q3"},
        ("q3", "a"): {"q3"},
        ("q3", "b"): {"q4"},
    },
    start_state="q0",
    accept_states={"q4"},
)

print("\n" + SEP)
print("LAB 2 — NDFA (Variant 2)")
print(SEP)
print(ndfa)

# -----------------------------------------------------------------------
# Task 3b — Determinism check
# -----------------------------------------------------------------------
print("\n" + SEP)
print("DETERMINISM CHECK")
print(SEP)
det = ndfa.is_deterministic()
print(f"  Is deterministic? {'Yes (DFA)' if det else 'No (NDFA)'}")
print("  Reason: delta(q1, b) = {q2, q3} — two targets for one (state, symbol) pair.")

# -----------------------------------------------------------------------
# Task 3a — FA -> Regular Grammar
# -----------------------------------------------------------------------
print("\n" + SEP)
print("FA -> REGULAR GRAMMAR")
print(SEP)
converted_grammar = ndfa.to_regular_grammar()
print(converted_grammar)
print(f"\n  Chomsky classification: {converted_grammar.classify_chomsky()}")

# -----------------------------------------------------------------------
# Task 3c — NDFA -> DFA  (subset construction)
# -----------------------------------------------------------------------
print("\n" + SEP)
print("NDFA -> DFA  (subset construction)")
print(SEP)
dfa = ndfa.to_dfa()
print(dfa)
print(f"\n  Is the result deterministic? {'Yes' if dfa.is_deterministic() else 'No'}")

# -----------------------------------------------------------------------
# Membership tests — NDFA and DFA must always agree
#
# Valid strings follow the pattern:  a b (a* | c) a* b
#   abb    : q0-a->q1-b->{q2,q3}  from q3: b->q4          TRUE
#   abab   : q0-a->q1-b->q3-a->q3-b->q4                   TRUE
#   abaab  : q0-a->q1-b->q3-a->q3-a->q3-b->q4             TRUE
#   abcb   : q0-a->q1-b->q2-c->q3-b->q4                   TRUE
#   abcab  : q0-a->q1-b->q2-c->q3-a->q3-b->q4             TRUE
# -----------------------------------------------------------------------
print("\n" + SEP)
print("STRING MEMBERSHIP TESTS  (NDFA vs DFA — must agree)")
print(SEP)

tests = [
    ("abb",   True),   # shortest accepting path via q3 branch
    ("abab",  True),   # loop once on a in q3 then terminate
    ("abaab", True),   # loop twice on a in q3
    ("abcb",  True),   # go through q2 branch
    ("abcab", True),   # q2 branch + a-loop in q3
    ("ab",    False),  # ends in {q2,q3}, neither is accepting
    ("a",     False),  # ends in q1
    ("b",     False),  # no transition from q0 on b
    ("abc",   False),  # ends in q3, not accepting
    ("",      False),  # q0 not accepting
    ("abbb",  False),  # after abb reaches q4, then b has no transition from q4
]

print(f"  {'String':<12} {'Expected':>10} {'NDFA':>8} {'DFA':>8} {'OK?':>6}")
print(f"  {'-'*12} {'-'*10} {'-'*8} {'-'*8} {'-'*6}")
all_ok = True
for s, expected in tests:
    ndfa_res = ndfa.string_belongs_to_language(s)
    dfa_res  = dfa.string_belongs_to_language(s)
    match = ndfa_res == dfa_res == expected
    all_ok = all_ok and match
    flag = "YES" if match else "FAIL"
    print(f"  {s!r:<12} {str(expected):>10} {str(ndfa_res):>8} {str(dfa_res):>8} {flag:>6}")

print(f"\n  All tests passed: {all_ok}")
