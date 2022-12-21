import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

def month_to_index(abbreviation):

    months = {
        "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3, "May": 4, "June": 5, "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11
    }
    return months[abbreviation]

def is_returning_visitor(VisitorType):

    if VisitorType == "Returning_Visitor":
        return 1
    else:
        return 0

def str_bool_to_int(string):
    # used for weekend and label columns
    if string == "TRUE":
        return 1
    else:
        return 0

def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        -0 Administrative, an integer
        -1 Administrative_Duration, a floating point number
        -2 Informational, an integer
        -3 Informational_Duration, a floating point number
        -4 ProductRelated, an integer
        -5 ProductRelated_Duration, a floating point number
        -6 BounceRates, a floating point number
        -7 ExitRates, a floating point number
        -8 PageValues, a floating point number
        -9 SpecialDay, a floating point number
        -10 Month, an index from 0 (January) to 11 (December)
        -11 OperatingSystems, an integer
        -12 Browser, an integer
        -13 Region, an integer
        -14 TrafficType, an integer
        -15 VisitorType, an integer 0 (not returning) or 1 (returning)
        -16 Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    with open(filename) as f:
        reader = csv.reader(f)
        # skip header
        next(reader)
        for row in reader:
            ev = []
            lbl = []
            ev.append(int(row[0]))
            ev.append(float(row[1]))
            ev.append(int(row[2]))
            ev.append(float(row[3]))
            ev.append(int(row[4]))
            for i in range(5,10):
                ev.append(float(row[i]))
            ev.append(month_to_index(row[10]))
            for i in range(11, 15):
                ev.append(int(row[i]))
            ev.append(is_returning_visitor(row[15]))
            ev.append(str_bool_to_int(row[16]))
            #lbl.append(str_bool_to_int(row[17]))
            evidence.append(ev)
            #labels.append(lbl)
            labels.append(str_bool_to_int(row[17]))

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    total_positives = 0
    total_negatives = 0
    predicted_positives = 0
    predicted_negatives = 0

    for actual, predicted in zip(labels, predictions):
        if actual == 1:
            total_positives += 1
            if actual == predicted:
                predicted_positives += 1
        if actual == 0:
            total_negatives += 1
            if actual == predicted:
                predicted_negatives += 1

    sensitivity = predicted_positives/total_positives
    specificity = predicted_negatives/total_negatives
    
    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
