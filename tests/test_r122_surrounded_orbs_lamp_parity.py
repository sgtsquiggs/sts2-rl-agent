"""Parity fixes found by the sts2-autoplay false-survival audit (R122): Surrounded and RandomEnemy cards, orb damage
through the damage-modify pass (Hard to Kill), and Unsettling Lamp with TemporaryStrengthPower debuffs."""

import sts2_env.powers  # noqa: F401

from sts2_env.cards.factory import create_card
from sts2_env.cards.ironclad import create_ironclad_starter_deck
from sts2_env.core.combat import CombatState
from sts2_env.core.enums import CardId, PowerId
from sts2_env.core.rng import Rng
from sts2_env.monsters.act1_weak import create_shrinker_beetle
from sts2_env.orbs.all import DarkOrb, LightningOrb


def _combat(enemies: int = 1, character_id: str = "Ironclad") -> CombatState:
    combat = CombatState(
        player_hp=70,
        player_max_hp=70,
        deck=create_ironclad_starter_deck(),
        rng_seed=4243,
        character_id=character_id,
    )
    for i in range(enemies):
        creature, ai = create_shrinker_beetle(Rng(4243 + i))
        combat.add_enemy(creature, ai)
    combat.start_combat()
    combat.energy = 10
    return combat


def _surrounded(combat: CombatState):
    left, right = combat.enemies
    left.apply_power(PowerId.BACK_ATTACK_LEFT, 1)
    right.apply_power(PowerId.BACK_ATTACK_RIGHT, 1)
    combat.player.apply_power(PowerId.SURROUNDED, 1)
    sur = combat.player.powers[PowerId.SURROUNDED]
    sur.facing = sur.FACING_LEFT
    return sur, left, right


def test_random_enemy_card_keeps_the_facing():
    combat = _combat(enemies=2)
    sur, _left, _right = _surrounded(combat)
    combat.hand = [create_card(CardId.SWORD_BOOMERANG)]
    assert combat.play_card(0)
    assert sur.facing == sur.FACING_LEFT  # C#: a RandomEnemy play has no cardPlay.Target


def test_targeted_card_still_turns_the_player():
    combat = _combat(enemies=2)
    sur, _left, _right = _surrounded(combat)
    combat.hand = [create_card(CardId.STRIKE_IRONCLAD)]
    assert combat.play_card(0, 1)
    assert sur.facing == sur.FACING_RIGHT


def test_orb_evoke_respects_hard_to_kill():
    combat = _combat(character_id="Defect")
    enemy = combat.enemies[0]
    enemy.max_hp = enemy.current_hp = 40
    enemy.apply_power(PowerId.HARD_TO_KILL, 9)
    dark = DarkOrb()
    dark._accumulated_evoke = 18
    dark.on_evoke(combat)
    assert enemy.current_hp == 31
    lightning = LightningOrb()
    lightning.on_evoke(combat)
    assert enemy.current_hp == 31 - 8


def test_unsettling_lamp_does_not_double_crush_unders_strength_twice():
    combat = _combat(enemies=1)
    combat.relics = combat._coerce_relics(["UNSETTLING_LAMP"])
    enemy = combat.enemies[0]
    combat.hand = [create_card(CardId.CRUSH_UNDER, upgraded=True)]
    assert combat.play_card(0)
    assert enemy.get_power_amount(PowerId.CRUSH_UNDER) == 4  # StrengthLoss 2, doubled by the lamp
    assert enemy.get_power_amount(PowerId.STRENGTH) == -4  # not -8: the internal Strength isn't doubled again
