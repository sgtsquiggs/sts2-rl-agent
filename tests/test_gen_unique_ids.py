"""GEN_UNIQUE_IDS (sts2-autoplay R181): factory cards without an instance id take one when the switch is on."""

import pytest

import sts2_env.cards.base as card_base
from sts2_env.cards.factory import create_card
from sts2_env.cards.status import make_dowsing, make_wither
from sts2_env.core.enums import CardId

# Factories that pass no instance_id (gosim's cards.json no_uid), one per path: a character factory without and with
# `upgraded`, and the status factories the sim calls directly (Aeonglass, Withering Presence).
NO_UID = (CardId.BONE_SHARDS, CardId.GLITTERSTREAM, CardId.COUNTDOWN_CARD, CardId.WITHER, CardId.DOWSING)


@pytest.fixture
def unique_ids():
    card_base.GEN_UNIQUE_IDS = True
    yield
    card_base.GEN_UNIQUE_IDS = False


@pytest.mark.parametrize("card_id", NO_UID)
def test_off_keeps_id_zero(card_id):
    before = card_base._next_instance_id
    a, b = create_card(card_id), create_card(card_id, upgraded=True)
    assert (a.instance_id, b.instance_id) == (0, 0)
    assert card_base._next_instance_id == before


@pytest.mark.parametrize("card_id", NO_UID)
def test_on_gives_each_card_its_own_id(unique_ids, card_id):
    before = card_base._next_instance_id
    a, b = create_card(card_id), create_card(card_id)
    assert (a.instance_id, b.instance_id) == (before + 1, before + 2)
    assert a != b
    assert [a, b].index(b) == 1


def test_on_status_factories(unique_ids):
    before = card_base._next_instance_id
    assert (make_wither().instance_id, make_dowsing().instance_id) == (before + 1, before + 2)


def test_on_leaves_cards_with_ids_alone(unique_ids):
    before = card_base._next_instance_id
    card = create_card(CardId.STRIKE_IRONCLAD)
    assert card.instance_id == before + 1
    assert card_base._next_instance_id == before + 1
