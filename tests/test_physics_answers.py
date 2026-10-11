from fractions import Fraction as F

from app.services.content_loader import content_loader


def test_phy_kin_0001():
    """Verify phy-kin-0001: 72 km/h braking at 4 m/s^2."""
    q = content_loader.get_question_by_id("phy-kin-0001")
    assert q is not None
    # Level B calculation:
    u = F(72) * F(5, 18)  # 20 m/s
    a = F(-4)
    v = F(0)
    # v^2 = u^2 + 2as => s = (v^2 - u^2) / (2a)
    s = (v**2 - u**2) / (2 * a)
    assert s == F(50)

    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "50" in correct_opt.text


def test_phy_kin_0002():
    """Verify phy-kin-0002: Thrown up at 20 m/s from 60 m cliff, hits ground."""
    q = content_loader.get_question_by_id("phy-kin-0002")
    assert q is not None
    # s = ut + 0.5 a t^2 => -60 = 20t - 5t^2 => 5t^2 - 20t - 60 = 0 => t^2 - 4t - 12 = 0
    # Roots: (t-6)(t+2) = 0 => t = 6
    u = 20
    g = 10
    h = -60
    # check t = 6
    t = 6
    s_calc = u * t - 0.5 * g * (t**2)
    assert s_calc == h
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "6 s" in correct_opt.text


def test_phy_kin_0003():
    """Verify phy-kin-0003: Trapezoid v-t area."""
    q = content_loader.get_question_by_id("phy-kin-0003")
    assert q is not None
    # Area = 0.5 * (14 + (10 - 4)) * 12
    area = F(1, 2) * (14 + 6) * 12
    assert area == 120
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "120 m" in correct_opt.text


def test_phy_kin_0004():
    """Verify phy-kin-0004: Police chase 2.5 t^2 = 30 t."""
    q = content_loader.get_question_by_id("phy-kin-0004")
    assert q is not None
    # 0.5 * 5 * t^2 = 30 * t => 2.5 t = 30 => t = 12
    t = F(30) / F(5, 2)
    assert t == 12
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "12 s" in correct_opt.text


def test_phy_kin_0005():
    """Verify phy-kin-0005: v^2 = 2g(20), (2v)^2 = 2gH => H = 4 * 20 = 80."""
    q = content_loader.get_question_by_id("phy-kin-0005")
    assert q is not None
    assert float(q.answer.correct_value) == 80.0


def test_phy_kin_0006():
    """Verify phy-kin-0006: s = 15(7) - 0.5(3)(49) = 105 - 73.5 = 31.5."""
    q = content_loader.get_question_by_id("phy-kin-0006")
    assert q is not None
    s = F(15) * 7 - F(3, 2) * 49
    assert float(s) == 31.5
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "31.5 m" in correct_opt.text


def test_phy_frc_0001():
    """Verify phy-frc-0001: 50 - 0.4*5*10 = 30 => a = 30/5 = 6."""
    q = content_loader.get_question_by_id("phy-frc-0001")
    assert q is not None
    F_pull = 50
    m = 5
    mu = F(4, 10)
    g = 10
    f_k = mu * m * g  # 20
    F_net = F_pull - f_k  # 30
    a = F_net / m  # 6
    assert a == 6
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "6 m/s²" in correct_opt.text


def test_phy_eng_0001():
    """Verify phy-eng-0001: mgh = mu m g s => s = h / mu = 5 / 0.25 = 20."""
    q = content_loader.get_question_by_id("phy-eng-0001")
    assert q is not None
    h = 5
    mu = F(25, 100)
    s = h / mu
    assert s == 20
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "20 m" in correct_opt.text


def test_mat_alg_0001():
    """Verify mat-alg-0001: (x-5)(x+1)/(x-2) <= 0."""
    q = content_loader.get_question_by_id("mat-alg-0001")
    assert q is not None
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "-1]" in correct_opt.text and "(2, 5]" in correct_opt.text


def test_mat_alg_0002():
    """Verify mat-alg-0002: 4^x - 10*2^x + 16 = 0 => x=1,3 => sum=4."""
    q = content_loader.get_question_by_id("mat-alg-0002")
    assert q is not None
    assert float(q.answer.correct_value) == 4.0


def test_tpat3_quant_0001():
    """Verify tpat3-quant-0001: 360 * (20/60) * (15/45) = 40 rpm."""
    q = content_loader.get_question_by_id("tpat3-quant-0001")
    assert q is not None
    n_D = F(360) * F(20, 60) * F(15, 45)
    assert n_D == 40
    correct_opt = [o for o in q.answer.options if o.correct][0]
    assert "40 rpm" in correct_opt.text
