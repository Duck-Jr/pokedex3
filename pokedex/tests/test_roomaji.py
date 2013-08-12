# encoding: utf8

import pokedex.roomaji
from pokedex.tests import positional_params

@positional_params(
        ('ヤミカラス',         'yamikarasu'),

        # Elongated vowel
        ('イーブイ',           'iibui'),
        ('ホーホー',           'hoohoo'),
        ('ピカチュウ',         'pikachuu'),

        # Combined characters
        ('ニャース',           'nyaasu'),
        ('ジャ',               'ja'),
        ('ぎゃくてん',         'gyakuten'),
        ('ウェザーボール',     'wezaabooru'),

        # Special katakana combinations
        ('ラティアス',         'ratiasu'),
        ('ウィー',             'wii'),
        ('セレビィ',           'sereby'),
    )
def test_roomaji(kana, roomaji):
    result = pokedex.roomaji.romanize(kana)
    assert result == roomaji


@positional_params(
        ('ヤミカラス',         'jamikarasu'),

        # Elongated vowel
        ('イーブイ',           'íbui'),
        ('ホーホー',           'hóhó'),
        ('ピカチュウ',         'pikačú'),

        # Combined characters
        ('ニャース',           'ňjásu'),
        ('ジャ',              'dža'),
        ('ぎゃくてん',         'gjakuten'),
        ('ウェザーボール',     'wezábóru'),

        # Special katakana combinations
        ('ラティアス',         'ratiasu'),
        ('ウィー',             'wí'),
        ('セレビィ',           'serebí'),
    )
def test_roomaji_cs(kana, roomaji):
    result = pokedex.roomaji.romanize(kana, 'cs')
    assert result == roomaji
