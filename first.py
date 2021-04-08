# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 01-Apr-2021
# Python 3.7
# Windows 10
"""String matching tool."""

import logging
import os


logging.basicConfig(filename="stringmatching_log.log",
                    level=logging.INFO,
                    format="%(levelname)s:%(asctime)s:%(message)s")


class StringMatcher:

    def naive(self, pattern, text):
        """Naive string matching algorithm (brute force)."""
        m = len(pattern)
        positions = []
        for shift in range(len(text) - m + 1):
            if pattern == text[shift:shift+m]:
                positions.append(shift)
        return positions

    def boyer_moore(self, pattern, text):
        """According to Cormen et al. (1990)."""
        bad_character = self._rightmost_index(pattern)  # dict
        good_suffix = self._good_suffix(pattern)  # list
        m = len(pattern)
        shift = 0
        positions = []
        while shift <= len(text) - m:  # ok
            j = m - 1  # last character in pattern
            while j > -1 and pattern[j] == text[shift+j]:
                j -= 1
            if j == -1:  # complete match found
                positions.append(shift)
                shift += good_suffix[0]  # TODO
            else:  # mismatch at index j
                shift += max(good_suffix[j],
                             j - bad_character.get(text[shift+j], -1))
        return positions

    # okay
    def _rightmost_index(self, pattern):  # need alphabet?  # need m?
        """Saves rightmost index of each character in the pattern."""
        last_occurrence = dict()  # rename?
        for j in range(len(pattern)):
            last_occurrence[pattern[j]] = j
        return last_occurrence

    def _good_suffix(self, pattern):  # always return > 0
        """Maps mismatch index to number of shifts that can be made
        without missing possible alignments of the matching suffix."""
        shifts = []  # maps indices of mismatches to valid shifts
        m = len(pattern)
        for j in range(m - 1):  # bis vorletzen?
            good_suffix = pattern[j+1:]  # at least one character
            rightmost_occurrence = self._rightmost_start_of_substr(good_suffix, pattern[:-1])  # always left to j+1
            if rightmost_occurrence == -1:
                shifts.append(self._start_of_longest_suffix_as_prefix(good_suffix, pattern))
                continue
            shifts.append(j + 1 - rightmost_occurrence)  # always positive
        shifts.append(1)  # shift 1 if rightmost character mismatches (no good suffix)
        return shifts

    # okay
    def _rightmost_start_of_substr(self, substring, string):
        """Returns start index of rightmost occurrence of substring."""
        m = len(substring)
        for i in range(len(string)-m, -1, -1):
            if substring == string[i:i+m]:  # naive string search which stops after first finding
                return i
        return -1

    def _start_of_longest_suffix_as_prefix(self, subpattern, pattern):
        """Returns start index of longest suffix of subpattern which is
        prefix of pattern."""
        while len(subpattern) > 1:  # while True
            subpattern = subpattern[1:]
            if pattern.startswith(subpattern):
                return len(pattern) - len(subpattern)
        return len(pattern)  # redundant

    def read_file(self, pattern, filename, encoding="utf-8"):
        line_shifts = []
        try:
            with open(filename, 'r', encoding=encoding) as read_f:
                for num, line in enumerate(read_f):
                    line_shifts.append((num, self.boyer_moore(line, pattern)))
            return line_shifts
        except FileNotFoundError:
            pass
        except PermissionError:
            pass

    def read_dir(self, pattern, dirname, encoding="utf-8"):
        doc_line_shifts = dict()
        try:
            for file in os.listdir(dirname):
                doc_line_shifts[file] = read_file(pattern, file, encoding=encoding)
        except NotADirectoryError:
            pass
        except FileNotFoundError:
            pass
















def _good_suffix_heuristic(pattern):
    longest_prefix = _prefix(pattern)
    longest_prefix_reversed = _prefix(pattern[::-1])
    m = len(pattern)
    good_suffix = dict()
    for j in range(m):
        good_suffix[j] = m - longest_prefix[m - 1]
    for l in range(1, m):
        j = m - longest_prefix_reversed[l] - 1
        if good_suffix[j] > l - longest_prefix_reversed[l]:
            good_suffix[j] = l - longest_prefix_reversed[l]
    return good_suffix


# okay maybe
def _prefix(pattern):
    longest_prefix = {0: 0}  # len of longest prefix that is suffix for pattern[:key]
    k = 0
    for q in range(1, len(pattern)):
        while k > 0 and pattern[k] != pattern[q]:
            k = longest_prefix[k - 1]  # k-1???
        if pattern[k] == pattern[q]:
            k += 1
        longest_prefix[q] = k
    return longest_prefix





if __name__ == "__main__":
    # text = "halloha\nhalloha my name is halloha hall halloh"
    # pattern = "halloha"
    # text = "abababbbcababa"
    # pattern = "ababbabacab"
    # print(naive_string_matcher(text, pattern))
    # print(boyer_moore_matcher(text, pattern))
    # print(_good_suffix_heuristic(pattern))
    # print(_prefix(pattern))

    # sm = StringMatcher()
    pattern = "holala"
    text = "he holala hallo hola hola hola ha holalalaho hos hola hola holala"
    # print(sm.naive(pattern, text))
    # # TODO: change dictionaries to lists
    # print(_rightmost_index("hallimallo"))
    # print(_rightmost_start_of_substr("bab", "ababa"))
    # print(_good_suffix("hausmaus"))
    sm = StringMatcher()
    print(sm.naive(pattern, text))
    print(sm.boyer_moore(pattern, text))
    print(sm._good_suffix("ababbabacab"))
