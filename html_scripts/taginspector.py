from html.parser import HTMLParser
import fnmatch
import glob
import sys
import os

class MyHTMLParser(HTMLParser):

    opened = []
    unopened = []

    def handle_starttag(self, tag, attrs):
        self.opened.append(tag)

    def handle_endtag(self, tag):
        if tag in self.opened:
            self.opened.remove(tag)
        else:
            self.unopened.append(tag)

    def show_results(self):
        if self.opened:
            print('\tFile contains unclosed tags! [' + ', '.join(self.opened) + ']')
        if self.unopened:
            print('\tFile contains unopened tags! [' + ', '.join(self.unopened) + ']')

    def clean(self):
        self.opened.clear()
        self.unopened.clear()

def scan_files(extension):
        for root, _, filenames in os.walk('.'):
                for filename in fnmatch.filter(filenames, '*.' + extension):
                        analyze_file(os.path.join(root, filename))

def analyze_file(filename):
    print('Analyzing file \'' + filename + '\'')
    parser = MyHTMLParser()
    with open(filename) as f:
        try:
            parser.feed(f.read())
            parser.show_results()
            parser.clean()
        except UnicodeDecodeError :
            print("File " + filename + " is encoded with not supported charset, only UTF-8 are allowed!")


if len(sys.argv) >= 2 :
    for arg in sys.argv[1:]:
        
        print('**** Scanning for extension .' + arg + ' ****')
        scan_files(arg)
else:
    print("USAGE:")
    print("python3 taginspector.py [list of extensions]")