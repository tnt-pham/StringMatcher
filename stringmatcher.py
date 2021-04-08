# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 08-Apr-2021
# Python 3.7
# Windows 10
"""String matching tool."""

import logging
import os

from tqdm import tqdm

from errors import EmptyStringException


logging.basicConfig(filename="stringmatcher_log.log",
                    level=logging.INFO,
                    format="%(levelname)s:%(asctime)s:%(message)s")


class StringMatcher:
    """Provides two string search algorithms to determine the positions
    in a text.

    Args:
        pattern (str): String that is searched for.

    Attributes:
        pattern (str): String that is searched for.
        bad_char_heuristic (dict): Mapping of characters (str) as keys
            to indices (int) of their rightmost occurrence in the
            pattern.
        good_suffix_heuristic (list): Mapping of mismatch index to
            number of shifts that can be made, on the basis of an
            already matching suffix (= good suffix), without missing
            possible alignments.
    """
    def __init__(self, pattern):
        if len(pattern) == 0:
            raise EmptyStringException("Invalid search string. Empty" +
                                       " strings are everywhere." +
                                       " Please try something with" +
                                       " characters.")
        self._pattern = pattern
        self._bad_char_heuristic = self.rightmost_index_table(pattern)
        self._good_suffix_heuristic = self._good_suffix(pattern)

    def naive(self, text):
        """Naive string matching algorithm (brute force).

        Args:
            text (str): Text that is searched for a pattern.

        Returns:
            list: Contains the indices of the pattern's occurrences.
        """
        m = len(self._pattern)
        positions = []
        for shift in range(len(text) - m + 1):
            if self._pattern == text[shift:shift+m]:
                positions.append(shift)
        return positions

    def boyer_moore(self, text):
        """Boyer-Moore (BM) string matching algorithm according to the
        description by Cormen et al. (1990). In contrast to the naive
        algorithm, this BM algorithm makes use of the pattern's
        inner patterns to skip shifts and reduce the number of
        comparisons to be made.
        
        Args:
            text (str): Text that is searched for a pattern.

        Returns:
            list: Contains the indices of the pattern's occurrences.
        """
        m = len(self._pattern)
        shift = 0
        positions = []
        while shift <= len(text) - m:
            j = m - 1  # last character in pattern
            while j > -1 and self._pattern[j] == text[shift+j]:
                j -= 1
            if j == -1:  # complete match found
                positions.append(shift)
                shift += self._good_suffix_heuristic[0]
            else:  # mismatch at index j
                shift += max(
                    self._good_suffix_heuristic[j],
                    j - self._bad_char_heuristic.get(text[shift+j], -1))  ############################################################ TODO
        return positions

    def search_file(self, file, encoding="utf-8", naive=False):
        """Searches file for occurrences of a string.

        Args:
            file (str): Path to the file which is to be searched for
                a particular string.
            encoding (str): File encoding. Defaults to utf-8.

        Returns:
            list: Contains 2-tuples consisting of a line number and a
                list of positions (int) in that line, e.g. for findings
                in line 2 and 56: [(2, [23, 41, 75]), (56, [45])].
        """
        line_positions = []
        try:
            with open(file, 'r', encoding=encoding) as read_f:
                if naive:
                    for num, line in enumerate(read_f, start=1):
                        line_positions.append((num, self.naive(line)))
                else:  # BM algorithm
                    for num, line in enumerate(read_f, start=1):
                        line_positions.append((num, self.boyer_moore(line)))
            return line_positions
        except FileNotFoundError as fnf:
            fnf_msg = file + " does not exist. Valid file path needed."
            logging.error(fnf_msg)
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except PermissionError as pe:
            pe_msg = file + " does not lead to a file."
            logging.error(pe_msg)
            raise FileNotFoundError(pe_msg).with_traceback(pe.__traceback__)

    def search_dir(self, dir, encoding="utf-8", naive=False):
        """Searches every file in a directory for occurrences of a
        string.

        Args:
            dir (str): Path to the directory of which every containing
                file is searched for a particular string.
            encoding (str): Encoding of the files in the directory.
                Defaults to utf-8.
            naive (bool): Naive search algorithm is used if True, else
                BM algorithm.

        Returns:
            dict: Each key is a filename and each value a list of
                2-tuples. These 2-tuples consist of a line number (int)
                and a list of positions (int) in that line, e.g. for
                findings in 'essay.txt' in line 2 and 56:
                {'essay.txt': [(2, [23, 41, 75]), (56, [45])],
                 'next_article.txt': ...}
        """
        doc_line_positions = dict()
        try:  # os.listdir vorher speichern in try, rest außerhalb
            for file in tqdm(os.listdir(dir), desc="search directory..."):
                filepath = os.path.join(dir, file)
                doc_line_positions[file] = self.search_file(filepath,
                                                            encoding=encoding,
                                                            naive=naive)
            return doc_line_positions
        except FileNotFoundError as fnf:
            fnf_msg = dir + " does not exist. Valid directory path needed."
            logging.error(fnf_msg)
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except NotADirectoryError as nad:
            nad_msg = dir + " does not lead to a directory."
            logging.error(nad_msg)
            raise NotADirectoryError(nad_msg).with_traceback(nad.__traceback__)

    @staticmethod
    def rightmost_index_table(pattern):
        """Retrieves rightmost index of each character which occurs in
        the pattern, e.g. for 'bob' the rightmost index of 'b' is 2 and
        of 'o' is 1.

        Args:
            pattern (str): String of which the characters's rightmost
                indices are retrieved.

        Return:
            dict: Contains characters (str) as keys and indices (int)
                as values.
        """
        char_index_table = dict()
        for j in range(len(pattern)):
            char_index_table[pattern[j]] = j
        return char_index_table

    def _good_suffix(self):
        """Maps mismatch index to number of shifts that can be made
        without missing possible alignments of the already matching
        suffix (= good suffix).
        """
        shifts = []
        m = len(self._pattern)
        for j in range(m - 1):  # without last index
            good_suffix = self._pattern[j+1:]  # at least one character
            # always left to j+1
            rightmost_occ = self.rightmost_substr_start(good_suffix,
                                                        self._pattern[:-1])
            if rightmost_occ == -1:
                shifts.append(self.start_of_longest_sfx_as_pfx(good_suffix,
                                                               self._pattern))
                continue
            shifts.append(j + 1 - rightmost_occ)
        shifts.append(1)  # if mismatch at last index (no good suffix)
        return shifts  # list containing ints > 0

    @staticmethod
    def rightmost_substr_start(subpattern, pattern):
        """Finds starting index of rightmost occurrence of substring
        in pattern if existing.

        Args:
            subpattern (str): Substring that is searched for.
            pattern (str): String that is searched.

        Returns:
            int: Starting index of rightmost occurrence if existing,
                else -1.
        """
        m = len(subpattern)
        for i in range(len(pattern) - m, -1, -1):  # naive string search
            if subpattern == pattern[i:i+m]:
                return i
        return -1

    @staticmethod
    def start_of_longest_sfx_as_pfx(suffix, pattern):
        """Determines starting index of longest suffix (of suffix) which
        is also a prefix of the pattern.
        
        Args:
            suffix (str): Suffix of pattern of which the longest suffix
                is ascertained.
            pattern (str): String of which the starting index is
                determined.

        Returns:
            int: Starting index in the pattern of longest suffix.
        """
        while True:
            suffix = suffix[1:]
            # at the latest fulfilled in case of empty string
            if pattern.startswith(suffix):
                return len(pattern) - len(suffix)




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
