from app.services.procedural_gen import (
    generate_area_volume,
    generate_fractions_powers,
    generate_kinematics_5eq,
    generate_kmh_to_ms,
    generate_random_drill,
)


def test_generate_kmh_to_ms():
    for _ in range(10):
        drill = generate_kmh_to_ms()
        assert drill["drill_type"] == "unit_kmh_ms"
        assert drill["stem"]
        assert drill["expected_answer"]
        assert drill["unit"] in ["m/s", "km/h"]
        assert drill["explanation"]


def test_generate_area_volume():
    for _ in range(10):
        drill = generate_area_volume()
        assert drill["drill_type"] == "area_volume"
        assert drill["stem"]
        assert drill["expected_answer"]
        assert drill["explanation"]


def test_generate_kinematics_5eq():
    for _ in range(10):
        drill = generate_kinematics_5eq()
        assert drill["drill_type"] == "kinematics_5eq"
        assert drill["stem"]
        assert drill["expected_answer"]
        assert drill["explanation"]


def test_generate_fractions_powers():
    for _ in range(10):
        drill = generate_fractions_powers()
        assert drill["drill_type"] == "fractions_powers"
        assert drill["stem"]
        assert drill["expected_answer"]
        assert drill["explanation"]


def test_generate_random_drill():
    drill = generate_random_drill()
    assert "drill_type" in drill
    assert "stem" in drill
    assert "expected_answer" in drill
