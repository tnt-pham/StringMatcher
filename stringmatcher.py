# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 08-Apr-2021
# Python 3.7
# Windows 10
"""String matching tool."""

import logging
import os

from errors import EmptyStringException


logging.basicConfig(filename="stringmatcher_log.log",
                    level=logging.INFO,
                    format="%(levelname)s:%(asctime)s:%(message)s")


class StringMatcher:
    """Provides two string search algorithms to determine the positions
    in a text.

    Args:
        pattern (str): String which should be searched for.

    Attributes:
        pattern (str): String which should be searched for.
        TODO
    """
    def __init__(self, pattern):
        if len(pattern) == 0:
            raise EmptyStringException("Invalid search string. Empty" +
                                       " strings are everywhere." +
                                       " Please try something with" +
                                       " characters.")
        self.pattern = pattern
        self.bad_char_heuristic = self._rightmost_index(pattern)  # dict
        self.good_suffix_heuristic = self._good_suffix(pattern)  # list

    def naive(self, text):
        """Naive string matching algorithm (brute force)."""
        m = len(self.pattern)
        positions = []
        for shift in range(len(text) - m + 1):
            if self.pattern == text[shift:shift+m]:
                positions.append(shift)
        return positions

    def boyer_moore(self, text):
        """According to the description by Cormen et al. (1990)."""
        m = len(self.pattern)
        shift = 0
        positions = []
        while shift <= len(text) - m:  # ok
            j = m - 1  # last character in pattern
            while j > -1 and self.pattern[j] == text[shift+j]:
                j -= 1
            if j == -1:  # complete match found
                positions.append(shift)
                shift += self.good_suffix_heuristic[0]  # mismatch at 0 or not does not make a difference since pattern passes this char anyway
            else:  # mismatch at index j
                shift += max(self.good_suffix_heuristic[j],
                             j - self.bad_char_heuristic.get(text[shift+j], -1))
        return positions


    def search_file(self, filename, encoding="utf-8", boyer_moore=True):
        line_positions = []  # filled with 2-tuples containing line number and a list of positions
        try:
            with open(filename, 'r', encoding=encoding) as read_f:
                if boyer_moore:
                    for num, line in enumerate(read_f, start=1):
                        line_positions.append((num, self.boyer_moore(line)))
                else:  # naive search
                    for num, line in enumerate(read_f, start=1):
                        line_positions.append((num, self.naive(line)))
            return line_positions
        except FileNotFoundError as fnf:
            fnf_msg = filename + " does not exist. Valid file path needed."
            logging.error(fnf_msg)
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except PermissionError as pe:
            pe_msg = filename + " does not lead to a file."
            logging.error(pe_msg)
            raise FileNotFoundError(pe_msg).with_traceback(pe.__traceback__)

    def search_dir(self, dirname, encoding="utf-8", boyer_moore=True):
        doc_line_positions = dict()
        try:  # maybe catch errors earlier?
            for file in os.listdir(dirname):
                filepath = os.path.join(dirname, file)
                doc_line_positions[file] = self.search_file(filepath,
                                                            encoding=encoding,
                                                            boyer_moore=boyer_moore)
            return doc_line_positions
        except FileNotFoundError as fnf:
            fnf_msg = dirname + " does not exist. Valid directory path needed."
            logging.error(fnf_msg)
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except NotADirectoryError as nad:
            nad_msg = dirname + " does not lead to a directory."
            logging.error(nad_msg)
            raise NotADirectoryError(nad_msg).with_traceback(nad.__traceback__)

    # private methods #
    # okay
    def _rightmost_index(self, pattern):  # need alphabet?
        """Saves rightmost index of each character in the pattern."""
        rightmost_index = dict()  # rename?
        for j in range(len(pattern)):
            rightmost_index[pattern[j]] = j
        return rightmost_index

    def _good_suffix(self):  # always return > 0
        """Maps mismatch index to number of shifts that can be made
        without missing possible alignments of the matching suffix."""
        shifts = []  # maps indices of mismatches to valid shifts
        m = len(self.pattern)
        for j in range(m - 1):  # bis vorletzen?
            good_suffix = self.pattern[j+1:]  # at least one character
            rightmost_occurrence = self._rightmost_start_of_substr(good_suffix, self.pattern[:-1])  # always left to j+1
            if rightmost_occurrence == -1:
                shifts.append(self._start_of_longest_sfx_as_pfx(good_suffix, self.pattern))
                continue
            shifts.append(j + 1 - rightmost_occurrence)  # always positive
        shifts.append(1)  # shift 1 if rightmost character mismatches (no good suffix)
        return shifts

    # okay
    def _rightmost_start_of_substr(self, subpattern, pattern):
        """Returns start index of rightmost occurrence of a substring."""
        m = len(subpattern)
        for i in range(len(pattern)-m, -1, -1):  # naive string search
            if subpattern == pattern[i:i+m]:
                return i
        return -1

    def _start_of_longest_sfx_as_pfx(self, suffix, pattern):
        """Returns start index of longest suffix which is a prefix of
        the pattern."""
        while len(suffix) > 1:  # while True
            suffix = suffix[1:]
            if pattern.startswith(suffix):
                return len(pattern) - len(suffix)
        return len(pattern)  # redundant




# def _good_suffix_heuristic(pattern):
#     longest_prefix = _prefix(pattern)
#     longest_prefix_reversed = _prefix(pattern[::-1])
#     m = len(pattern)
#     good_suffix = dict()
#     for j in range(m):
#         good_suffix[j] = m - longest_prefix[m - 1]
#     for l in range(1, m):
#         j = m - longest_prefix_reversed[l] - 1
#         if good_suffix[j] > l - longest_prefix_reversed[l]:
#             good_suffix[j] = l - longest_prefix_reversed[l]
#     return good_suffix


# # okay maybe
# def _prefix(pattern):
#     longest_prefix = {0: 0}  # len of longest prefix that is suffix for pattern[:key]
#     k = 0
#     for q in range(1, len(pattern)):
#         while k > 0 and pattern[k] != pattern[q]:
#             k = longest_prefix[k - 1]  # k-1???
#         if pattern[k] == pattern[q]:
#             k += 1
#         longest_prefix[q] = k
#     return longest_prefix





if __name__ == "__main__":
    pattern = "holala"
    text = "he holala hallo hola hola hola\n ha holalalaho hos hola hola holala"
    sm = StringMatcher(pattern)
    print(sm.naive(text))
    print(sm.boyer_moore(text))
    print(sm._good_suffix())
