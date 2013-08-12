# Encoding: UTF-8

from pokedex.tests import *

from pokedex.lookup import PokedexLookup

lookup = PokedexLookup()

@positional_params(
        # Simple lookups
        ('Eevee',          'pokemon_species',133),
        ('Scratch',        'moves',        10),
        ('Master Ball',    'items',        1),
        ('normal',         'types',        1),
        ('Run Away',       'abilities',    50),

        # Funny characters
        ('Mr. Mime',       'pokemon_species', 122),
        ("Farfetch'd",     'pokemon_species', 83),
        ('Poké Ball',      'items',           4),

        # Forms
        ('Rotom',          'pokemon_species', 479),
        ('Wash Rotom',     'pokemon_forms',   708),
        ('East Shellos',   'pokemon_forms',   688),

        # Other languages
        ('イーブイ',       'pokemon_species', 133),
        ('Iibui',          'pokemon_species', 133),
        ('Eievui',         'pokemon_species', 133),
        ('이브이',         'pokemon_species', 133),
        ('伊布',           'pokemon_species', 133),
        ('Evoli',          'pokemon_species', 133),
    )
def test_exact_lookup(input, table, id):
    results = lookup.lookup(input)
    assert len(results) == 1
    assert results[0].exact == True

    row = results[0].object
    assert row.__tablename__ == table
    assert row.id == id


def test_id_lookup():
    results = lookup.lookup('1')
    assert len(results) >= 5
    assert all(result.object.id == 1 for result in results)


def test_multi_lookup():
    results = lookup.lookup('Metronome')
    assert len(results) == 2
    assert results[0].exact


def test_type_lookup():
    results = lookup.lookup('pokemon:1')
    assert results[0].object.__tablename__ == 'pokemon_species'
    assert len(results) == 1
    assert results[0].object.name == 'Bulbasaur'

    results = lookup.lookup('1', valid_types=['pokemon_species'])
    assert results[0].object.name == 'Bulbasaur'


def test_language_lookup():
    # There are two objects named "charge": the move Charge, and the move
    # Tackle, which is called "Charge" in French.
    results = lookup.lookup('charge')
    assert len(results) > 1

    results = lookup.lookup('@fr:charge')
    assert results[0].iso639 == 'fr'
    assert len(results) == 1
    assert results[0].object.name == 'Tackle'

    results = lookup.lookup('charge', valid_types=['@fr'])
    assert results[0].object.name == 'Tackle'

    results = lookup.lookup('@fr,move:charge')
    assert results[0].object.name == 'Tackle'

    results = lookup.lookup('@fr:charge', valid_types=['move'])
    assert results[0].object.name, 'Tackle'


@positional_params(
        # Regular English names
        ('chamander',          'Charmander'),
        ('pokeball',           'Poké Ball'),

        # Names with squiggles in them
        ('farfetchd',          "Farfetch'd"),
        ('porygonz',           'Porygon-Z'),

        # Sufficiently long foreign names
        ('カクレオ',           'Kecleon'),
        ('Yamikrasu',          'Murkrow'),
    )
def test_fuzzy_lookup(misspelling, name):
    results = lookup.lookup(misspelling)
    first_result = results[0]
    assert first_result.object.name == name


def test_nidoran():
    results = lookup.lookup('Nidoran')
    top_names = [result.object.name for result in results[0:2]]
    assert 'Nidoran♂' in top_names
    assert 'Nidoran♀' in top_names


@positional_params(
        ('pokemon:*meleon',    'Charmeleon'),
        ('item:master*',       'Master Ball'),
        ('ee?ee',              'Eevee'),
    )
def test_wildcard_lookup(wildcard, name):
    results = lookup.lookup(wildcard)
    first_result = results[0]
    assert first_result.object.name == name


def test_bare_random():
    for i in range(5):
        results = lookup.lookup('random')
        assert len(results) == 1


@positional_params(
        ['pokemon_species'],
        ['moves'],
        ['items'],
        ['abilities'],
        ['types'],
    )
def test_qualified_random(table_name):
    results = lookup.lookup('random', valid_types=[table_name])
    assert len(results) == 1
    assert results[0].object.__tablename__ == table_name


def test_crash_empty_prefix():
    """Searching for ':foo' used to crash, augh!"""
    results = lookup.lookup(':Eevee')
    assert results[0].object.name == 'Eevee'
