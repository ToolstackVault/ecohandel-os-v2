# Agent Output Contracts

## Doel
Alle EcoHandel agents moeten in een vast, machineleesbaar en menselijk bruikbaar format communiceren.

---

## Algemene regels
- Kort, gestructureerd, geen wollige rapporten
- Elke run levert 3 blokken:
  1. `task_output`
  2. `run_notes`
  3. `learning_notes`
- `learning_notes` alleen vullen bij echte fouten, ruis, correcties of bewezen betere aanpak
- Jean beslist wat wordt gepromoveerd

---

## Scout Agent
### task_output
- new_topics[]
- source_summary[]
- urgent_signals[]

### verplichte velden per new_topics[]
- topic
- signal_type
- source
- search_intent
- commercial_relevance
- urgency
- confidence
- notes

---

## Strategist Agent
### task_output
- scored_topics[]
- top_5_recommendation[]
- watchlist[]
- killed[]

### verplichte velden per scored_topics[]
- topic
- priority_score
- content_type
- business_goal
- why_now
- recommended_next_step
- confidence

---

## Refresh Agent
### task_output
- refresh_candidates[]
- urgent_fixes[]

### verplichte velden per refresh_candidates[]
- url
- issue_type
- severity
- evidence
- recommended_fix
- priority
- confidence

---

## Writer Agent
### task_output
- brief_summary
- draft_path
- content_type
- assumptions[]
- open_questions[]

---

## Fact & Product Agent
### task_output
- checked_claims[]
- risk_flags[]
- approved_claims[]
- corrections[]
- confidence

---

## SERP Gap Agent
### task_output
- missing_pages[]
- competitor_patterns[]
- cluster_gaps[]
- opportunities[]

---

## Learning Notes format
Gebruik alleen als nodig:
- issue
- cause
- impact
- suggested_fix
- recurrence_risk

---

## Opslag
Aanbevolen locaties:
- `agents/scout/latest.json`
- `agents/strategist/latest.json`
- `agents/refresh/latest.json`
- `agents/logs/YYYY-MM-DD-<agent>.json`
