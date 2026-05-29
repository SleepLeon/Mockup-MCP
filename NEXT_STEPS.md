# Next steps

## 1. Refine the system prompt

- [ ] Run the hero scenario and capture Claude's actual output — compare against the intended mockup format
- [ ] Tune the opening brief structure: headline opportunity, saturation warning, recommended reallocation in 3-5 sentences
- [ ] Tighten the priority action list format — consistent columns, ranking logic explicit in the prompt
- [ ] Test edge cases: what does Claude say when asked about a country with no strong signal?

## 2. Refine the tool logic

- [ ] Improve `run_scenario` revenue calculation — validate the saturation dampening factor (0.6x excess) against MMM theory
- [ ] Improve the scenario summary text — make it more narrative, less mechanical
- [ ] Review action derivation in `generate_data.py` — ensure `watch` threshold (saturation ≥78) feels right in practice
- [ ] Add `list_weeks` tool so Claude can discover available weeks without the user hardcoding them

## 3. Guard rails and safety constraints

- [ ] Hard cap on single-channel spend increase in `run_scenario` — flag if new_spend > 2× recommended
- [ ] Confidence gate — Claude should refuse to make a strong recommendation if confidence < 0.7, prompt says this but the tool should surface it clearly
- [ ] Saturation ceiling — warn explicitly if any change would push saturation_pct above 95
- [ ] Budget neutrality check — warn in summary if total_spend_delta is significantly non-zero (i.e. the scenario is not a reallocation but a net increase)
- [ ] Unknown country/channel handling — return a clear error row rather than silently skipping

## 4. Production data connection

- [ ] Add `db.py` — Redshift connection pool, parameterised query by week
- [ ] Add `DATABASE_URL` to `.env`, load via `python-dotenv`
- [ ] Mirror the synthetic row shape exactly in SQL so no tool changes needed
- [ ] Validate one week of real MMM output against the synthetic schema
- [ ] Remove dependency on `data/synthetic.json` once real data is confirmed working
