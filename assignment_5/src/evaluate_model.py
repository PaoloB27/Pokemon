import os
import argparse
import pickle
import random
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.tree import plot_tree
from scipy.stats.distributions import randint
from train_model import encode_types

def evaluate_model(y_pred, y_true, save_dir):
    """
    Evaluates the input predictions by comparing them to the ground truth.

    Parameters:
    - y_pred: array with the predicted outcomes.
    - y_true: array with the true outcomes.
    - save_dir: path to the directory where to save evaluation plots.
    """

    # print the classification report
    print(f"\nClassification Report on the test set:\n {classification_report(y_true, y_pred)}")

    # create and save the confusion matrix
    sns.set_style("whitegrid")
    sns.heatmap(data=confusion_matrix(y_true, y_pred), cmap="Reds", annot=True)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix Test Set")
    plt.savefig(os.path.join(save_dir, "confusion_matrix_test_set.jpg"), dpi=350)
    plt.close()

    # compute the roc and auc scores
    fpr, tpr, thresholds = roc_curve(y_true, y_pred)
    auc_score = auc(fpr, tpr)
    print(f"The AUC score is {auc_score: .2f}")
    roc_df = pd.DataFrame({"False Positive Rate": fpr, "True Positive Rate": tpr})

    # plot the roc
    sns.set_style("whitegrid")
    plt.plot([0, 1], [0, 1], linestyle="--", color="blue", label="Random Classifier", zorder=1)
    sns.lineplot(data=roc_df, x="False Positive Rate", y="True Positive Rate", label=f"ROC Curve, AUC={auc_score: .2f}", color="red", zorder=2)
    plt.legend()
    plt.title("ROC Classifier")
    plt.savefig(os.path.join(save_dir, "roc_test_set.jpg"), dpi=350)
    plt.close()

def plot_feature_importance(feature_names, feature_importances, save_path):
    """
    Creates and saves a plot with the importance of each feature, according to the trained classifier.

    Parameters:
    - feature_names: array of strings with the names of the features.
    - feature_importances: array with the importances of the features.
    - save_path: path to the file where to save the plot.
    """

    # plot the feature importances
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 8))
    sns.barplot(data=pd.DataFrame({"Feature Name": feature_names, "Importance": feature_importances}).sort_values(by="Importance", ascending=False), x="Importance", y="Feature Name")
    plt.title("Feature Importances")
    plt.xlabel("Mean Decrease in Impurity (MDI)")
    plt.savefig(save_path, dpi=350)
    plt.close()

def plot_decision_trees(estimators, feature_names, save_dir, n_trees=3):
    """
    Plots n_trees decision trees sampled uniformly at random from the input ones.

    Parameters:
    - estimators: list of DecisionTreeClassifier objects representing a random forest.
    - feature_names: array with the names of the features.
    - save_dir: path to the directory where to save the plots.
    - n_trees: integer representing the number of decision trees to be sampled and plotted.
    """

    # sample n_trees decision trees
    sampled_trees = random.sample(estimators, k=n_trees)

    # plot each sampled tree
    for i, tree in enumerate(sampled_trees):
        plot_tree(tree, feature_names=feature_names, filled=True, max_depth=2, proportion=True)
        plt.savefig(os.path.join(save_dir, f"sampled_decision_tree_{i}.jpg"), dpi=350)
        plt.close()

def parse_args():
    """
    Parses command line arguments.

    Returns:
    - parser.parse_args(): ArgumentParser object with parsed arguments.
    """

    # create the argument parser
    parser = argparse.ArgumentParser(description="Validates a trained model on a test set.")

    # arguments
    parser.add_argument("-i", "--input_data", type=str, required=False, default=os.path.join("..", "data", "collected_data.csv"), help="Path to the input dataset with data collected from a simulation.")
    parser.add_argument("-m", "--model_path", type=str, required=False, default=os.path.join("..", "model", "model.pickle"), help="Path to the file where the trained model is saved.")
    parser.add_argument("-t", "--test_indices_path", type=str, required=False, default=os.path.join("..", "data", "test_indices.npy"), help="Path to the file with the indices of the test samples in the original dataset.")
    parser.add_argument("-p", "--plots_dir", type=str, required=False, default=os.path.join("..", "results"), help="Path to the directory where to save the generated plots.")
    parser.add_argument("-r", "--random_seed", type=int, required=False, default=27, help="Random seed for reproducibility.")
                          
    return parser.parse_args()

if __name__ == '__main__':

    # pars command line arguments
    args = parse_args()

    # set the random seed for reproducibility
    random.seed(args.random_seed)
    np.random.seed(args.random_seed)

    # load the data generated by the simulation and extract only test samples
    print("Loading data ...")
    dataset = pd.read_csv(args.input_data)
    test_indices = np.load(args.test_indices_path, allow_pickle=True)
    test_set = dataset.loc[test_indices]

    # create the folder where to save the plots if it does not exist yet
    os.makedirs(args.plots_dir, exist_ok=True)

    # encode the pokemon types
    print("Preparing data ...")
    test_set = encode_types(test_set)

    # extract features and battle outcomes
    X_test = test_set.drop(columns=["outcome", "game", "battle"])
    y_test = test_set["outcome"]

    # load the trained model
    with open(args.model_path, "rb") as file:
        clf = pickle.load(file)

    # predict the outcome for test data
    print("Predicting test outcomes ...")
    y_test_pred = clf.predict(X_test)

    # evaluate the model
    print("Evaluating the model on the test set...")
    evaluate_model(y_test_pred, y_test, os.path.join(args.plots_dir))

    # create a plot with feature importance
    plot_feature_importance(X_test.columns, clf.feature_importances_, os.path.join(args.plots_dir, "feature_importances_plot.jpg"))

    # sample and save the plot of some decision trees
    plot_decision_trees(clf.estimators_, X_test.columns, args.plots_dir)