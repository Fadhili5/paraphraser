PLAN_LIMITS = {
    "free": {
        "max_characters": 20_000,
        "max_chars_per_request": 2000,
        "max_chunks": 2,
        "beams": 1,
    },
    "basic": {
        "max_characters": 200_000,
        "max_chars_per_request": 5000,
        "max_chunks": 4,
        "beams": 1,
    },
    "pro": {
        "max_characters": 1_000_000,
        "max_chars_per_request": 15000,
        "max_chunks": 6,
        "beams": 2,
    },
    "ultra": {
        "max_characters": 3_000_000,
        "max_chars_per_request": 30000,
        "max_chunks": 10,
        "beams": 2,
    },
}