# -*- coding: utf-8 -*-
"""kel-3-uas.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JiIlSzhypAeg3SCKeKeEFMOaMQDa6_nD
"""

# Library for Data Manipulation.
import pandas as pd
import numpy as np

# Library for Data Visualization.
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import matplotlib.ticker as ticker
sns.set(style="white",font_scale=1.5)
sns.set(rc={"axes.facecolor":"#FFFAF0","figure.facecolor":"#FFFAF0"})
sns.set_context("poster",font_scale = .7)

# Library to overcome Warnings.
import warnings
warnings.filterwarnings('ignore')

# Library to perform Statistical Analysis.
from scipy import stats
from scipy.stats import chi2
from scipy.stats import chi2_contingency

# Library to Display whole Dataset.
pd.set_option("display.max.columns",None)


# pipeline
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer

# Machine learning algorithms
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier
from sklearn.base import ClassifierMixin
from sklearn.model_selection import StratifiedKFold, cross_val_predict

#for hypertuning
import optuna
from collections import Counter
from sklearn.model_selection import RandomizedSearchCV,GridSearchCV,RepeatedStratifiedKFold

# for model evaluation
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, confusion_matrix, classification_report, roc_auc_score, cohen_kappa_score, balanced_accuracy_score, roc_curve

# Read data train
df_train = pd.read_csv('train_features.csv')
df_train.head()

# Read data train labels
df_labels = pd.read_csv('train_labels.csv')
df_labels.head()

# Read data test
df_test = pd.read_csv('test_features.csv')
df_test.head()

# Gabungkan dataframe menggunakan merge
df_train = pd.concat([df_train, df_labels], axis=1)
df_train

# Drop columns 'id' and 'tanggal_menjadi_anggotathat is not important for modelling
id = df_test['ID']
cols = ['ID', 'tanggal_menjadi_anggota']
df_test.drop(columns=cols, inplace=True)

cols2 = 'tanggal_menjadi_anggota'
df_train.drop(columns=cols2, inplace=True)
df_train_prep = df_train.copy()

df_test_prep = df_test.copy()

# handling missing value of country cols
df_train_prep['pendidikan'] = df_train_prep['pendidikan'].fillna('Sarjana')
df_train_prep['status_pernikahan'] = df_train_prep['status_pernikahan'].fillna('Rencana Menikah')

# handling missing value of country cols
df_test_prep['pendidikan'] = df_test_prep['pendidikan'].fillna('Sarjana')
df_test_prep['status_pernikahan'] = df_test_prep['status_pernikahan'].fillna('Rencana Menikah')

# handling noise of country cols
df_train_prep['pendidikan'] = df_train_prep['pendidikan'].replace({
    '5': 'Sarjana'
})
df_train_prep['status_pernikahan'] = df_train_prep['status_pernikahan'].replace({
    '5': 'Rencana Menikah'
})

# handling noise of country cols
df_test_prep['pendidikan'] = df_test_prep['pendidikan'].replace({
    '5': 'Sarjana'
})
df_test_prep['status_pernikahan'] = df_test_prep['status_pernikahan'].replace({
    '5': 'Rencana Menikah'
})

# handling missing value active_number cols
df_test_prep['keluhan'] = df_test_prep['keluhan'].fillna(0)

# handling missing value active_number cols
df_train_prep['keluhan'] = df_train_prep['keluhan'].fillna(0)

# Numerical columns
for col in df_test_prep.select_dtypes(exclude='object'):
    df_test_prep[col] = df_test_prep[col].fillna(df_test_prep[col].median())
df_test_prep.isnull().sum()

# Numerical columns
for col in df_train_prep.select_dtypes(exclude='object'):
    df_train_prep[col] = df_train_prep[col].fillna(df_train_prep[col].median())
df_train_prep.isnull().sum()

df_train_prep["pendidikan"] = df_train_prep["pendidikan"].replace({"SMP":1 ,"SMA":2, "Sarjana":3,"Magister":4, "Doktor":5})
df_test_prep["pendidikan"] = df_test_prep["pendidikan"].replace({"SMP":1 ,"SMA":2, "Sarjana":3,"Magister":4, "Doktor":5})

df_train_prep["status_pernikahan"] = df_train_prep["status_pernikahan"].replace({"Sendiri":1 ,"Rencana Menikah":2, "Menikah":3,"Cerai":4, "Cerai Mati":5})
df_test_prep["status_pernikahan"] = df_test_prep["status_pernikahan"].replace({"Sendiri":1 ,"Rencana Menikah":2, "Menikah":3,"Cerai":4, "Cerai Mati":5})

x = df_train_prep.drop(['jumlah_promosi'], axis=1) # Independent variabel
y = df_train_prep[['jumlah_promosi']] # Dependen variabel

# Balancing Imbalanced Data
import imblearn
from imblearn.over_sampling import SMOTE
smote = SMOTE()
x_smote, y_smote = smote.fit_resample(x, y)
print("Before Smote" , y.value_counts())
print()
print("After Smote" , y_smote.value_counts())

from sklearn.preprocessing import RobustScaler, MinMaxScaler
scaler = RobustScaler()
minmax = MinMaxScaler()

x_smote_scaled = x_smote
df_test_scaled = df_test_prep

# Scaled with minmax
columns_to_minmax_scale = ['pendidikan','status_pernikahan','terakhir_belanja','jumlah_anak_remaja']
x_smote_scaled[columns_to_minmax_scale] = minmax.fit_transform(x_smote_scaled[columns_to_minmax_scale])

# Scaled with Robust
columns_to_RobustScaler = ['pendapatan','jumlah_anak_balita','belanja_buah','belanja_daging','belanja_ikan','belanja_kue','pembelian_diskon','pembelian_web','pembelian_toko']
x_smote_scaled[columns_to_RobustScaler] = scaler.fit_transform(x_smote_scaled[columns_to_RobustScaler])

training_score = []
testing_score = []
precission = []
recall = []
Roc_Auc_score = []
f1_score_ = []

from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, f1_score, confusion_matrix, classification_report, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def model_prediction(model, x, y, n_splits=5, random_state=42):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    training_score = []
    testing_score = []
    precision = []
    recall = []
    roc_auc = []
    f1_score_ = []

    for train_index, test_index in skf.split(x, y):
        x_train, x_test = x.iloc[train_index], x.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        model.fit(x_train, y_train)
        x_train_pred = model.predict(x_train)
        x_test_pred = model.predict(x_test)

        if len(np.unique(y)) == 2:  # Binary classification
            y_test_prob = model.predict_proba(x_test)[:, 1]
            roc_auc.append(roc_auc_score(y_test, y_test_prob))
        else:  # Multiclass classification
            y_test_prob = model.predict_proba(x_test)
            roc_auc.append(roc_auc_score(y_test, y_test_prob, multi_class='ovr'))

        training_score.append(accuracy_score(y_train, x_train_pred) * 100)
        testing_score.append(accuracy_score(y_test, x_test_pred) * 100)
        precision.append(precision_score(y_test, x_test_pred, average='macro'))
        recall.append(recall_score(y_test, x_test_pred, average='macro'))
        f1_score_.append(f1_score(y_test, x_test_pred, average='macro'))

    print("\n------------------------------------------------------------------------")
    print(f"Mean Accuracy_Score of {model} model on Training Data is:", np.mean(training_score))
    print(f"Mean Accuracy_Score of {model} model on Testing Data is:", np.mean(testing_score))
    print(f"Mean Precision Score of {model} model is:", np.mean(precision))
    print(f"Mean Recall Score of {model} model is:", np.mean(recall))
    print(f"Mean ROC_AUC Score of {model} model is:", np.mean(roc_auc))
    print(f"Mean f1 Score of {model} model is:", np.mean(f1_score_))

    print("\n------------------------------------------------------------------------")
    print(f"Classification Report of {model} model is:")
    y_pred_all = cross_val_predict(model, x, y, cv=skf)
    print(classification_report(y, y_pred_all))

    print("\n------------------------------------------------------------------------")
    print(f"Confusion Matrix of {model} model is:")
    cm = confusion_matrix(y, y_pred_all)
    plt.figure(figsize=(8, 4))
    sns.heatmap(cm, annot=True, fmt="g", cmap="summer")
    plt.show()

# Example usage
# from sklearn.ensemble import ExtraTreesClassifier
# model_prediction(ExtraTreesClassifier(), x_smote, y_smote, n_splits=5, random_state=42)

model_prediction(ExtraTreesClassifier(), x_smote, y_smote, n_splits=5, random_state=42)

from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import GridSearchCV

def model_prediction(model, x_data, y_data, metric='accuracy', n_splits=5):
    # Perform cross-validation
    scores = cross_val_score(model, x_data, y_data, cv=n_splits, scoring=metric)
    return scores

# Define the parameter grid
param_grid = {
    'n_estimators': [10, 50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Instantiate the ExtraTreesClassifier
et_model = ExtraTreesClassifier(random_state=42)

# Perform hyperparameter tuning using GridSearchCV with 'accuracy' as the scoring metric
grid_search = GridSearchCV(estimator=et_model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(x_smote, y_smote)

# Print the best parameters and the best accuracy score
print("Best parameters: ", grid_search.best_params_)
print("Best accuracy score: ", grid_search.best_score_)