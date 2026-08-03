import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import(
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
)
from imblearn.over_sampling import SMOTE
import joblib

print("--- Task 1: Dtaset Profling & Saving---")
if not os.path.exists("titanic.csv"):
    df_raw = sns.load_dataset('titanic')
    df_raw.to_csv("titanic.csv", index=False)
    print("--> titanic.csv created successfully!")
else:
    df_raw = pd.read_csv("titanic.csv")
    print("--> titanic.csv loaded from local storage!")

df = df_raw.copy()
df['deck'] = df['deck'].astype(str).fillna('missing')
df['age'] = df['age'].fillna(df['age'].median())
df = df.dropna(subset=['embarked', 'embark_town'])

x = df.drop(columns=['survived'])
y = df['survived']
x_train, x_test, y_train, y_test = train_test_split(
    x,y, test_size=0.2, random_state=42, stratify=y
)

num_features = ['age', 'fare', 'sibsp', 'parch']
cat_features = ['sex', 'embarked', 'pclass']

num_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

cat_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer([
    ('num', num_transformer, num_features),
    ('cat', cat_transformer, cat_features)
])

full_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True))
])

full_pipeline.fit(x_train, y_train)
joblib.dump(full_pipeline, 'full_pipeline.joblib')
print("Module 2 Analytics Pipeline Script Executed Successfully!")