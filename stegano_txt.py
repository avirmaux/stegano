#!/usr/bin/env python

import glob, os
import sys
import subprocess
import argparse

def secret_char(c):
    """
    Return correct XeLaTeX code for secret characters.
    """
    return "\\raisebox{{0.07ex}}{{{}}}".format(c)

def non_secret_char(c):
    """
    Return correct XeLaTeX code for non secret characters.
    """
    return c

def generate_tex(title, author, txt, indices=None):
    """
    Generate TeX file with title, author and txt shifted at `indices` places.
    """
    with open('head', 'r') as head,\
         open('stegano.tex', 'w') as file_tex:

    # First lines are
    # - Title
    # - Author

        file_tex.write("".join(head.readlines())) # Write heading
        file_tex.write("\\title{{{}}}\n".format(title))
        file_tex.write("\\author{{{}}}\n".format(author))
        file_tex.write("\\date{{}}\n")

        file_tex.write("\\begin{document}\n\\maketitle\n")

        # Write char by char, adding decoration when indices is reach
        i = 0
        while i < len(txt):
            if i in indices:
                file_tex.write(secret_char(txt[i]))
            else:
                file_tex.write(non_secret_char(txt[i]))
            i += 1

        file_tex.write("\\end{document}")

def subwords(txt, sub):
    """
    Return the indices of the first appearance of `sub` in `txt`.

    Return [] if `sub` is not a subword of `txt`.
    """
    txt = txt.lower()
    txt = txt.replace('’', '\'')
    sub = sub.lower().replace(' ', '')
    it = 0
    indices = []
    for c in sub:
        try:
            while txt[it] != c:
                it += 1
            indices.append(it)
        except (IndexError):
            print('Cannot find secret in text.')
            return []
    return indices

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--secret', help="secret message", type=str)
    args = parser.parse_args()

    secret = args.secret

    with open('octavie--nerval.txt', 'r') as file_in:
        title = file_in.readline().rstrip()
        author = file_in.readline().rstrip()
        txt = "".join(file_in.readlines())

        # secret = "jetaime"
        print("Looking for pattern... ", end='')
        sub = subwords(txt, secret)
        if sub == []:
            sys.exit(-1)
        print("Got it!")

    # Pipeline
    print("Generating TeX... ", end='')
    generate_tex(title, author, txt, sub)
    print("Done")
    print("Compiling... ", end='')
    latex_command = "xelatex stegano.tex"
    latex_compilation = subprocess.Popen(latex_command.split(), stdout=subprocess.PIPE)
    output, error = latex_compilation.communicate()
    if error != None:
        print(error)
    else:
        os.rename("stegano.pdf", "hide.pdf")
        print("Done")

    # Cleaning
    for dirty_file in glob.glob("stegano.*"):
        os.remove(dirty_file)

if __name__ == '__main__':
    main()
