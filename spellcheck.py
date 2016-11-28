import argparse

from collections import defaultdict

from cmd import Cmd

import re


VOWEL_RE = re.compile(r'[aeiouy]')
REPEAT_RE = re.compile(r'(.)\1+')


def hash_word(word):
    # Vowels get replaced with 'A'
    word = VOWEL_RE.sub('A', word)
    # Repeated letters are replaced with a single letter
    word = REPEAT_RE.sub(r'\1', word)
    return word


def pick_suggestion(input_word, candidate_word_lst, candidate_word_vowel_stat_lst):
    input_word_vowel_stat = vowels_stat(input_word)
    dct = {}
    for candidate_word, candidate_word_vowel_stat in zip(candidate_word_lst, candidate_word_vowel_stat_lst):
        dct[candidate_word] = sum(abs(x-y) for x, y in zip(input_word_vowel_stat, candidate_word_vowel_stat))
    return min(dct, key=lambda key: dct[key])


def vowels_stat(word):
    return [len(m.group(0)) for m in re.finditer(r'[aeiouy]+', word)]


class SpellCmd(Cmd):

    NO_SUGGESTION = 'NO SUGGESTION'

    prompt = '> '
    intro = """
    Spellchecking util. Will print corrected word or `{no_suggestion}` string if no corrections can be performed.
    """.format(
        no_suggestion=NO_SUGGESTION
    )

    def _prepare_word(self, word):
        return str(word).strip().lower()

    def __init__(self, dict_file_name):
        Cmd.__init__(self)

        with open(dict_file_name, 'r') as f:
            self.word_lst = [self._prepare_word(line) for line in f]

        self.word_hash_dct = defaultdict(set)
        self.vowel_stat_dct = {}

        for word in self.word_lst:
            word_hash = hash_word(word)
            self.word_hash_dct[word_hash].add(word)
        for word_hash in self.word_hash_dct:
            self.vowel_stat_dct[word_hash] = map(
                lambda w: vowels_stat(w),
                self.word_hash_dct[word_hash]
            )

    def default(self, line):
        word = self._prepare_word(line)
        word_hash = hash_word(word)
        if word in self.word_lst:
            print(word)
        elif word_hash in self.word_hash_dct:
            candidate_lst = self.word_hash_dct[word_hash]
            candidate_vowel_stat_lst = self.vowel_stat_dct[word_hash]
            suggestion = pick_suggestion(word, candidate_lst, candidate_vowel_stat_lst)
            if suggestion:
                print(suggestion)
            else:
                print(self.NO_SUGGESTION)
        else:
            print(self.NO_SUGGESTION)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--dict-file-name',
        action='store',
        dest='dict_file_name',
        default='words.txt',
        help='File with the BIG dictionary with english words'
    )
    options = vars(parser.parse_args())
    SpellCmd(**options).cmdloop()
