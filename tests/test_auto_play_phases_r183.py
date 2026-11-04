"""v0.109+ turn phases for auto-plays (sts2-autoplay R183).

CombatManager.RunAutoPrePlayPhase fires AfterAutoPrePlayPhaseEntered after the hand draw, AfterPlayerTurnStart,
AfterSideTurnStart and the orb queue (MayhemPower, HistoryCourse, Imbued; WhisperingEarring in the Late pass).
EndPlayerTurnPhaseOneInternal fires AfterAutoPostPlayPhaseEntered before BeforeSideTurnEnd (StampedePower,
HowlFromBeyond, IAmInvincible).
"""

from sts2_env.cards.factory import create_card
from sts2_env.core.combat import CombatState
from sts2_env.core.enums import CardId, PowerId
from sts2_env.monsters.act1_weak import create_shrinker_beetle
from sts2_env.core.rng import Rng


def _combat(relics=()):
    combat = CombatState(
        player_hp=80, player_max_hp=80, deck=[], rng_seed=4242, character_id="Ironclad", relics=list(relics)
    )
    creature, ai = create_shrinker_beetle(Rng(4242))
    creature.max_hp = creature.current_hp = 500
    combat.add_enemy(creature, ai)
    combat.start_combat()
    return combat


def _owned(combat, card_id):
    card = create_card(card_id)
    card.owner = combat.player
    return card


def test_history_course_replay_sees_turn_start_strength():
    combat = _combat(["HistoryCourse"])
    enemy = combat.enemies[0]
    combat.hand = [_owned(combat, CardId.STRIKE_IRONCLAD)]
    combat.draw_pile = [_owned(combat, CardId.DEFEND_IRONCLAD) for _ in range(6)]
    combat.energy = 1
    assert combat.play_card(0, 0)
    combat.apply_power_to(combat.player, PowerId.DEMON_FORM, 2)
    seen = {}
    orig = combat.auto_play_card

    def spy(card, *a, **k):
        seen["hand"] = len(combat.hand)
        seen["str"] = combat.player.get_power_amount(PowerId.STRENGTH)
        return orig(card, *a, **k)

    combat.auto_play_card = spy
    combat.end_player_turn()
    assert (seen["hand"], seen["str"]) == (5, 2)


def test_mayhem_plays_after_the_draw_and_turn_start_hooks():
    combat = _combat()
    combat.hand = []
    combat.draw_pile = [_owned(combat, CardId.DEFEND_IRONCLAD) for _ in range(7)]
    combat.apply_power_to(combat.player, PowerId.MAYHEM, 1)
    combat.apply_power_to(combat.player, PowerId.DEMON_FORM, 2)
    seen = {}
    orig = combat.auto_play_card

    def spy(card, *a, **k):
        seen["hand"] = len(combat.hand)
        seen["str"] = combat.player.get_power_amount(PowerId.STRENGTH)
        return orig(card, *a, **k)

    combat.auto_play_card = spy
    combat.end_player_turn()
    assert (seen["hand"], seen["str"]) == (5, 2)
    assert len(combat.draw_pile) == 1


def test_i_am_invincible_plays_before_turn_end_hooks():
    combat = _combat()
    card = _owned(combat, CardId.I_AM_INVINCIBLE)
    combat.hand = []
    combat.draw_pile = [card]
    combat._apply_auto_post_play()  # noqa: SLF001
    assert card not in combat.draw_pile
    assert combat.player.block == card.base_block
