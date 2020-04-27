import os
import matplotlib

if not "DISPLAY" in os.environ:
    matplotlib.use('Agg')

import qeGraphMaker.graph as graph
from matplotlib.backends.backend_pdf import PdfPages
import re
from qeGraphMaker.apiRequest import QEdataRequest
import qeGraphMaker.helper as helper
from datetime import datetime,date


validPdfName = r'^\w+\.pdf$'
validDate = r'^(19\d{2}|20\d{2})\-(0[1-9]|1[0-2])\-([0-2]\d|3[0-1])$'


class MultiGraph():
    def __init__(self, fileName):
        self.fileName = fileName
        self.pdfName = ""
        self.graphs = []
        self.appReq = QEdataRequest()
        self.flags = {"update":self.update}

    def update(self, start, end, **kwargs):
        startMonth = start[0:7]
        endMonth = end[0:7]
        self.appReq.update(startMonth, endMonth)


    def construct(self):
        lineNum = 1
        pdfName = ""
        graphs = []   # new empty non-instance variables allow for nonassignment if input is invalid
        options = []
        fileOb = open(self.fileName, "r")
        pdfName = fileOb.readline().rstrip()
        if(not re.match(validPdfName, pdfName)):
            message = "Line {0:d}: {} is not a valid name for a pdf please have it of form \w+.pdf"
            raise IOError(message.format(lineNum, fileName))

        lineNum = 2

        for line in fileOb:
            line = line.rstrip()
            options = line.split(":")

            if(len(options) < 7 or len(options) > 8):
                message = "Line {}: Not enough arguments provided, needed 7 or 8 seperated by ':' but got {}"
                raise IOError(message.format(lineNum, len(options)))
            elif(len(options) > 8):
                message = "Line {}: Too many arguments provided, needed 7 or 8 seperated by ':' but got {}"
                raise IOError(message.format(lineNum, len(options)))

            cards = set(options[0].split(","))
            cardReg = helper.regFromList(self.appReq.validCards())

            for card in cards:
                if(not re.match(cardReg, card)):
                    message = "Line {}: {} is not a valid card name. Valid names are: {}"
                    raise IOError(message.format(lineNum, card, ", ".join(structure[cards])))

            test = options[1]
            testReg = helper.regFromList(self.appReq.validTests())

            if(not re.match(testReg, test)):
                message = "Line {}: {} is not a valid test name"
                raise IOError(message.format(lineNum))

            subtest = options[2]
            subtestReg = helper.regFromList(self.appReq.validSubtests(test))

            if(not re.match(subtestReg, subtest)):
                message = "Line {}: {} is not a valid subtest choice with current selection: test={}"
                raise IOError(message.format(lineNum, subtest, test))

            type = options[3]
            typeReg = helper.regFromList(self.appReq.validTypes(test, subtest))

            if(not re.match(typeReg, type)):
                message = "Line {}: {} is not a valid type option with current selection: test={}, subtest={}"
                raise IOError(message.format(lineNum, type, test, subtest))

            labels = set(options[4].split(","))

            labelReg = helper.regFromList(self.appReq.validLabels(test, subtest, type))
            for label in labels:
                if(not re.match(labelReg, label)):
                    message = "Line {}: {} is not a valid label option with current selection: test={}, subtest={}, type={}"
                    raise IOError(message.format(lineNum, label, test, subtest, type))

            start = options[5]

            if(start == "earliest"):
                minDate = int((datetime.now() - datetime.fromtimestamp(0)).total_seconds())
                for card in cards:
                    dates = map(lambda x: x["datetime"], self.appReq.getData(cardName = card,
                                                                             test = test,
                                                                             subtest = subtest,
                                                                             type = type ))
                    curMin = min(dates)
                    minDate = min(curMin, minDate)
                start = date.fromtimestamp(minDate).isoformat()


            if(not re.match(validDate, start) and start != "earliest"):
                message = "Line {}: {} is not a valid format for start date"
                raise IOError(message.format(lineNum, start))

            end = options[6]

            if(end == "today"):
                end = date.today().isoformat()

            if(not re.match(validDate, end) and end != "today"):
                message = "Line {}: {} is not a valid format for end date"
                raise IOError(message.format(lineNum, end))

            if(end == "today"):
                datetime.now().date().isoformat()

            if(len(options) == 8):
                line_flags = set(options[7].split(","))
                for flag in line_flags:
                    if( not flag == ""):
                        self.flags[flag](cards = cards,
                                         test = test,
                                         subtest = subtest,
                                         type = type,
                                         labels = labels,
                                         start = start,
                                         end = end )

            graphs.append(graph.Graph(cards, test, subtest, type, labels, start, end))
        self.graphs = graphs
        self.pdfName = pdfName

    def createBook(self):
        with PdfPages(self.pdfName) as pdf:
            for graph in self.graphs:
                graph.plotGraph(multiPdf = pdf)
