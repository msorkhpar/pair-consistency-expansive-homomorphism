import csv

import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score


def build_confusion_matrix(result_csv_file_path, output_path):

    actual = []
    predicted = []
    with open(result_csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            actual.append(int(row[0].split("_")[0]))
            predicted.append(int(row[1].split("_")[0]))

    matrix = confusion_matrix(actual, predicted)
    cm_display = ConfusionMatrixDisplay(confusion_matrix=matrix)
    accuracy = accuracy_score(actual, predicted)
    print("Accuracy:", accuracy)
    cm_display.plot()
    plt.savefig(output_path + "/confusion_matrix.png")
