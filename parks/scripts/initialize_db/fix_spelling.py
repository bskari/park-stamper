#!/bin/python
"""Fixes some common spelling errors in the master list. Might I add that this
is one of the reasons why having a website is useful?
"""
import os
import sys


def levenshtein_ratio(s1, s2, cutoff=None):
    max_len = max(len(s1), len(s2))
    if cutoff is not None:
        cutoff = int(math.ceil((1.0 - cutoff) * max_len) + .1)
    return 1.0 - (
        float(levenshtein(s1, s2, cutoff=cutoff))
        / max_len
    )


def levenshtein(s1, s2, cutoff=None):
    """Compute the Levenshtein edit distance between two strings. If the
    minimum distance will be greater than cutoff, then quit early and return
    at least cutoff.
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1, cutoff)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        current_row_min = sys.maxint
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            min_all_three = min(
                insertions,
                deletions,
                substitutions
            )
            current_row.append(min_all_three)
            current_row_min = min(current_row_min, min_all_three)

        if cutoff is not None and current_row_min > cutoff:
            return current_row_min
        previous_row = current_row

    return previous_row[-1]


def fix_misspellings(test=None):
    if test is None:
        test = False

    words = (
        'Bonus',
        'Cemetery',
        'Heritage',
        'Historic',
        'Historical',
        'Monument',
        'Memorial',
        'National',
        'Park',
        'Preserve',
        'Recreation',
        'Recreational',
        'Scenic',
    )

    ok_words = (
        'Hermitage',
        'History',
        'Presence',
        'Reception',
        'Reservation',
        'Renovation',
        'Parks',
        'Part',
    )

    for word in words:
        command = r"grep -i -P -o '\b[{first_letter}][a-z]{{{length_minus_one},{length_plus_one}}}\b' master_list.csv | sort -u".format(
            first_letter=word[0],
            length_minus_one=(len(word[1:]) - 1),
            length_plus_one=(len(word[1:]) + 1),
        )

        if test:
            print('Running {command}'.format(command=command))

        maybe_misspellings = os.popen(command).readlines()
        # Trim newlines
        maybe_misspellings = [m[:-1] for m in maybe_misspellings]
        # Ignore the correct spelling
        for j in (word, word.lower(), word.upper()):
            if j in maybe_misspellings:
                maybe_misspellings.remove(j)
        # Ignore ok words
        for i in ok_words:
            for j in (i, i.lower(), i.upper()):
                if j in maybe_misspellings:
                    maybe_misspellings.remove(j)
        # 'Recreationa' => 'Recreational', not 'Recreation'
        removals = []
        for mm in maybe_misspellings:
            if word == 'Historic' or word == 'Recreation':
                if 'a' in mm[-3:].lower() or 'l' in mm[-3:].lower():
                    removals.append(mm)
        for r in removals:
            maybe_misspellings.remove(r)


        # Misspellings must have most of the letters from the word
        misspellings = [mm for mm in maybe_misspellings if levenshtein_ratio(mm[1:].lower(), word[1:].lower()) >= .65]

        for misspelling in misspellings:

            if misspelling == misspelling.upper():
                replacement = word.upper()
            elif misspelling == misspelling.lower():
                replacement = word.lower()
            else:
                replacement = word

            if test:
                print(
                    '{word} found {times} times'.format(
                        word=misspelling,
                        times=os.popen(
                            r"grep -c -P '\b{word}\b' master_list.csv".format(
                                word=misspelling,
                            )
                        ).readlines()[0][:-1],
                    )
                )
                print(
                    'Replacing {word} with {replacement}'.format(
                        word=misspelling,
                        replacement=replacement,
                    )
                )
            else:

                os.system(
                    r"sed -i -r 's/\b{misspelling}\b/{replacement}/g' master_list.csv".format(
                        misspelling=misspelling,
                        replacement=replacement,
                    )
                 )

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {program} [--test|--run]'.format(program=sys.argv[0]))
        sys.exit(1)
    elif sys.argv[1] == '--test':
        fix_misspellings(test=True)
    elif sys.argv[1] == '--run':
        fix_misspellings(test=False)
        # Fix whte space too
        os.system(r"sed -i -r 's/\s+$//' master_list.csv")
    else:
        print('Usage: {program} [--test|--run]'.format(program=sys.argv[0]))
        sys.exit(1)
