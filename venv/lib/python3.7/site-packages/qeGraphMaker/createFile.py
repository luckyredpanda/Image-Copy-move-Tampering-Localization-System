import readline
import qeGraphMaker.apiRequest as apiRequest
import re
import argparse


class MyCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = options

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


def main():

    flags = ["update"]
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required = False,
            help="Output txt file, out.txt by default", default = "out.txt")

    req = apiRequest.QEdataRequest()

    print("This tool is for creating txt files which are of proper form so that they" \
            "can be called with xeqt.py, which makes a PDF booklet. Use tab for autocomplete")

    def writeLine():
        ###########################################################################
        validCards = req.validCards()
        completer = MyCompleter(["next"] + validCards)
        readline.set_completer(completer.complete)
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims("\n\r")
        cards = []
        while(True):
            userIn = input("Enter desired card ('next' to continue): ").strip()
            if(userIn == "next"):
                if(not cards):
                    print("No input for card")
                    continue
                break
            if(not userIn in validCards):
                print("Invalid card name")
                continue
            cards.append(userIn)
        ###########################################################################

        validTests = req.validTests()
        completer = MyCompleter(validTests)
        readline.set_completer(completer.complete)

        test = input("Enter test name: ").strip()
        while(not test in validTests):
            print("Invalid test name")
            test = input("Enter test name: ").strip()
        ###########################################################################

        validSubtests = req.validSubtests(test)
        completer = MyCompleter(validSubtests)
        readline.set_completer(completer.complete)

        subtest = input("Enter subtest name: ").strip()
        while(not subtest in validSubtests):
            print("Invalid subtest name")
            subtest = input("Enter subtest name: ").strip()

        ###########################################################################

        validTypes = req.validTypes(test, subtest)
        completer = MyCompleter(validTypes)
        readline.set_completer(completer.complete)

        type = input("Enter type: ").strip()
        while(not type in validTypes):
            print("Invalid type")
            type = input("Enter type: ").strip()
        ###########################################################################

        validLabels = req.validLabels(test, subtest, type)
        completer = MyCompleter(["next"] + validLabels)
        readline.set_completer(completer.complete)

        labels = []
        while(True):
            userIn = input("Enter desired label ('next' to continue): ").strip()
            if(userIn == "next"):
                if(not labels):
                    print("No input for label")
                    continue
                break
            if(not userIn in validLabels):
                print("Invalid label")
                continue
            labels.append(userIn)
        ###########################################################################

        completer = MyCompleter([])
        readline.set_completer(completer.complete)
        start = input("Enter start date of the form YYYY-MM-DD: ")
        end = input("Enter end date of the form YYYY-MM-DD: ")

        completer = MyCompleter(["next"] + flags)
        readline.set_completer(completer.complete)
        my_flags=[]
        while(True):
            userIn = input("Enter flag ('next' to continue): ").strip()
            if(userIn == "next"):
                break
            if(not userIn in flags):
                print("Invalid flag")

            my_flags.append(userIn)

        array = [",".join(cards), test, subtest, type, ",".join(labels), start, end, ",".join(my_flags)]

        return ":".join(array) + "\n"


    def createFile():

        pdfName = input("Enter the name of the PDF which you want to create: ").strip()
        if(pdfName == ""):
            raise IOError("No name provided")

        if(not re.match(r'^.+\.pdf$', pdfName)):
            pdfName += ".pdf"

        toWrite = pdfName + "\n"

        toWrite = toWrite + writeLine()

        while(True):
            userIn = input("Would you like to make another page (y/n)? ").strip()
            if(userIn.lower() == "n" or userIn.lower() == "no"):
                break
            elif(userIn.lower() != "y" and userIn.lower() != "yes"):
                print("Input not recognized")
                continue

            toWrite = toWrite + writeLine()

        fo = open(parser.parse_args().output, "w")
        fo.write(toWrite)
        fo.close()

    createFile()

if __name__ ==  "__main__":
    main()
