import requests
import json

apiLocation = "http://netqe-infra01.knqe.lab.eng.bos.redhat.com:8009"

class QEdataRequest():

    def validCards(self):
        return requests.get(apiLocation + "/valid/cards").json()

    def validTests(self):
        return requests.get(apiLocation + "/valid/tests").json()

    def validSubtests(self, test):
        payload = {"test": test}
        return requests.get(apiLocation + "/valid/subtests", params = payload).json()

    def validTypes(self, test, subtest):
        payload = {"test": test, "subtest": subtest}
        return requests.get(apiLocation + "/valid/types", params = payload).json()

    def validLabels(self, test, subtest, type):
        payload = {"test": test, "subtest": subtest, "type":type}
        return requests.get(apiLocation + "/valid/labels", params = payload).json()

    def getData(self, **kwargs):
        payload = kwargs
        data = requests.get(apiLocation + "/data", params = payload).json()
        return data

    def getStructure(self):
        return requests.get(apiLocation + "/charts").json()

    def update(self, startMonth, endMonth):
        return requests.post(apiLocation + "/update", data = {"start": startMonth, "end": endMonth})
