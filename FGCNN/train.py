'''
# Time   : 2021/1/7 14:33
# Author : junchaoli
# File   : train.py
'''

from model import FGCNN
from utils import create_criteo_dataset

import tensorflow as tf
from tensorflow.keras import optimizers, losses
from sklearn.metrics import accuracy_score

if __name__ == '__main__':
    file_path = 'E:\\PycharmProjects\\推荐算法\\data\\train.txt'
    feature_columns, (X_train, y_train), (X_test, y_test) = create_criteo_dataset(file_path, test_size=0.2)
    hidden_units = [128]
    dropout = 0.2
    filters = [14, 16]
    kernel_width = [7, 7]
    dnn_maps = [3, 3]

    model = FGCNN(feature_columns, hidden_units, dropout=dropout, filters=filters, kernel_width=kernel_width, dnn_maps=dnn_maps)
    optimizer = optimizers.SGD(0.01)

    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    train_dataset = train_dataset.batch(32).prefetch(tf.data.experimental.AUTOTUNE)

    summary_writer = tf.summary.create_file_writer('E:\\PycharmProjects\\tensorboard')
    for epoch in range(30):
        sum_loss = []
        for batch, data_batch in enumerate(train_dataset):
            X_train, y_train = data_batch[0], data_batch[1]
            with tf.GradientTape() as tape:
                pre = model(X_train)
                loss = tf.reduce_mean(losses.binary_crossentropy(y_train, pre))
                grad = tape.gradient(loss, model.variables)
                optimizer.apply_gradients(zip(grad, model.variables))
            sum_loss.append(loss.numpy())
            if batch%10==0:
                print("epoch: {} batch: {} loss: {}".format(epoch, batch, tf.reduce_mean(sum_loss)))
        with summary_writer.as_default():
            tf.summary.scalar('loss', tf.reduce_mean(sum_loss), epoch)

    pre = model(X_test)
    pre = [1 if x>0.5 else 0 for x in pre]
    print("Accuracy: ", accuracy_score(y_test, pre))
