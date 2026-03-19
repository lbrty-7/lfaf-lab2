# Laboratory Work 2 — Determinism in Finite Automata. NDFA to DFA. Chomsky Hierarchy.

**Course:** Formal Languages & Finite Automata  
**Student:** Vladimir Buliga  
**Variant:** 2  
**Date:** February 2026

---

## Theory

### Determinism vs Non-Determinism

A **Deterministic Finite Automaton (DFA)** is one where for every state `q` and every input symbol `a`, there is at most one possible next state. Formally, the transition function is `δ: Q × Σ → Q`.

A **Non-Deterministic Finite Automaton (NDFA)** relaxes this constraint: a single `(state, symbol)` pair may lead to multiple states simultaneously. The transition function becomes `δ: Q × Σ → 2^Q`. Despite this apparent extra power, NDFAs and DFAs recognize exactly the same class of languages — the regular languages.

### Chomsky Hierarchy

| Type | Name | Production Form |
|------|------|----------------|
| 0 | Unrestricted | `α → β` (no restriction) |
| 1 | Context-Sensitive | `\|β\| ≥ \|α\|` |
| 2 | Context-Free | `A → γ` (single non-terminal on LHS) |
| 3 | Regular | `A → a` or `A → aB` (right-linear) |

### Subset Construction (NDFA → DFA)

Each DFA state represents a *set* of NDFA states that could be active simultaneously. Starting from `{q0}`, for each input symbol, the next DFA state is the union of all NDFA states reachable from any state in the current set. A DFA state is accepting if it contains at least one NDFA accepting state.

---

## Objectives

1. Add `classify_chomsky()` to the `Grammar` class
2. Implement `to_regular_grammar()` on `FiniteAutomaton`
3. Implement `is_deterministic()` on `FiniteAutomaton`
4. Implement `to_dfa()` using subset construction

---

## Variant 2 — NDFA Definition
```
Q  = {q0, q1, q2, q3, q4}
Σ  = {a, b, c}
F  = {q4}
δ(q0, a) = q1
δ(q1, b) = q2    ← same state, same symbol
δ(q1, b) = q3    ← two different targets → NON-DETERMINISTIC
δ(q2, c) = q3
δ(q3, a) = q3
δ(q3, b) = q4
```

---

## Implementation

### `classify_chomsky()`

Uses three boolean flags (`is_type3`, `is_type2`, `is_type1`) checked from most to least restrictive. For Type 3, each RHS must be either a single terminal or a terminal followed by a non-terminal. Non-terminal names may be multi-character (e.g. `Q1`), so the check compares `rhs[0]` against `V_T` and `rhs[1:]` against `V_N` as a whole token.

### `to_regular_grammar()`

Reverses the Lab 1 conversion: transition `δ(A, a) = B` → production `A → aB`. If `B` is accepting, also adds `A → a`. The start state maps to non-terminal `S`.

### `is_deterministic()`

Checks whether any transition value is a set with more than one element. Returns `False` for this NDFA because `("q1", "b")` maps to `{"q2", "q3"}`.

### `to_dfa()` — Subset Construction
```
1. Start with DFA state {q0}
2. For each unvisited DFA state S and each symbol a:
       next = union of δ(s, a) for all s in S
       add transition (S, a) → next
3. A DFA state is accepting if it contains any NDFA accepting state
4. Repeat until no unvisited states remain
```

---

## Results

### NDFA → DFA

| NDFA states | DFA state | Accepting? |
|-------------|-----------|------------|
| `{q0}` | `{q0}` | No |
| `{q1}` | `{q1}` | No |
| `{q2, q3}` | `{q2,q3}` | No |
| `{q3}` | `{q3}` | No |
| `{q4}` | `{q4}` | Yes |

DFA transitions:
```
δ({q0},    a) = {q1}
δ({q1},    b) = {q2,q3}
δ({q2,q3}, a) = {q3}
δ({q2,q3}, b) = {q4}
δ({q2,q3}, c) = {q3}
δ({q3},    a) = {q3}
δ({q3},    b) = {q4}
```

### Membership Tests (NDFA vs DFA — all agree)

| String | Expected | NDFA | DFA |
|--------|----------|------|-----|
| `abb` | ✓ | True | True |
| `abab` | ✓ | True | True |
| `abcb` | ✓ | True | True |
| `ab` | ✗ | False | False |
| `abc` | ✗ | False | False |
| `""` | ✗ | False | False |

---

## Conclusions

This lab deepened the understanding of finite automata by confronting the distinction between determinism and non-determinism. The subset construction elegantly resolves non-determinism by treating sets of NDFA states as first-class DFA states — the non-determinism is not eliminated but folded into the state space. A key observation is that the resulting DFA had the same number of states as the NDFA, which is the best case; in general, subset construction can produce up to `2^n` states. The Chomsky classification confirmed that the Lab 1 grammar is Type 3, consistent with it being equivalent to a finite automaton.
