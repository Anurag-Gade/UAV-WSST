# -*- coding: utf-8 -*-
"""UAV_Model_Final

Automatically generated by Colaboratory.

"""

from tensorflow.python.client import  device_lib
device_lib.list_local_devices()

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense

from sklearn.model_selection import train_test_split, KFold
import pandas as pd
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import seaborn as sns

from tensorflow.keras.layers import BatchNormalization
from sklearn import metrics 
from sklearn.metrics import classification_report
import time
from tqdm.notebook import tqdm


from google.colab import drive
drive.mount('/content/drive')

import h5py
 
DATA_DIR = "/content/drive/MyDrive/data_224.mat"
 
data = h5py.File(DATA_DIR,'r')
 
data.keys()

import numpy as np
 
X = np.transpose(np.array(data['Img_Data_Res']))
Y = np.reshape(np.array(data['Labels']),[-1,])
 
print(X.shape)
print(Y.shape)

X, X_test, Y, Y_test = train_test_split(X, Y, test_size=0.1)
#X = (X)/255
#X_test = (X_test)/255

import matplotlib.pyplot as plt
 
plt.imshow(X[0,:,:,:])

X.shape


#Model Parameters
num_classes = 15 
filter_conv = (6,6)
pool = (4,4)
dropout_rate = 0.35
input_shape = (224,224,3)
train_accuracy_per_fold = []
test_accuracy_per_fold = []

kfold = KFold(n_splits = 10, shuffle=True)
fold = 1

for train, test in kfold.split(X,Y):
  
  model = Sequential()

  model.add(BatchNormalization(input_shape = input_shape))
  model.add(Conv2D(8, filter_conv, padding = 'same', activation = 'relu'))
  model.add(MaxPooling2D(pool_size = pool, strides = None))

  model.add(Conv2D(16, filter_conv, padding = 'same', activation = 'relu'))
  model.add(MaxPooling2D(pool_size = pool, strides = None))

  model.add(Conv2D(32, filter_conv, padding = 'same', activation = 'relu'))
  model.add(MaxPooling2D(pool_size = pool, strides = None))
  model.add(Dropout(dropout_rate))
  model.add(Flatten())

  model.add(Dense(num_classes, activation = 'softmax'))

  model.build(input_shape)

  
  model.summary()

  optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001)
  model.compile(
        optimizer = optimizer, loss = "sparse_categorical_crossentropy", metrics = ["accuracy"]
  )

  # early_stopping_split = tf.keras.callbacks.EarlyStopping(
  #   monitor = "val_loss",
  #   patience = 20
  # )

  history = model.fit(X[train], Y[train], epochs = 50, batch_size=8, shuffle = True, validation_split = 0.1)
  test_loss, test_acc = model.evaluate(X_test, Y_test, verbose = 2)
  print("Test accuracy in fold {} : {}%".format(fold, test_acc*100))
  fold = fold+1
  test_accuracy_per_fold.append(test_acc*100)

print(f'> Overall Test Accuracy: {np.mean(test_accuracy_per_fold)} (+- {np.std(test_accuracy_per_fold)})')

model.save('/content/drive/MyDrive/Documents/UAV_Final.h5')

"""Holdout"""

num_classes = 15
filter_conv = (6,6)
pool = (4,4)
dropout_rate = 0.35
input_shape = (224,224,3)


model = Sequential()

model.add(BatchNormalization(input_shape = input_shape))
model.add(Conv2D(8, filter_conv, padding = 'same', activation = 'relu'))
model.add(MaxPooling2D(pool_size = pool, strides = None))

model.add(Conv2D(16, filter_conv, padding = 'same', activation = 'relu'))
model.add(MaxPooling2D(pool_size = pool, strides = None))

model.add(Conv2D(32, filter_conv, padding = 'same', activation = 'relu'))
model.add(MaxPooling2D(pool_size = pool, strides = None))
model.add(Dropout(dropout_rate))
model.add(Flatten())

model.add(Dense(num_classes, activation = 'softmax'))

model.build(input_shape)

model.summary()

optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001)
model.compile(
      optimizer = optimizer, loss = "sparse_categorical_crossentropy", metrics = ["accuracy"]
)

# early_stopping_split = tf.keras.callbacks.EarlyStopping(
#   monitor = "val_loss",
#   patience = 20
# )

history = model.fit(X, Y, epochs = 50, batch_size=8, shuffle = True, validation_split = 0.1)
test_loss, test_acc = model.evaluate(X_test, Y_test, verbose = 2)


#Accuracy Plot
plt.figure('Accuracy Plot')
plt.plot(history.history['accuracy'], label='train_accuracy')
plt.plot(history.history['val_accuracy'], label = 'validation_accuracy')
plt.legend(loc='lower right')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0, 1])
plt.title('Accuracy Plot')
plt.savefig('/content/drive/MyDrive/UAV_Project/Plots/Accuracy_Plot_Model.eps', format='eps')
plt.savefig('/content/drive/MyDrive/UAV_Project/Plots/Accuracy_Plot_Model.pdf', format='pdf')


#Loss Plot
plt.figure('Loss Plot')
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label = 'validation_loss')
plt.legend(loc='upper right')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.ylim([0, 1])
plt.title('Loss Plot')
plt.savefig('/content/drive/MyDrive/UAV_Project/Plots/Loss_Plot_Model.eps', format='eps')
plt.savefig('/content/drive/MyDrive/UAV_Project/Plots/Loss_Plot_Model.pdf', format='pdf')

test_loss, test_acc = model.evaluate(X_test,  Y_test, verbose=2)
Y_te = np.array(tf.math.argmax(model.predict(X_test), 1))
cm = tf.math.confusion_matrix(Y_test, Y_te)


acc = metrics.accuracy_score(Y_test, Y_te)
print("test accuracy =", acc*100,"%\n")

print(classification_report(Y_test, Y_te))

con_mat = tf.math.confusion_matrix(labels=Y_test, predictions=Y_te).numpy()

con_mat_norm = np.around(con_mat.astype('float') / con_mat.sum(axis=1)[:, np.newaxis], decimals=2)
classes = ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14"]
con_mat_df = pd.DataFrame(con_mat_norm,
                     index = classes, 
                     columns = classes)
plt.figure('Confusion Matrix',figsize=(6,8))
sns.heatmap(con_mat_df, annot=True, cmap="Blues")
plt.tight_layout()
plt.title('Confusion Matrix')
plt.ylabel('True Label', fontsize=10)
plt.xlabel('Predicted Label', fontsize=10)
plt.savefig('/content/drive/MyDrive/UAV_Project/Plots/Confusion_Matrix_Model_1.eps', format='eps')
plt.savefig('/content/drive/MyDrive/UAV_Project/Plots/Confusion_Matrix_Model_1.pdf', format='pdf')
plt.savefig('/content/drive/MyDrive/UAV_Project/Plots/Confusion_Matrix_Model_1.png', format='png')

model.save('/content/drive/MyDrive/UAV_Project/UAV_Model_Final.h5')

# pip install poof

# import poof

