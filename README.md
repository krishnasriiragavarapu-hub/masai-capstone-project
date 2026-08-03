# Module 2- Analytics & Modeling Pipeline 

This repository contains the complete analytics pipeline for the Titanic dataset, including data profiling, cleaning, classification modeling, imbalance comparison, regression sub-tasks, and model persistence.

---
## 1. Data Profiling & Cleaning Summary

* **Dataset Strategy**: Loaded using 'seaborn.load_dataset('titanic')' and  saved locally as 'titanic.csv' for offline execution.
* **Missing Value Strategy**:
  *'embarked' / 'embark_town (<5% missing): Dropped missing rows.
  *'age' (5-30% missing): Imputed using column median.
  *'deck' (>30% missing): Categorized explicitly as ''missing''.
* **Exploratory Analysis Insights**:
  * IQR bounds ($Q1 - 1.5/times IQR, Q3 + 1.5/times IQR$) identified notable right-skwed outliers in 'fare'.
  * Strongest feature correlation observed between passenger class ('pclass') and ticket fare ('fare').

  ---

  ## 2. Model Performance Comparison 

  ### Classification Sub-Task
  All models were trained on an identical 80/20 stratifiedx train-test split.
  | MOdel | Accuracy |precision | Recall | F1-Score | ROC_AUC |
  |:--- | :---: | :---: | :---: | :---: | :---: |
  | **Logistic Regression** | 0.7989 | 0.7647 | 0.7222 | 0.7429 | 0.8521 |
  | **Decision Tre** | 0.7709 | 0.7206  | 0.6806 | 0.7000 | 0.7554 | 
  | **Random Forest (tuned)** | **0.8268** | **0.8030** | **0.7361** | **0.7681** | **0.8745** |

  * **Hyperparameter Tuning & OOB Score**: Random Forest tuned with 'oob_score=True' achieved an Out-of-Bag validation score of **0.8140**.
  * **Imbalance Analysis**: Compared baseline vs. 'class_weight='balanced' 'vs.SMOTE (applied to train split only). 'class_weight='balanced''achieved the best recall stability without synthetic noise.

  ### Regression sub-task ('fare' prediction)
  * **MAE**: '18.42'
  * **RMSE**: '32.15'
  * **$R^@$**: '0.385'
  * **Heteroscedasticity Analysis**: Residual plots show non-constant, expanding varience as fitted values increase, coonfirming the presence of heteroscedasticity.

  ---
  ## 3. Final Recommendation & saved Artifact 
  * **REcommended Model**: **Random Forest Classifier**
  * **Reasoning**: Outperforms all baseline  models across F1-Score (0.7681) and ROC-AUC (0.8745)   while reducing varience.
  * **Saved Artifact**: Saved as 'full_pipeline.joblib' via 'joblib.dump()'. Contains end-to-end  preprocessing transformers paired directly with the fitted estimator.
