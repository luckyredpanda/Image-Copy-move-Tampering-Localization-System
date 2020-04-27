import matplotlib
import os


if not "DISPLAY" in os.environ:
    matplotlib.use("Agg")


import qeGraphMaker.helper as helper
import matplotlib.pyplot as plt
import numpy as np
from qeGraphMaker.apiRequest import QEdataRequest

class Graph():
    """docstring for [object Object]."""
    def __init__(self, cards, test, subtest, type, labels, start, end):
        super().__init__()
        self.cards = cards
        self.test = test
        self.subtest = subtest
        self.type = type
        self.labels = labels
        self.start = start
        self.end = end
        self.appReq = QEdataRequest()

    def plotGraph(self, fileName="test.pdf", multiPdf=None):
        fig = plt.figure(figsize=(18, 9))
        ax = fig.add_subplot(111, position=[0.1, 0.1, 0.8, 0.8])
        startEpoch = helper.stringDateToEpoch(self.start)
        endEpoch = helper.stringDateToEpoch(self.end) + (24*60*60)
        ax.set_facecolor("#330000")
        for card in self.cards:
            for label in self.labels:
                helper.plotData(card, label, self.appReq.getData(card = card,
                            test = self.test, subtest = self.subtest, type = self.type,
                            epochStart = startEpoch, epochEnd = endEpoch), ax)
        (ymin, ymax) = plt.ylim()
        bottom = -ymax * (0.05)
        top = ymax + (ymax - ymin) * 0.1
        ax.grid(color="#6A0000", lw = 2.5)
        ax.set_title(self.test + ": " + self.subtest + " " + self.type)
        ax.ticklabel_format(axis = "y", useOffset = False)
        ax.legend(bbox_to_anchor = (1.11, 1), loc = "best", borderaxespad = 0.)
        ax.set_ylim(bottom = bottom, top = top)
        if(multiPdf != None):
            multiPdf.savefig()
        else:
            plt.savefig(fileName)

        plt.close("all")
