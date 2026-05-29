"""
Generates synthetic MMM output data for the steering assistant demo.
Run: python generate_data.py
Writes: data/synthetic.json
"""

import json
import random
from pathlib import Path

WEEK = "2026-W22"

COUNTRIES = [
    "DE", "GB", "FR", "IT", "ES", "NL", "PL", "SE", "BE", "AT",
    "CH", "DK", "NO", "FI", "PT", "CZ", "HU", "RO", "GR", "IE",
    "SK", "HR", "SI", "LT", "LV", "EE", "BG", "RS", "UA", "ZA",
]

CHANNELS = [
    "paid_search", "paid_social", "display", "video",
    "affiliate", "email", "influencer", "programmatic",
]

# ROI ranges (min, max) per channel
CHANNEL_ROI = {
    "paid_search":  (2.5, 4.0),
    "paid_social":  (1.8, 3.0),
    "display":      (0.7, 2.0),
    "video":        (1.5, 2.5),
    "affiliate":    (2.0, 3.5),
    "email":        (3.0, 6.0),
    "influencer":   (1.0, 2.0),
    "programmatic": (0.8, 1.8),
}

# Spend ranges (EUR) by channel — bigger channels get bigger budgets
CHANNEL_SPEND = {
    "paid_search":  (40_000, 120_000),
    "paid_social":  (30_000, 100_000),
    "display":      (20_000, 80_000),
    "video":        (25_000, 90_000),
    "affiliate":    (15_000, 60_000),
    "email":        (5_000,  25_000),
    "influencer":   (10_000, 50_000),
    "programmatic": (20_000, 70_000),
}

# Seeded story rows: (country, channel) -> override dict
SEEDS = {
    ("DE", "paid_search"): {
        "current_spend": 84_000,
        "recommended_spend": 106_000,
        "roi": 3.4,
        "saturation_pct": 72,
        "action": "increase",
        "confidence": 0.91,
        "notes": "Strong elasticity, 28% below saturation curve",
    },
    ("PL", "paid_search"): {
        "current_spend": 52_000,
        "recommended_spend": 70_000,
        "roi": 3.1,
        "saturation_pct": 68,
        "action": "increase",
        "confidence": 0.88,
        "notes": "Underinvested market, high search intent, room to scale",
    },
    ("NL", "paid_social"): {
        "current_spend": 38_000,
        "recommended_spend": 53_000,
        "roi": 2.7,
        "saturation_pct": 61,
        "action": "increase",
        "confidence": 0.85,
        "notes": "Social engagement high, 39% below saturation — clear scale opportunity",
    },
    ("FR", "display"): {
        "current_spend": 78_000,
        "recommended_spend": 54_000,
        "roi": 0.8,
        "saturation_pct": 94,
        "action": "decrease",
        "confidence": 0.93,
        "notes": "Deeply over-saturated, diminishing returns — cut to recommended level",
    },
    ("IT", "display"): {
        "current_spend": 64_000,
        "recommended_spend": 46_000,
        "roi": 0.9,
        "saturation_pct": 91,
        "action": "decrease",
        "confidence": 0.90,
        "notes": "Over-saturated, ROI at floor — reduce spend to recover efficiency",
    },
    ("ES", "display"): {
        "current_spend": 55_000,
        "recommended_spend": 42_000,
        "roi": 0.7,
        "saturation_pct": 96,
        "action": "decrease",
        "confidence": 0.95,
        "notes": "Worst ROI in portfolio, near full saturation — immediate reduction required",
    },
    ("SE", "paid_social"): {
        "current_spend": 61_000,
        "recommended_spend": 63_000,
        "roi": 2.1,
        "saturation_pct": 82,
        "action": "watch",
        "confidence": 0.78,
        "notes": "Approaching saturation — hold current level, monitor weekly",
    },
    ("AT", "paid_search"): {
        "current_spend": 31_000,
        "recommended_spend": 33_000,
        "roi": 2.8,
        "saturation_pct": 79,
        "action": "watch",
        "confidence": 0.76,
        "notes": "Nearing saturation threshold — small headroom, do not scale without review",
    },
    ("BE", "display"): {
        "current_spend": 28_000,
        "recommended_spend": 29_000,
        "roi": 1.3,
        "saturation_pct": 80,
        "action": "watch",
        "confidence": 0.74,
        "notes": "At saturation boundary — hold and observe before any increase",
    },
}

ACTION_NOTES = {
    "increase": [
        "Below saturation curve, ROI above portfolio average",
        "Headroom remains, high conversion rate this week",
        "Elasticity strong, incremental revenue opportunity",
        "Market underpenetrated relative to size",
        "CPM efficiency high, demand signal solid",
    ],
    "decrease": [
        "Over-saturated, marginal return below threshold",
        "ROI declining week-on-week, cut to recovery level",
        "Diminishing returns — reallocate to higher-ROI channels",
        "Saturation curve flattening, spend above optimal point",
        "Frequency capping hitting limits, audience exhausted",
    ],
    "hold": [
        "Spend at optimal level, ROI stable",
        "At equilibrium — no change needed this week",
        "Model confidence high, current allocation correct",
        "Efficiency steady, no reallocation opportunity identified",
        "On plan — monitor for saturation signals next week",
    ],
    "watch": [
        "Approaching saturation, monitor closely",
        "ROI softening — hold and review next week",
        "Near threshold, one more week of data needed",
        "Mixed signals — do not scale until trend confirmed",
        "Confidence interval wide — conservative hold recommended",
    ],
}


def derive_action(saturation_pct: int, roi: float) -> str:
    if saturation_pct >= 88 or roi < 1.0:
        return "decrease"
    if saturation_pct >= 78:
        return "watch"
    if saturation_pct <= 70 and roi >= 2.0:
        return "increase"
    return "hold"


def build_row(country: str, channel: str, rng: random.Random) -> dict:
    seed = SEEDS.get((country, channel))

    roi_lo, roi_hi = CHANNEL_ROI[channel]
    sp_lo, sp_hi = CHANNEL_SPEND[channel]

    current_spend = round(rng.randint(sp_lo, sp_hi) / 1000) * 1000
    roi = round(rng.uniform(roi_lo, roi_hi), 1)
    saturation_pct = rng.randint(40, 95)
    action = derive_action(saturation_pct, roi)
    confidence = round(rng.uniform(0.65, 0.97), 2)

    # Recommended spend: increase if under-saturated, decrease if over
    if action == "increase":
        rec_factor = rng.uniform(1.10, 1.35)
        recommended_spend = round(current_spend * rec_factor / 1000) * 1000
    elif action == "decrease":
        rec_factor = rng.uniform(0.65, 0.85)
        recommended_spend = round(current_spend * rec_factor / 1000) * 1000
    elif action == "watch":
        rec_factor = rng.uniform(0.98, 1.05)
        recommended_spend = round(current_spend * rec_factor / 1000) * 1000
    else:
        recommended_spend = current_spend

    spend_delta = recommended_spend - current_spend
    current_revenue = round(current_spend * roi / 1000) * 1000
    incremental_revenue = round(abs(spend_delta) * roi * 0.8 / 1000) * 1000
    note = rng.choice(ACTION_NOTES[action])

    row = {
        "country": country,
        "channel": channel,
        "week": WEEK,
        "current_spend": current_spend,
        "recommended_spend": recommended_spend,
        "spend_delta": spend_delta,
        "current_revenue": current_revenue,
        "incremental_revenue": incremental_revenue,
        "roi": roi,
        "saturation_pct": saturation_pct,
        "action": action,
        "confidence": confidence,
        "notes": note,
    }

    if seed:
        row.update(seed)
        row["spend_delta"] = row["recommended_spend"] - row["current_spend"]
        row["current_revenue"] = round(row["current_spend"] * row["roi"] / 1000) * 1000
        row["incremental_revenue"] = round(abs(row["spend_delta"]) * row["roi"] * 0.8 / 1000) * 1000

    return row


def main():
    rng = random.Random(42)
    rows = [build_row(c, ch, rng) for c in COUNTRIES for ch in CHANNELS]

    out = Path("data/synthetic.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=2))
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
