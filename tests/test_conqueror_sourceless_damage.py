"""ConquerorPower on sourceless damage (from QuarionIC/sts2-rl-agent d2a9dfae)."""

import sts2_env.cards  # noqa: F401  (loads the card registries)
from sts2_env.cards.status import is_sovereign_blade
from sts2_env.core.combat import CombatState
from sts2_env.core.damage import calculate_damage
from sts2_env.core.enums import PowerId, ValueProp
from sts2_env.core.rng import Rng
from sts2_env.monsters.act1_weak import create_nibbit


def test_conqueror_power_survives_sourceless_enemy_damage():
    """An enemy attack has no card source; is_sovereign_blade(None) must be False, not raise,
    and the 2x Sovereign Blade multiplier must not apply."""
    assert is_sovereign_blade(None) is False

    combat = CombatState(player_hp=70, player_max_hp=70, deck=[], rng_seed=11, character_id="Necrobinder")
    enemy, ai = create_nibbit(Rng(11))
    combat.add_enemy(enemy, ai)
    combat.apply_power_to(combat.primary_player, PowerId.CONQUEROR, 2)
    assert calculate_damage(10, enemy, combat.primary_player, ValueProp.MOVE, combat) == 10
