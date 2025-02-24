
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import datetime as dt
from datetime import datetime,tzinfo
import scipy, json, csv, time, pytz
from pytz import timezone
import numpy as np
import pandas as pd
import os
import pickle

from run_scripts.plot_tools import plot_anomal_multi_columns,plot_anomal_multi_columns_3d,plot_multi_columns,plot_one_column_with_label,plot_predict, plot_after_train,plot_before_train
from run_scripts.metric_tools import calc_point2point, adjust_predicts,multi_threshold_eval
from run_scripts.utils import train_step,eval_step,train

import tensorflow as tf
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
for device in gpu_devices:
    tf.config.experimental.set_memory_growth(device, True)
      
dataset_name = "SYN"
dataset_dim = 5


def prepare_data(args):
    args['model_dir'] = "run_scripts/out/models"
    # path
    dataset_dir = args['dataset_dir']
    train_data_path = os.path.join(dataset_dir,"train.csv") 
    test_data_path = os.path.join(dataset_dir,"test.csv") 
    # read
    train_data=pd.read_csv(train_data_path)
    test_data = pd.read_csv(test_data_path)
    rows = train_data.shape[0]
    train_num = int(rows * 0.5)
    
    train_np = train_data.values[:,:4] 
    test_np = test_data.values[:,:4]  
    test_label_np = test_data.values[:,:4]  
    
    train_np = np.nan_to_num(train_np)
    test_np = np.nan_to_num(test_np)
    test_with_label_np = np.nan_to_num(test_label_np)
    
    # normalize
    scaler = StandardScaler()
    train_np = scaler.fit_transform(train_np)
    test_np = scaler.transform(test_np)

    # test_with_label
    columns = [str(i+1) for i in range(args['dataset_dim'])]
    
    test_with_label_np[:,:4] = test_np
    test_with_label_df = pd.DataFrame(test_with_label_np)
    columns.append(args['anomal_col']) # inplace
    test_with_label_df.columns = columns
    test_with_label_df[args['anomal_col']] = test_with_label_df[args['anomal_col']].astype(int)    

    
    # plot 
    if args["plot"]:
        plot_before_train(args, df=test_with_label_df)
    
    return train_np, test_np, test_with_label_df 


if __name__ == "__main__":
    # models = ["DAGMM","lstmod", "LSTMAE","LSTMVAE", "telemanom","deeplog", "LSTMVAEGMM","LSTMAEGMM","GRUVAEGMM","LSTMVAEDISTGMM"]
    import argparse
    parser = argparse.ArgumentParser(description='Tensorflow Training')
    parser.add_argument('--models', type=str, nargs='+', default=[],help="train models")
    parser.add_argument('--num_gmm', type=int, default=4,help="number of gmm")
    parser.add_argument('--position', type=int, default=99,help="location of a timepoint in a timeseries for energy calculate")
    args = parser.parse_args()
    models = args.models
    print("models: ", models)
    print("num gmm: ",args.num_gmm)
    for m in models:
        print(f" < * > {m} " * 20)
        train(
            m,
            dataset_name=dataset_name,
            dataset_dim=dataset_dim,
            prepare_data=prepare_data,
            num_gmm=args.num_gmm,
            position=args.position
            )