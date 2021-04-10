# -*- coding: utf-8 -*-

# Thomas N. T. Pham (nhpham@uni-potsdam.de)
# 09-Apr-2021
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
        case (bool): Case-sensitive string search if True,
            else case-insensitive.

    Attributes:
        pattern (str): String that is searched for.
        bad_char_heuristic (dict): Mapping of characters (str) as keys
            to indices (int) of their rightmost occurrence in the
            pattern.
        good_suffix_heuristic (list): Mapping of mismatch index to
            number of shifts that can be made, on the basis of an
            already matching suffix (= good suffix), without missing
            possible alignments.
        case (bool): Case-sensitive string search if True,
            else case-insensitive.
    """
    def __init__(self, pattern, case=True):
        if len(pattern) == 0:
            raise EmptyStringException("Invalid search string. Empty" +
                                       " strings are everywhere." +
                                       " Please try something with" +
                                       " characters.")
        if not case:
            pattern = pattern.lower()

        self._pattern = pattern
        self._bad_char_heuristic = self._rightmost_index_table(pattern)
        self._good_suffix_heuristic = self._good_suffix_shifts(pattern)
        self.case = case

    def naive(self, text):
        """Naive string matching algorithm (brute force).

        Args:
            text (str): Text that is searched for a pattern.

        Returns:
            list: Contains the indices of the pattern's occurrences.
        """
        if not self.case:
            text = text.lower()
        m = len(self._pattern)
        positions = []
        for shift in range(len(text) - m + 1):
            if self._pattern == text[shift:shift+m]:
                positions.append(shift)
        return positions

    def boyer_moore(self, text):
        """Boyer-Moore (BM) string matching algorithm according to the
        description by Cormen et al. (1990). In contrast to the naive
        algorithm, this BM algorithm reads the pattern from right to
        left and makes use of the pattern's inner structure to skip
        shifts and reduce the number of comparisons to be made.

        Args:
            text (str): Text that is searched for a pattern.

        Returns:
            list: Contains the indices of the pattern's occurrences.
        """
        if not self.case:
            text = text.lower()
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
                    j - self._bad_char_heuristic.get(text[shift+j], -1)
                    )
        return positions

    def search_file(self, file, encoding="utf-8", naive=False):
        """Searches text file for occurrences of a string.

        Args:
            file (str): Path to the text file which is to be searched
                for a particular string.
            encoding (str): File encoding. Defaults to utf-8.
            naive (bool): Naive search algorithm is used if True, else
                BM algorithm. Defaults to False.

        Returns:
            list: Contains 2-tuples consisting of a line number and a
                list of positions (int) in that line, e.g. for findings
                in line 2 and 56: [(2, [23, 41, 75]), (56, [45])].
        """
        search_func = self.naive if naive else self.boyer_moore
        line_positions = []
        try:
            with open(file, 'r', encoding=encoding) as read_f:
                for num, line in enumerate(read_f, start=1):
                    positions = search_func(line)
                    if positions:
                        line_positions.append((num, positions))
            return line_positions
        except FileNotFoundError as fnf:
            fnf_msg = file + " does not exist. Valid file path needed."
            logging.error(fnf_msg)
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except PermissionError as pe:
            pe_msg = file + " does not lead to a file."
            logging.error(pe_msg)
            raise FileNotFoundError(pe_msg).with_traceback(pe.__traceback__)
        except UnicodeDecodeError as ud:
            ud_msg = (f"{encoding} codec not proper for '{file}'." +
                      " Make sure it is a plain text file.")
            logging.error(ud_msg)
            raise UnicodeDecodeError(ud.encoding, ud.object, ud.start, ud.end,
                                     ud_msg).with_traceback(ud.__traceback__)

    def search_dir(self, dir, encoding="utf-8", naive=False):
        """Searches every txt-file in a directory for occurrences of a
        string.

        Args:
            dir (str): Path to the directory of which every containing
                txt-file is searched for a particular string.
            encoding (str): Encoding of the txt-files in the directory.
                Defaults to utf-8.
            naive (bool): Naive search algorithm is used if True, else
                BM algorithm. Defaults to False.

        Returns:
            dict: Each key is a filename and each value a list of
                2-tuples. These 2-tuples consist of a line number (int)
                and a list of positions (int) in that line, e.g. for
                findings in 'essay.txt' in line 2 and 56:
                {'essay.txt': [(2, [23, 41, 75]), (56, [45])],
                 'next_article.txt': ...}
        """
        doc_line_positions = dict()
        try:
            file_list = os.listdir(dir)
        except FileNotFoundError as fnf:
            fnf_msg = dir + " does not exist. Valid directory path needed."
            logging.error(fnf_msg)
            raise FileNotFoundError(fnf_msg).with_traceback(fnf.__traceback__)
        except NotADirectoryError as nad:
            nad_msg = dir + " does not lead to a directory."
            logging.error(nad_msg)
            raise NotADirectoryError(nad_msg).with_traceback(nad.__traceback__)
        for file in tqdm(file_list, desc="search directory...", leave=False):
            if file.endswith(".txt"):
                filepath = os.path.join(dir, file)
                location = self.search_file(filepath, encoding=encoding,
                                            naive=naive)
                if location:
                    doc_line_positions[file] = location
        return doc_line_positions

# private methods #
    @staticmethod
    def _rightmost_index_table(pattern):
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

    def _good_suffix_shifts(self, pattern):
        """Maps mismatch index to number of shifts that can be made
        without missing possible alignments of the already matching
        suffix (= good suffix).

        Args:
            pattern (str): String of which the possible shifts are
                calculated, depending on the index of the mismatch.

        Returns:
            list: Contains integer > 0.
        """
        shifts = []
        m = len(pattern)
        for j in range(m - 1):
            good_suffix = pattern[j+1:]  # at least one character
            rightmost_occ = self._rightmost_substr_start(good_suffix,
                                                         pattern[:-1])
            if rightmost_occ == -1:  # not found
                shifts.append(self._start_of_longest_sfx_as_pfx(good_suffix,
                                                                pattern))
            else:
                shifts.append(j + 1 - rightmost_occ)
        shifts.append(1)  # if mismatch at last index (no good suffix)
        return shifts

    @staticmethod
    def _rightmost_substr_start(subpattern, pattern):
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
    def _start_of_longest_sfx_as_pfx(suffix, pattern):
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


if __name__ == "__main__":
    print("######################## INITIALIZE DEMO #########################")
    pattern1 = "TGA"
    pattern2 = "evaluation"
    text = "tgaTGATCTGATAGAtaaCTACGTGATAGTGAtga"
    dir_path = "testdata"
    file_path = os.path.join(dir_path, "essay1.txt")
    print('')
    print("################## Find occurrences in a string ##################")
    print(f"Let us find the starting indices of '{pattern1}' in this DNA" +
          " sequence,\nusing the naive as well as the Boyer-Moore algorithm:")
    print(f">>> text = '{text}'")
    print(f">>> sm1 = StringMatcher('{pattern1}')")
    print(">>> print(sm1.naive(text))")
    sm1 = StringMatcher(pattern1)
    print(sm1.naive(text))
    print(">>> print(sm1.boyer_moore(text))")
    print(sm1.boyer_moore(text))
    print('')
    print("How about a case-insensitive search?")
    print(f">>> sm_insensitive = StringMatcher('{pattern1}', case=False)")
    print(">>> print(sm_insensitive.boyer_moore(text))")
    sm_insensitive = StringMatcher(pattern1, case=False)
    print(sm_insensitive.boyer_moore(text))

    print('')
    print("################## Find occurrences in one file ##################")
    print(f"Let us find the positions of '{pattern2}' in a text file,\n" +
          "using the Boyer-Moore algorithm:")
    print(f">>> file_path = '{file_path}'")
    print(f">>> sm2 = StringMatcher('{pattern2}')")
    print(">>> print(sm2.search_file(file_path, encoding='utf-8'))")
    sm2 = StringMatcher(pattern2)
    print(sm2.search_file(file_path, encoding="utf-8", naive=False))
    print("Hooray, this means we have occurrences in line 8 at index 11,\n" +
          "as well as in line 9 at index 12 and 24!")
    print('')
    print("How about using the naive algorithm instead?")
    print(">>> print(sm2.search_file(file_path, encoding='utf-8'," +
          " naive=True))")
    print(sm2.search_file(file_path, encoding="utf-8", naive=True))

    print('')
    print("######## Find occurrences in all txt-files of a directory ########")
    print(f"Let us find the positions of '{pattern2}' in all txt-files\n" +
          "of a directory using the Boyer-Moore algorithm:")
    print(f">>> dir_path = '{dir_path}'")
    print(f">>> sm2 = StringMatcher('{pattern2}')")
    print(">>> print(sm2.search_dir(dir_path, encoding='utf-8'))")
    print(sm2.search_dir(dir_path, encoding="utf-8", naive=False))
    print("Nice, we have found some occurrences in 'essay1.txt' in line 8\n" +
          "at index 11, in line 9 at index 12 and 24, and in 'paper1.txt'\n" +
          "in line 14 at index 73.")
    print('')
    print("If preferred, the naive algorithm can also be used of course!")
    print(">>> print(sm2.search_dir(dir_path, encoding='utf-8', naive=True))")
    print(sm2.search_dir(dir_path, encoding="utf-8", naive=True))
    print('')
    print("For more information please take a look at the Readme. Have fun!")
    print("############################ END DEMO ############################")
