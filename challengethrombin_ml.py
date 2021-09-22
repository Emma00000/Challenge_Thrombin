# -*- coding: utf-8 -*-
"""ChallengeThrombin_ML.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18MBEcfVmmRF-bo2FM86JGc8HsDj3XVjT

Machine Learning LCG

Emmanuel Hernández Sánchez
                                                                                          Tamara López González

# CHALLENGE OF THROMBIN

Se identifica y aisla el receptor (trombina) objetivo del fármaco, y se prueban moléculas para determinar su capacidad al unirse (1909). Se separan compuestos activos (42 vinculantes) e inactivos (no vinculantes), y dicha determinación se usa para fármacos. Cada compuesto es un  vector de características con un valor de clase (A o I) y 139,351 características binarias.



            Determinar cuáles de las propiedades son críticas para predecir el valor de la clase.

### Librerías, función y datos
"""

import numpy as np
from collections import Counter
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,classification_report, make_scorer

from sklearn.feature_selection import chi2, SelectKBest, mutual_info_classif
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_selection import RFE

from imblearn.under_sampling import NearMiss, ClusterCentroids, EditedNearestNeighbours
from imblearn.over_sampling import SMOTE, ADASYN

# Función del análisis de rendimiento 
def analysis(Ypred, testY):
    print('\nAccuracy: {}\n'.format(accuracy_score(Ypred, testY)))
    print('Precision: {}\n'.format(precision_score(Ypred, testY, average = 'weighted')))
    print('Recall: {}\n'.format(recall_score(Ypred, testY, average = 'weighted')))
    print('F-score: {}\n'.format(f1_score(Ypred, testY, average = 'weighted')))
    print('\nConfusion matrix: \n')
    print(str(confusion_matrix(Ypred, testY)) + '\n')
    print('Classification report: \n')
    print(classification_report(Ypred, testY, target_names = ['A', 'I']) + '\n')

# Cargar el data set de entrenamiento
with open('./Thrombin/thrombin.data', 'r') as file:
  train_set = file.readlines()
print('Se recuperaron: ', str(len(train_set)), ' líneas en el vector de entrenamiento.')


#Cargamos el data set de prueba
with open('./Thrombin-2/Thrombin.testset', 'r') as file:
  test_set = file.readlines()
print('Se recuperaron: ', str(len(test_set)), ' líneas en el vector de prueba.')

with open('./Thrombin/ThrombinKey', 'r') as file:
  test_class = file.readlines()
print('Se recuperaron: ', str(len(test_class)), ' clases en el vector de prueba.')

# Guardar datos 

train_data = []
train_class = []

for lines in train_set:
  lines = lines.replace("\n","")
  l = lines.split(",")
  train_class.append(l[0])
  l = l[1:]
  l = [int(i) for i in l]
  train_data.append(l)
    
train_data = np.array(train_data)
print("Datos de entretamiento: ")
print(len(train_data),"  ",len(train_class))

test_data=[]

for lines in test_set:
  lines = lines.replace("\n","")
  l = lines.split(",")[1:]
  l = [int(i) for i in l]
  test_data.append(l)
test_class = [i.replace("\n","") for i in test_class]

test_data = np.array(test_data)
print('Datos de test: ')
print(len(test_data),"  ",len(test_class))

# Verificar proporciones
print('Proporciones en los datos:')
print(sorted(Counter(train_class).items()))
print(sorted(Counter(test_class).items()))

"""### Clasificación inicial sin modificaciones"""

# Clasificación inicial lineal

svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(train_data, train_class)

Ypred = svm_classifier.predict(test_data)

analysis(Ypred, test_class)

# Clasificación inicial rbf

svm_classifier = SVC(kernel = "rbf")
svm_classifier.fit(train_data, train_class)

Ypred = svm_classifier.predict(test_data)

analysis(Ypred, test_class)

"""Aunque un kernel "rbf" parecía ser más prometedor por usar un híper plano no lineal que se pudiera acoplar mejor a los datos desbalanceados (y posiblemente incrustados entre clases), los resultados muestran una mejor clasificación con un kernel "linear". Adicionalmente, se probaron técnicas de reducción de dimensionalidad con kernel "rbf" y no daban ningún cambio.

## Reducción de dimensionalidad

De las herramientas para reducción de dimensionalidad vistas, nos pareció que las siguientes eran las más adecuadas para el problema: 
* *Recursive Feature Elimination (RFE)*: podría ser la mejor opción al ir eliminando recursivamente lo que se considere menos importante bajo un parámetro, pero es computacionalmente muy costoso. 
* *Mutual information (MI)*: mide la dependencia entre las variables y eliminaría características dependientes redundantes.
* *Chi cuadrada*: características no negativas booleanos y mide la dependencia a la clase.
* *SVD truncada (LSA)*: reducción lineal mediante la descomposición de valores singulares truncados (SVD)

* **Mutual information (MI)**:
"""

# Reducción de dimensión con MI
reducMi = SelectKBest(mutual_info_classif, k = 700)
Xtrain_Mi = reducMi.fit_transform(train_data, train_class)
Xtest_Mi = reducMi.transform(test_data)

# Entrenar el modelo
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(Xtrain_Mi, train_class)

Ypred = svm_classifier.predict(Xtest_Mi)

analysis(Ypred, test_class)

"""* **Chi cuadrada**:"""

# Reducción de dimensión con Chi2
reducChi = SelectKBest(chi2, k = 700)
print(train_data.shape)
Xtrain_Chi2 = reducChi.fit_transform(train_data, train_class)
Xtest_Chi2 = reducChi.transform(test_data)
print(Xtrain_Chi2.shape)

# Entrenar el modelo
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(Xtrain_Chi2, train_class)

Ypred = svm_classifier.predict(Xtest_Chi2)

analysis(Ypred, test_class)

"""* **SVD truncada (LSA)**:"""

# Reducción de dimensión con LSA a 700 dimensiones 
reducSVD = TruncatedSVD(n_components = 700, random_state = 42) 
Xtrain_SVD = reducSVD.fit_transform(train_data)
Xtest_SVD = reducSVD.transform(test_data)

# Entrenar el modelo
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(Xtrain_SVD, train_class)

Ypred = svm_classifier.predict(Xtest_SVD)

analysis(Ypred, test_class)

"""- **RFE**"""

# Reducción de dimensión 
estimator = SVC(kernel = "linear")
rfe = RFE(estimator = estimator, n_features_to_select = 700, step = 500, verbose = 0)

# Entrenar el modelo
rfe.fit(train_data, train_class)
# Predecir clases de datos prueba
Ypred = rfe.predict(test_data)

"""La reducción de dimensionalidad fue menos efectiva de lo esperado y con resultados muy similares entre diferentes métodos (e incluso similares con una clasificación sin alteración). Aún así, la reducción hecha con *Mutual Information* dio mejores resultados para la clase minoritaria que se trata resaltar.

## Técnicas para desbalanceo

#### UNDERSAMPLING

**Generación de prototipos**


Reduce el número de ejemplos en la clase usando ejemplos distintos a los ejemplos originales

- *Cluster centroids*: Usa los centroides del agrupamiento k-means en lugar de los ejemplos originales
"""

# Cluster centroids 
x_resampled_Cluster, y_resampled_Cluster = ClusterCentroids().fit_resample(Xtrain_Mi, train_class)
print(sorted(Counter(y_resampled_Cluster).items()))

print(len(x_resampled_Cluster),"  ",len(y_resampled_Cluster))

# Entrenar el modelo y predecir
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(x_resampled_Cluster, y_resampled_Cluster)

Ypred = svm_classifier.predict(Xtest_Mi)

print('\nAccuracy: {}\n'.format(accuracy_score(Ypred, test_class)))
print('Precision: {}\n'.format(precision_score(Ypred, test_class, average = 'weighted')))
print('Recall: {}\n'.format(recall_score(Ypred, test_class, average = 'weighted')))
print('F-score: {}\n'.format(f1_score(Ypred, test_class, average = 'weighted')))

print('\nConfusion matrix: \n')
print(str(confusion_matrix(Ypred, test_class)) + '\n')
print('Classification report: \n')
print(classification_report(Ypred, test_class, target_names = ['A', 'I']) + '\n')

analysis(Ypred, test_class)

"""**Selección de prototipos controlado**


Reduce el número de ejemplos en la clase usando los ejemplos originales, y es controlado porque se especifica el número de ejemplos

- *NearMiss*: Usa algoritmo de vecinos cercanos (nearest neighbors)

        - NearMiss-1: ejemplos de clase mayoritaria con la menor distancia media a los más cercanos de la clase minoritaria

        - NearMiss-2: ejemplos de clase mayoritaria con la menor distancia media a los más lejanos de la clase minoritaria
"""

# NearMiss-1
x_resampled_Nearmiss1, y_resampled_Nearmiss1 = NearMiss(version = 1).fit_resample(Xtrain_Mi, train_class)
print(sorted(Counter(y_resampled_Nearmiss1).items()))

# Entrenar el modelo y predecir
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(x_resampled_Nearmiss1, y_resampled_Nearmiss1)

Ypred = svm_classifier.predict(Xtest_Mi)

analysis(Ypred, test_class)

# NearMiss-2
x_resampled_Nearmiss2, y_resampled_Nearmiss2 = NearMiss(version = 2).fit_resample(Xtrain_Mi, train_class)
print(sorted(Counter(y_resampled_Nearmiss2).items()))

# Entrenar el modelo y predecir
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(x_resampled_Nearmiss2, y_resampled_Nearmiss2)

Ypred = svm_classifier.predict(Xtest_Mi)

analysis(Ypred, test_class)

"""**Selección de prototipos por limpieza**


Reduce el número de ejemplos en la clase usando los ejemplos originales, y es por limpieza porque se especifica el número de ejemplos, sólo se eliminan los casos irregulares de clases.

- *Edited Nearest Neighbours*: Aplica el algoritmo de vecinos cercanos a  cada instancia de la clase mayoritaria y elimina aquellos cuyos vecinos no pertenezcan a la misma (todos o la mayoría)
"""

# Editec Nearest Neighbours
x_resampled_ENN, y_resampled_ENN = EditedNearestNeighbours().fit_resample(Xtrain_Mi, train_class)
print(sorted(Counter(y_resampled_ENN).items()))

# Entrenar el modelo y predecir
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(x_resampled_ENN, y_resampled_ENN)

Ypred = svm_classifier.predict(Xtest_Mi)

analysis(Ypred, test_class)

"""#### OVERSAMPLING

**Aleatorio**


Generación de nuevos ejemplos de manera aleatoria con reemplazo (se mantienen los ejemplos originales)

- *Synthetic Minority Oversampling Technique (SMOTE)*: SMOTE regular: selecciona aleatoriamente el ejemplo inicial
"""

# SMOTE 
x_resampled_SMOTE, y_resampled_SMOTE = SMOTE().fit_resample(Xtrain_Mi, train_class)
print(sorted(Counter(y_resampled_SMOTE).items()))

# Entrenar el modelo y predecir
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(x_resampled_SMOTE, y_resampled_SMOTE)

Ypred = svm_classifier.predict(Xtest_Mi)

analysis(Ypred, test_class)

"""- *Adaptive Synthetic Sampling Approach (ADASYN)*: Genera ejemplos cerca de los originales mal clasificados por un clasificador k-Nearest Neighbors (kNN)

"""

# ADASYN 
x_resampled_ADASYN, y_resampled_ADASYN = ADASYN().fit_resample(Xtrain_Mi, train_class)
print(sorted(Counter(y_resampled_ADASYN).items()))


# Entrenar el modelo y predecir
svm_classifier = SVC(kernel = "linear")
svm_classifier.fit(x_resampled_ADASYN, y_resampled_ADASYN)

Ypred = svm_classifier.predict(Xtest_Mi)

analysis(Ypred, test_class)





