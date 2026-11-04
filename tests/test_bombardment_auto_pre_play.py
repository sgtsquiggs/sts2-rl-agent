"""Bombardment replays from the exhaust pile in the auto-pre-play phase (sts2-autoplay R182b).

Bombardment.cs (v0.111) plays itself in AfterAutoPrePlayPhaseEnteredEarly, which CombatManager.RunAutoPrePlayPhase
fires after SetupPlayerTurn (hand draw, AfterPlayerTurnStart) and AfterSideTurnStart, not before the hand draw.
"""

from sts2_env.cards.factory import create_card
from sts2_env.core.enums import CardId, PowerId


def _bombardment_in_exhaust(combat):
    card = create_card(CardId.BOMBARDMENT)
    card.owner = combat.player
    combat.exhaust_pile.append(card)
    return card


def test_replay_after_turn_start_strength(simple_combat):
    # The replay comes after the hand draw (5 cards in hand) and after Demon Form's Strength (AfterSideTurnStart).
    combat = simple_combat
    enemy = combat.enemies[0]
    enemy.max_hp = enemy.current_hp = 500
    card = _bombardment_in_exhaust(combat)
    combat.apply_power_to(combat.player, PowerId.DEMON_FORM, 2)
    seen = {}
    orig = combat.auto_play_card

    def spy(c, *a, **k):
        seen["hand"] = len(combat.hand)
        seen["str"] = combat.player.get_power_amount(PowerId.STRENGTH)
        before = enemy.current_hp + enemy.block
        out = orig(c, *a, **k)
        seen["dealt"] = before - enemy.current_hp - enemy.block
        return out

    combat.auto_play_card = spy
    combat.end_player_turn()
    assert (seen["hand"], seen["str"]) == (5, 2)
    assert seen["dealt"] > 0
    assert card in combat.exhaust_pile
