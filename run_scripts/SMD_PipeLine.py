
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

from run_scripts.plot_tools import plot_anomal_multi_columns,plot_anomal_multi_columns_3d,plot_multi_columns,plot_one_column_with_label,plot_predict, plot_after_train, plot_before_train
from run_scripts.metric_tools import calc_point2point, adjust_predicts,multi_threshold_eval
from run_scripts.utils import train_step,eval_step,train


import tensorflow as tf
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
for device in gpu_devices:
    tf.config.experimental.set_memory_growth(device, True)
    
    
    

    
machine_names = ["machine-1-1", "machine-1-2","machine-1-3", "machine-1-4",  "machine-1-5","machine-1-6",  "machine-1-7", "machine-1-8", 
                 "machine-2-1",  "machine-2-2", "machine-2-3",  "machine-2-4","machine-2-5", "machine-2-6", "machine-2-7",    "machine-2-8",  "machine-2-9", 
                "machine-3-1",  "machine-3-2",  "machine-3-3",  "machine-3-4", "machine-3-5",  "machine-3-6","machine-3-7",  "machine-3-8",   "machine-3-9", "machine-3-10","machine-3-11"]


# machine_names = ["machine-1-8","machine-1-2","machine-1-3","machine-1-4",  "machine-1-5"]

# machine_names = ["machine-1-1","machine-1-6",  "machine-1-7", "machine-2-1",  "machine-2-2", "machine-2-7", "machine-2-8","machine-3-3",  "machine-3-4","machine-3-6", "machine-3-8", "machine-3-11"]

# machine_names = [ "machine-1-2","machine-1-3", "machine-1-4",  "machine-1-5", "machine-1-8", 
#                    "machine-2-3",  "machine-2-4","machine-2-5", "machine-2-6",  "machine-2-9", 
#                  "machine-3-1",  "machine-3-2",  "machine-3-5","machine-3-7",    "machine-3-9", "machine-3-10"]


# machine_names = ["machine-3-5"]


train_suffix = "_train.pkl"
test_suffix = "_test.pkl"
test_label_suffix = "_test_label.pkl"


dataset_name = "SMD"
dataset_dim = 38

def prepare_data(args,machine_name):
    # path
    dataset_dir = args['dataset_dir']
    train_data_path = os.path.join(dataset_dir,machine_name + train_suffix) 
    test_data_path = os.path.join(dataset_dir,machine_name + test_suffix) 
    test_label_path = os.path.join(dataset_dir,machine_name + test_label_suffix) 
    # read
    train_data = pickle.load(open(train_data_path,'rb'))
    test_data = pickle.load(open(test_data_path,'rb'))
    test_label = pickle.load(open(test_label_path,'rb'))
    
    
    # convert to dataframe
    columns = [str(i+1) for i in range(args['dataset_dim'])]
    train_df = pd.DataFrame(train_data,columns=columns)
    test_df = pd.DataFrame(test_data,columns=columns) 
    if args['use_important_cols']:
        train_df = train_df.loc[:,args['important_cols']]
        test_df = test_df.loc[:,args['important_cols']]
     
    if args['use_important_cols']:   
        columns = [str(i+1) for i in range(len(args['important_cols']))]
    
    # normalize
    scaler = StandardScaler()
    train_np = scaler.fit_transform(train_df)
    test_np = scaler.transform(test_df)
    
    # test_with_label
    
    test_with_label = np.concatenate([test_np, test_label.reshape(-1,1)], axis=1)
    test_with_label_df = pd.DataFrame(test_with_label)
    columns.append(args['anomal_col']) # inplace
    test_with_label_df.columns = columns
    test_with_label_df[args['anomal_col']] = test_with_label_df[args['anomal_col']].astype(int)
    
    # plot 
    if args["plot"]:
        plot_before_train(args, df=test_with_label_df)
    
    return train_np, test_np, test_with_label_df 


 

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Tensorflow Training')
    parser.add_argument('--models', type=str, nargs='+', default=[])
    parser.add_argument('--num_gmm', type=int, default=4,help="number of gmm")
    parser.add_argument('--position', type=int, default=99,help="location of a timepoint in a timeseries for energy calculate")
    args = parser.parse_args()
    models = args.models
    print("models: ", models)
    print("num gmm: ",args.num_gmm)
    print("position: ",args.position)
    for m in models:
        for mn in machine_names:
            train(model=m, dataset_name=dataset_name, dataset_dim=dataset_dim, prepare_data=prepare_data, machine_name=mn, num_gmm=args.num_gmm, position=args.position)