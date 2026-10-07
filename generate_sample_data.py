"""
generate_sample_data.py
------------------------
Builds an OFFLINE, realistic sample dataset that mirrors the real schema and
component categories used by NHTSA's Office of Defects Investigation (ODI)
complaints database (the same source real dealership/warranty quality teams
use as an early-warning signal for field failures).

This is a stand-in for the live data so the whole pipeline runs instantly,
without internet access. For REAL live records, run fetch_nhtsa_data.py
on a machine with normal internet access.

Output: data/sample_claims.csv
"""

import csv
import random

random.seed(42)

MAKES_MODELS = [
    ("Toyota", "Camry"), ("Toyota", "Corolla"), ("Honda", "Civic"),
    ("Honda", "Accord"), ("Ford", "F-150"), ("Ford", "Explorer"),
    ("Chevrolet", "Silverado"), ("Chevrolet", "Malibu"), ("Tesla", "Model 3"),
    ("Hyundai", "Elantra"), ("Nissan", "Altima"), ("Jeep", "Grand Cherokee"),
    ("BMW", "3 Series"), ("Kia", "Sportage"), ("Volkswagen", "Jetta"),
]

# Real NHTSA-style component categories
COMPONENTS = {
    "ENGINE": [
        "The engine stalled unexpectedly while driving on the highway at {speed} mph.",
        "Check engine light came on and the vehicle lost power intermittently.",
        "Engine makes a loud knocking noise on cold start, oil consumption is excessive.",
        "Vehicle would not start, engine cranks but does not turn over.",
    ],
    "BRAKES": [
        "Brake pedal went to the floor with no braking response, nearly caused a crash.",
        "ABS warning light stays on and brakes feel spongy under normal braking.",
        "Rear brakes are grinding, pads appear to be worn well below the wear indicator.",
        "Brake fluid leak found under the vehicle, pedal felt soft the day before.",
    ],
    "ELECTRICAL SYSTEM": [
        "Entire dashboard went dark while driving, warning chimes sounded randomly.",
        "Battery drains overnight even when the vehicle is not used for a day.",
        "Infotainment screen randomly reboots and the backup camera loses signal.",
        "Headlights flicker at night, sometimes cutting out completely for a few seconds.",
    ],
    "AIRBAGS": [
        "Airbag warning light is illuminated constantly, dealer says sensor is faulty.",
        "Airbag deployed unexpectedly while the vehicle was parked and not in use.",
        "Side curtain airbag did not deploy during a low speed collision.",
    ],
    "STEERING": [
        "Steering wheel became very difficult to turn at low speed, power steering failed.",
        "Vehicle pulls hard to the right and there is a clunking noise from the steering column.",
        "Steering locked up briefly while making a turn out of a parking lot.",
    ],
    "SUSPENSION": [
        "Front suspension makes a loud popping noise over bumps, control arm may be worn.",
        "Vehicle bounces excessively after hitting a pothole, shocks may have failed.",
        "Rear strut mount is broken, causing a metallic rattling sound while driving.",
    ],
    "FUEL SYSTEM": [
        "Strong smell of fuel noticed inside the cabin after refueling.",
        "Fuel gauge reads incorrectly, vehicle ran out of gas despite gauge showing half full.",
        "Fuel leak observed dripping from underneath the vehicle near the tank.",
    ],
    "TRANSMISSION": [
        "Transmission slips between second and third gear, especially when accelerating.",
        "Vehicle jerks hard when shifting from park to drive, sometimes delays engagement.",
        "Transmission fluid leak found, vehicle lost power while merging onto the freeway.",
    ],
}

CATEGORIES = list(COMPONENTS.keys())


def make_row(claim_id):
    make, model = random.choice(MAKES_MODELS)
    category = random.choice(CATEGORIES)
    template = random.choice(COMPONENTS[category])
    text = template.format(speed=random.choice([45, 55, 65, 70]))

    # Severity signals (mirrors real NHTSA fields: crash, fire, injuries, deaths)
    crash = random.random() < 0.08
    fire = random.random() < 0.03
    injuries = random.choice([0, 0, 0, 0, 1, 2]) if random.random() < 0.1 else 0
    deaths = 1 if (fire and random.random() < 0.05) else 0
    mileage = random.randint(500, 95000)
    model_year = random.choice(range(2016, 2026))

    return {
        "claim_id": f"WC{claim_id:05d}",
        "make": make,
        "model": model,
        "model_year": model_year,
        "mileage": mileage,
        "component": category,
        "complaint_text": text,
        "crash": int(crash),
        "fire": int(fire),
        "injuries": injuries,
        "deaths": deaths,
    }


def main(n=1200):
    rows = [make_row(i) for i in range(1, n + 1)]
    fields = list(rows[0].keys())
    with open("data/sample_claims.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {n} sample warranty claims to data/sample_claims.csv")


if __name__ == "__main__":
    main()
