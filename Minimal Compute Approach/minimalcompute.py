from prepCAFEData import *
from sklearn.linear_model import RidgeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.svm import LinearSVC
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from modelBenchmark import benchmark


def createConfusionMatrix(clf, y_test, pred):
    fig, ax = plt.subplots(figsize=(10, 5))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax)
    ax.xaxis.set_ticklabels(target_names)
    ax.yaxis.set_ticklabels(target_names)
    _ = ax.set_title(
        f"Confusion Matrix for {clf.__class__.__name__}\non the original documents"
    )


def ridgeClassifierModel(X_train, y_train, X_test, y_test):
    clf = RidgeClassifier(tol=1e-2, solver="sparse_cg")
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)
    createConfusionMatrix(clf, y_test, pred)


# X_train, X_test, y_train, y_test, feature_names, target_names = createData(oversampling=True)
# ridgeClassifierModel(X_train, y_train, X_test, y_test)

# X_train, X_test, y_train, y_test, feature_names, target_names = createData(oversampling=False)
# ridgeClassifierModel(X_train, y_train, X_test, y_test)
# plt.show()

# Pull, format, and vectorize data
# X_train, X_test, y_train, y_test, feature_names, target_names = createData(oversampling=oversampling)



for clf, name in (
    (LogisticRegression(C=5, max_iter=10000), "Logistic Regression"),
    (RidgeClassifier(alpha=1.0, solver="sparse_cg"), "Ridge Classifier"),
    (KNeighborsClassifier(n_neighbors=100), "kNN"),
    (RandomForestClassifier(), "Random Forest"),
    # L2 penalty Linear SVC
    (LinearSVC(C=0.1, dual=False, max_iter=10000), "Linear SVC"),
    # L2 penalty Linear SGD
    (
        SGDClassifier(
            loss="log_loss", alpha=1e-4, n_iter_no_change=3, early_stopping=True
        ),
        "log-loss SGD",
    ),
    # NearestCentroid (aka Rocchio classifier)
    (NearestCentroid(), "NearestCentroid"),
    # Sparse naive Bayes classifier
    (ComplementNB(alpha=0.1), "Complement naive Bayes"),
):
    print("=" * 80)
    print(name)
    results = []
    for _ in range(20):
        X_train, X_test, y_train, y_test, feature_names, target_names = createData(oversampling='SMOTE')
        results.append(benchmark(X_train, y_train, X_test, y_test, clf, name))
    df = pd.DataFrame(results, columns=['name', 'accuracy', 'train_time', 'test_time'])
    print(f"Accuracy:    {df['accuracy'].mean()}")
