import re

LETTER_MAP = {
    'a': 'а', 'b': 'бэ', 'c': 'цэ', 'd': 'дэ',
    'e': 'е', 'f': 'эф', 'g': 'гэ', 'h': 'аш'
}
NUMBER_MAP = {
    '1': 'один', '2': 'два', '3': 'три', '4': 'четыре',
    '5': 'пять', '6': 'шесть', '7': 'семь', '8': 'восемь'
}

_cell_re = re.compile(r'\b([a-h])([1-8])\b', re.IGNORECASE)

def transliterate_chess_notation(text: str) -> str:
    def repl(match):
        letter = match.group(1).lower()
        number = match.group(2)
        return f"{LETTER_MAP[letter]} {NUMBER_MAP[number]}"
    
    return _cell_re.sub(repl, text)