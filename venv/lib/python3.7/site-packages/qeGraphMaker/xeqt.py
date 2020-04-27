import qeGraphMaker.graphFileParser as graphFileParser
import argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", required = True,
                        help = "Update file name, for help with format look at multiGraphFileExample")

    args = parser.parse_args()

    a = graphFileParser.MultiGraph(args.file)

    a.construct()

    a.createBook()

if __name__ == "__main__":
    main()
