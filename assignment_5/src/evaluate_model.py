import os
import ast
import argparse
import pickle
import random
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from scipy.stats.distributions import randint

def encode_types(dataset):
    """
    Encodes the pokemon types.
    Each type is one-hot encoded.
    Both the columns "player_types" and "opponent_types" are substituded by one column for each type in the dataset with value 1 if the considered pokemon has that type and 0 otherwise.

    Parameters:
    - dataset: pandas dataframe with pokemon data.

    Returns:
    - pandas dataframe with the pokemon types encoded.
    """

    # transform the lists stored as strings into actual lists
    dataset["player_types"] = dataset["player_types"].apply(ast.literal_eval)
    dataset["opponent_types"] = dataset["opponent_types"].apply(ast.literal_eval)

    # encode players' types
    player_df = dataset.explode("player_types")
    player_df = pd.get_dummies(player_df["player_types"], prefix="player").groupby(player_df.index).sum()
    
    # encode opponents' types
    opponent_df = dataset.explode("opponent_types")
    opponent_df = pd.get_dummies(opponent_df["opponent_types"], prefix="opponent").groupby(opponent_df.index).sum()

    # remove the columns "player_types" and "opponent_types" and add the columns with players' types and opponents' types
    return pd.concat([dataset, player_df, opponent_df], axis=1).drop(["player_types", "opponent_types"], axis=1)

def hyper_params_search(X_train, y_train, save_path):
    """
    Performs a randomized search for the best hyper parameters, validating the search using k-fold cross validation.
    It also saves the model trained with the best found parameters on the whole training set.

    Parameters:
    - X_train: array with training features.
    - y_train: array with tarining labels.
    - save_path: path to the file where to save the model trained with best found parameters on the whole training set.

    Returns:
    - scikit-learn RandomForestClassifier trained on the whole training set with the best hyper parameters.
    """

    # perform a grid search to find the best set of hyper-parameters using cross validation
    hyper_params_grid = {"n_estimators": randint(50, 1000), "max_depth": randint(1, 50)}
    clf = RandomForestClassifier()
    random_search = RandomizedSearchCV(clf, param_distributions={"n_estimators": [1], "max_depth": [2]}, n_iter=1, cv=2, verbose=4, n_jobs=8)
    random_search.fit(X_train, y_train)
    print(f"\nBest hyperparameters: {random_search.best_params_}")

    # save the model
    with open(save_path, "wb") as file:
        pickle.dump(random_search.best_estimator_, file)
    
    # return the best estimator re-trained on the whole training set
    return random_search.best_estimator_

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
    sns.barplot(data=pd.DataFrame({"Feature Name": feature_names, "Importance": feature_importances}), x="Importance", y="Feature Name")
    plt.title("Feature Importances")
    plt.xlabel("Mean Decrease in Impurity (MDI)")
    plt.savefig(save_path, dpi=350)
    plt.close()

def parse_args():
    """
    Parses command line arguments.

    Returns:
    - parser.parse_args(): ArgumentParser object with parsed arguments.
    """

    # create the argument parser
    parser = argparse.ArgumentParser(description="Validates a trained model on the test set.")

    # arguments
    parser.add_argument("-i", "--input_data", type=str, required=False, default="./results/collected_data.csv", help="Path to the input dataset with data collected from a simulation.")
    parser.add_argument("-m", "--model_dir", type=str, required=False, default="./model", help="Path to the directory where to save the trained model.")
    parser.add_argument("-p", "--plots_dir", type=str, required=False, default="./results", help="Path to the directory where to save the generated plots.")
    parser.add_argument("-r", "--random_seed", type=int, required=False, default=27, help="Random seed for reproducibility.")
                          
    return parser.parse_args()

if __name__ == '__main__':

    # pars command line arguments
    args = parse_args()

    # set the random seed for reproducibility
    random.seed(args.random_seed)
    np.random.seed(args.random_seed)

    # load the data generated by the simulation
    print("Loading data ...")
    dataset = pd.read_csv(args.input_data)

    # create the folders where to save the results if it does not exist yet
    os.makedirs(args.plots_dir, exist_ok=True)
    os.makedirs(args.model_dir, exist_ok=True)

    # encode the pokemon types
    print("Preparing data ...")
    dataset = encode_types(dataset)

    # divide the features from the battle outcomes
    X = dataset[[col for col in dataset.columns if col != "outcome"]]
    y = dataset["outcome"]

    # split data into a training and a test set
    test_ratio = 0.2
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_ratio, random_state=args.random_seed)

    # select the hyper parameters by performing a randomized search with k-fold cross validation and re-train the model on the whole training set
    print("Performing a randomized hyper parameters search and training a model with the best found hyper parameters ...")
    clf = hyper_params_search(X_train, y_train, os.path.join(args.model_dir, "model.pickle"))

    # predict the outcome for test data and evaluate the model
    print("Predicting test outcomes ...")
    y_test_pred = clf.predict(X_test)
    print("Evaluating the model on the test set...")
    evaluate_model(y_test_pred, y_test, os.path.join(args.plots_dir))

    # create a plot with feature importance
    plot_feature_importance(X.columns, clf.feature_importances_, os.path.join(args.plots_dir, "feature_importances_plot.jpg"))
    