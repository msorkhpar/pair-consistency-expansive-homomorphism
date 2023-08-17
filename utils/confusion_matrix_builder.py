import csv
import os.path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def build_confusion_matrix(result_csv_file_path, output_path):
    confusion_matrix = np.zeros((10, 10), dtype=int)

    with open(result_csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)

        for row in reader:
            actual = int(row[0].split("_")[0])
            detected = int(row[1].split("_")[0])
            confusion_matrix[actual][detected] += 1

    row_sums = confusion_matrix.sum(axis=1, keepdims=True)
    normalized_confusion_matrix = confusion_matrix / row_sums * 100

    plt.figure(figsize=(10, 8))
    sns.heatmap(normalized_confusion_matrix, annot=True, cmap='YlGnBu', fmt='.2f', cbar_kws={'label': 'Percentage (%)'})
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(output_path, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')