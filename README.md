This project was written on Windows 10, Python 3.7.3.  
Visit me on [GitHub](https://github.com/thommy24/StringMatcher) for latest updates and infos!

## NAME
main.py - command line tool for string search in a string, a file or a directory.

## DESCRIPTION
String matching is a task that is encountered often and in various fields. Be it an automatic system identifying plagiarism, biologists searching for a particular DNA sequence or solely a person trying to find a certain word in a text file, there are different application areas and as it happens there are different string matching algorithms as well. Each one has its strengths and weaknesses, but depending on our purpose we can select the most appropriate one.

This command line tool uses the Boyer-Moore algorithm, which tends to be faster the longer the search string and the larger the alphabet is, but the naive algorithm is implemented as well and can be chosen if wanted. The program provides the means to search for a string (= concatenation of characters) in a text, in a text file or in all txt-files of a directory and returns the positions of the occurrences, e.g. the starting indices if a text is searched. Additionally, a case-insensitive search is also possible. However, be aware of the limitation that in files, no search strings that exceed more than one line can be found since the text is read line by line. Hence, the search string should not contain any newline characters when searching a file or directory.

Keep in mind that line numbers in files start at 1 while the column indices start at 0.

##  REQUIREMENTS
- install dependencies (make sure you are located in the project's root directory when executing the following command)  
> python -m pip install -r requirements.txt  
- alternatively: `python -m pip install tqdm`
- a text, a text file or a directory with txt-files of your choice that is searched

## SYNOPSIS
- show command line syntax and more information on arguments
> python main.py --help

- options overview
> python main.py [-h, --help] [-t, --text STRING | -f, --file FILE | -d, --dir DIR] [--search SEARCHSTRING] [--encoding ENC] [-i, --insensitive] [--naive]

- search in another string
> python main.py --search SEARCHSTRING --text STRING

- search in a text file
> python main.py --search SEARCHSTRING --file FILE [--encoding ENC]?

- search in all txt-files of a directory
> python main.py --search SEARCHSTRING --dir DIR [--encoding ENC]?

- additional settings:
    - case-insensitive search in another string
    > python main.py --search SEARCHSTRING --text STRING --insensitive

    - use the naive search algorithm (instead of Boyer-Moore):
    > python main.py --search SEARCHSTRING --text STRING --naive

- Side notes:
    - You can use either `--text`, `--file` or `--dir` at once.
    - Additionally, you can combine the settings `--insensitive` and `--naive`, also while searching in a file or directory.

### ARGUMENTS
- SEARCHSTRING
    - string (= concatenation of characters) that is to be searched
    - should not contain newline characters when searching a file or directory (otherwise no occurrences)
    - regular expressions cannot be used
- STRING
    - text that is searched for the search string
- FILE
    - path to/name of a text file
    - is searched for the search string
- DIR
    - path to/name of a directory
    - contained txt-files are searched for the search string
    - contained subdirectories are **not** searched
- ENC
    - encoding such as `utf-8`, `utf-16`, `utf-32`, `windows-1250`, `big5`, `latin-1`, `ascii`, ...
    - defaults to `utf-8`
    - can be specified for FILE or DIR
- Side note:
    - make sure to enclose the argument with quotation marks `""`

### EXAMPLES
- search in another string  
`python main.py --search "world" -t "Hello, World! This is a wonderful world."`
    - case-insensitive search in another string  
    `python main.py --search "world" -t "Hello, World! This is a wonderful world." -i`
    - search in another string using the naive algorithm (instead of Boyer-Moore)  
    `python main.py --search "world" -t "Hello, World! This is a wonderful world." --naive`

- search in a utf-8-encoded text file  
`python main.py --search "evaluation" -f "testdata\\essay1.txt"`

- search all txt-files of a directory  
`python main.py --search "evaluation" -d "testdata" --encoding "utf-8"`

## AUTHOR
Thomas N. T. Pham  
University of Potsdam, April 2021  
[My Github](https://github.com/thommy24/StringMatcher)  
For more information or questions, feel free to contact nhpham@uni-potsdam.de
