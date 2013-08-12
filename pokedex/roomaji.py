# encoding: utf8
"""Provides `romanize()` for romanizing simple Japanese text.

Also provides available romanizers in a dictionary keyed by language identifier.
"""

class Romanizer(object):
    def __init__(self, parent=None, **tables):
        """Create a Romanizer

        parent: A LookupTables to base this one on
        tables: Dicts that become the object's attributes. If a parent is given,
            its tables are used, and updated with the given ones
        """
        self.parent = parent
        if parent:
            self.tables = parent.tables
            for name, table in list(tables.items()):
                # Take a copy -- don't want to clobber the parent's tables
                self.tables[name] = dict(self.tables[name])
                self.tables[name].update(table)
        else:
            self.tables = tables

        for name, table in list(self.tables.items()):
            setattr(self, name, table)

    def romanize(self, string):
        """Convert a string of kana to roomaji."""

        vowels = ['a', 'e', 'i', 'o', 'u', 'y']

        characters = []
        last_kana = None  # Used for ー; っ or ッ; ん or ン
        last_char = None  # Used for small kana combos
        for char in string:
            # Full-width Latin
            if 0xff01 <= ord(char) <= 0xff5e:
                if last_kana == 'sokuon':
                    raise ValueError("Sokuon cannot precede Latin characters.")

                # XXX Real Unicode decomposition would be nicer
                char = chr(ord(char) - 0xff01 + 0x21)
                characters.append(char)

                last_kana = None

            # Small vowel kana
            elif char in self.roomaji_small_kana:
                combo = last_char + char
                if combo in self.roomaji_small_kana_combos:
                    characters[-1] = self.roomaji_small_kana_combos[combo]

                else:
                    # If we don't know what it is...  act dumb and treat it as a
                    # full-size vowel.  Better than bailing, and seems to occur a
                    # lot, e.g. ピィ is "pii"
                    characters.append(self.roomaji_small_kana[char])

                last_kana = self.roomaji_small_kana[char]

            # Youon
            elif char in self.roomaji_youon:
                if not last_kana or last_kana[-1] != 'i' or last_kana == 'i':
                    raise ValueError("Youon must follow an -i sound.")

                # Drop the -i and append the ya/yu/yo sound
                new_sound = self.roomaji_youon[char]
                if last_kana in self.y_drop:
                    # Strip the y-
                    new_char = self.y_drop[last_kana] + new_sound[1:]
                else:
                    new_char = last_kana[:-1] + new_sound

                characters[-1] = new_char
                last_kana = new_char

            # Sokuon
            elif char in ('っ', 'ッ'):
                # Remember it and double the consonant next time around
                last_kana = 'sokuon'

            # Extended vowel or n
            elif char == 'ー':
                if last_kana[-1] not in vowels:
                    raise ValueError("'ー' must follow by a vowel.")
                if last_kana[-1] in self.lengthened_vowels:
                    characters[-1] = characters[-1][:-1]
                    characters.append(self.lengthened_vowels[last_kana[-1]])
                else:
                    characters.append(last_kana[-1])

                last_kana = None

            # Regular ol' kana
            elif char in self.roomaji_kana:
                kana = self.roomaji_kana[char]

                if last_kana == 'sokuon':
                    if kana[0] in vowels:
                        raise ValueError("Sokuon cannot precede a vowel.")

                    characters.append(kana[0])
                elif last_kana == 'n' and kana[0] in vowels:
                    characters.append("'")

                # Special characters fo doubled kana
                if kana[0] in self.lengthened_vowels and characters and kana == characters[-1][-1]:
                    kana = self.lengthened_vowels[kana[0]]
                    characters[-1] = characters[-1][:-1]

                characters.append(kana)

                last_kana = kana

            # Not Japanese?
            else:
                if last_kana == 'sokuon':
                    raise ValueError("Sokuon must be followed by another kana.")

                characters.append(char)

                last_kana = None

            last_char = char


        if last_kana == 'sokuon':
            raise ValueError("Sokuon cannot be the last character.")

        return str(''.join(characters))


romanizers = dict()

romanizers['en'] = Romanizer(
    roomaji_kana={
        # Hiragana
        'あ': 'a',     'い': 'i',     'う': 'u',     'え': 'e',     'お': 'o',
        'か': 'ka',    'き': 'ki',    'く': 'ku',    'け': 'ke',    'こ': 'ko',
        'さ': 'sa',    'し': 'shi',   'す': 'su',    'せ': 'se',    'そ': 'so',
        'た': 'ta',    'ち': 'chi',   'つ': 'tsu',   'て': 'te',    'と': 'to',
        'な': 'na',    'に': 'ni',    'ぬ': 'nu',    'ね': 'ne',    'の': 'no',
        'は': 'ha',    'ひ': 'hi',    'ふ': 'fu',    'へ': 'he',    'ほ': 'ho',
        'ま': 'ma',    'み': 'mi',    'む': 'mu',    'め': 'me',    'も': 'mo',
        'や': 'ya',                    'ゆ': 'yu',                    'よ': 'yo',
        'ら': 'ra',    'り': 'ri',    'る': 'ru',    'れ': 're',    'ろ': 'ro',
        'わ': 'wa',    'ゐ': 'wi',                    'ゑ': 'we',    'を': 'wo',
                                                                        'ん': 'n',
        'が': 'ga',    'ぎ': 'gi',    'ぐ': 'gu',    'げ': 'ge',    'ご': 'go',
        'ざ': 'za',    'じ': 'ji',    'ず': 'zu',    'ぜ': 'ze',    'ぞ': 'zo',
        'だ': 'da',    'ぢ': 'ji',    'づ': 'dzu',   'で': 'de',    'ど': 'do',
        'ば': 'ba',    'び': 'bi',    'ぶ': 'bu',    'べ': 'be',    'ぼ': 'bo',
        'ぱ': 'pa',    'ぴ': 'pi',    'ぷ': 'pu',    'ぺ': 'pe',    'ぽ': 'po',

        # Katakana
        'ア': 'a',     'イ': 'i',     'ウ': 'u',     'エ': 'e',     'オ': 'o',
        'カ': 'ka',    'キ': 'ki',    'ク': 'ku',    'ケ': 'ke',    'コ': 'ko',
        'サ': 'sa',    'シ': 'shi',   'ス': 'su',    'セ': 'se',    'ソ': 'so',
        'タ': 'ta',    'チ': 'chi',   'ツ': 'tsu',   'テ': 'te',    'ト': 'to',
        'ナ': 'na',    'ニ': 'ni',    'ヌ': 'nu',    'ネ': 'ne',    'ノ': 'no',
        'ハ': 'ha',    'ヒ': 'hi',    'フ': 'fu',    'ヘ': 'he',    'ホ': 'ho',
        'マ': 'ma',    'ミ': 'mi',    'ム': 'mu',    'メ': 'me',    'モ': 'mo',
        'ヤ': 'ya',                    'ユ': 'yu',                    'ヨ': 'yo',
        'ラ': 'ra',    'リ': 'ri',    'ル': 'ru',    'レ': 're',    'ロ': 'ro',
        'ワ': 'wa',    'ヰ': 'wi',                    'ヱ': 'we',    'ヲ': 'wo',
                                                                        'ン': 'n',
        'ガ': 'ga',    'ギ': 'gi',    'グ': 'gu',    'ゲ': 'ge',    'ゴ': 'go',
        'ザ': 'za',    'ジ': 'ji',    'ズ': 'zu',    'ゼ': 'ze',    'ゾ': 'zo',
        'ダ': 'da',    'ヂ': 'ji',    'ヅ': 'dzu',   'デ': 'de',    'ド': 'do',
        'バ': 'ba',    'ビ': 'bi',    'ブ': 'bu',    'ベ': 'be',    'ボ': 'bo',
        'パ': 'pa',    'ピ': 'pi',    'プ': 'pu',    'ペ': 'pe',    'ポ': 'po',
                                        'ヴ': 'vu',
    },

    roomaji_youon={
        # Hiragana
        'ゃ': 'ya',                    'ゅ': 'yu',                    'ょ': 'yo',

        # Katakana
        'ャ': 'ya',                    'ュ': 'yu',                    'ョ': 'yo',
    },

    # XXX If romanize() ever handles hiragana, it will need to make sure that the
    # preceding character was a katakana
    # This does not include every small kana combination, but should include every
    # one used in a Pokémon name.  An exhaustive list would be..  very long
    roomaji_small_kana={
        'ァ': 'a',     'ィ': 'i',     'ゥ': 'u',     'ェ': 'e',     'ォ': 'o',
    },
    roomaji_small_kana_combos={
        # These are, by the way, fairly arbitrary.  "shi xi" to mean "sy" is
        # particularly weird, but it seems to be what GF intends

        # Simple vowel replacement
                        'ウィ': 'wi',  'ウゥ': 'wu',  'ウェ': 'we',  'ウォ': 'wo',
        'ヴァ': 'va',  'ヴィ': 'vi',                  'ヴェ': 've',  'ヴォ': 'vo',
                                                        'チェ': 'che',
                                                        'シェ': 'she',
                                                        'ジェ': 'je',
        'テァ': 'tha', 'ティ': 'ti',  'テゥ': 'thu', 'テェ': 'tye', 'テォ': 'tho',
        'デァ': 'dha', 'ディ': 'di',  'デゥ': 'dhu', 'デェ': 'dye', 'デォ': 'dho',
        'ファ': 'fa',  'フィ': 'fi',  'ホゥ': 'hu',  'フェ': 'fe',  'フォ': 'fo',

        # Not so much
        'シィ': 'sy',
        'ミィ': 'my',
        'ビィ': 'by',
        'ピィ': 'py',
    },
    lengthened_vowels={},
    y_drop={'chi': 'ch', 'shi': 'sh', 'ji': 'j'},
)

romanizers['cs'] = Romanizer(parent=romanizers['en'],
    roomaji_kana={
        'し': 'ši', 'ち': 'či', 'つ': 'cu',
        'や': 'ja', 'ゆ': 'ju', 'よ': 'jo',
        'じ': 'dži', 'ぢ': 'dži',
        'シ': 'ši', 'チ': 'či', 'ツ': 'cu',
        'ヤ': 'ja', 'ユ': 'ju', 'ヨ': 'jo',
        'ジ': 'dži', 'ヂ': 'dži',
    },
    roomaji_youon={
        'ゃ': 'ja', 'ゅ': 'ju', 'ょ': 'jo',
        'ャ': 'ja', 'ュ': 'ju', 'ョ': 'jo',
    },
    roomaji_small_kana_combos={
        'チェ': 'če', 'シェ': 'še', 'ジェ': 'dže',
        'テェ': 'tje', 'デェ': 'dje',
        'シィ': 'sí', 'ミィ': 'mí', 'ビィ': 'bí', 'ピィ': 'pí',
    },
    lengthened_vowels={'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú'},
    y_drop={'či': 'č', 'ši': 'š', 'dži': 'dž', 'ni': 'ňj'},
)

def romanize(string, lang='en'):
    """Convert a string of kana to roomaji."""

    # Get the correct romanizer; fall back to English
    romanizer = romanizers.get(lang, 'en')

    # Romanize away!
    return romanizer.romanize(string)
