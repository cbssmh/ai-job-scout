# Scoring System

The recommendation score is designed to be easy to inspect and test. The active API path uses `app/scoring/recommendation_scorer.py`.

## Purpose

The score ranks already-analyzed jobs against a user profile. It is not an LLM-generated judgment. It is a deterministic calculation from extracted job fields and user inputs.

## Inputs

`RecommendationScorer.score()` receives:

- `RecommendationContext`: job id, title, company, location, role, tech stack, language requirement, and visa sponsorship.
- `RecommendationRequest`: user skills, preferred countries, and whether the user needs visa sponsorship.

## Skill Score

Skill matching is delegated to `calculate_match_score()` in `app/agents/skill_matcher.py`.

Current behavior:

1. Split `context.tech_stack` by comma.
2. Trim and lowercase each job skill.
3. Lowercase each user skill.
4. Count job skills that exactly match a user skill.
5. Return `int((matched_count / job_skill_count) * 100)`.

If `tech_stack` is empty, the score is `0` with the reason `No extracted tech stack.`.

## Language Bonus

`_calculate_language_bonus()` returns:

- `10` when `language_requirement` contains `english`, case-insensitive.
- `0` otherwise.

## Visa Bonus

`_calculate_visa_bonus()` returns:

- `10` when `visa_needed` is true and `visa_sponsorship == "possible"`.
- `0` otherwise.

The current comparison is exact and case-sensitive for `possible`.

## Location Bonus

`_calculate_location_bonus()` returns:

- `0` when the request has no preferred countries.
- `10` when `LocationParser.extract_country(location)` matches one of the lowercased preferred countries.
- `0` otherwise.

`LocationParser.extract_country()` splits a location string by comma and returns the last non-empty part lowercased. For example, `Berlin, Germany` becomes `germany`.

## Total Score

The active formula is:

```text
match_score =
  skill_score
+ language_bonus
+ visa_bonus
+ location_bonus
```

The final score is capped:

```python
total_score = min(skill_score + visa_bonus + language_bonus + location_bonus, 100)
```

There is no lower-bound clamp in this path because all current components are non-negative.

## 100 Point Cap

The final `match_score` cannot exceed `100`. A perfect skill match plus all three bonuses still returns `100`, not `130`.

## Reason Generation

The scorer returns `reason_parts`:

- skill match reason from `calculate_match_score()`
- `language_bonus=<value>`
- `visa_bonus=<value>`
- `location_bonus=<value>`

`RecommendationBuilder.build()` joins these parts with a semicolon-space delimiter into the API `reason` field.

## Example

User profile:

```json
{
  "skills": ["Python", "FastAPI", "Docker", "AWS"],
  "preferred_countries": ["Germany"],
  "visa_needed": true
}
```

Job context:

```json
{
  "location": "Berlin, Germany",
  "tech_stack": "Python, FastAPI, Docker",
  "language_requirement": "Business English required",
  "visa_sponsorship": "possible"
}
```

Calculation:

```text
skill_score = 100
language_bonus = 10
visa_bonus = 10
location_bonus = 10
raw total = 130
match_score = 100
```

## Edge Cases

- Missing tech stack returns `skill_score=0`.
- Empty preferred countries always return `location_bonus=0`.
- A location without commas is treated as the country value after lowercasing.
- `visa_sponsorship="Possible"` does not receive the visa bonus because the active check is case-sensitive.
- Partial skill names do not match. `node` does not match `node.js` unless both strings normalize to the same exact value before scoring.

## Known Limitations

- Skill matching is exact token matching, not semantic matching.
- The active recommendation route returns `similarity_score=null`; similarity-oriented helper modules are not wired into `/recommendations/run`.
- Bonuses are fixed at `10` and are not configurable.
- The scorer does not account for seniority, salary, remote policy, job freshness, or user deal-breakers.
- LLM extraction quality affects the input fields, even though the final arithmetic is deterministic.

## Why the LLM Does Not Calculate the Final Score

The LLM extracts structured signals from messy text. The backend calculates the final score so that ranking is repeatable, explainable, and directly covered by unit tests.
