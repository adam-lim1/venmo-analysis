# ************************** Initialization **************************

get_ipython().magic('matplotlib inline')

import pandas as pd
import pickle

# PACKAGES FOR WEBCAM IMAGES
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# Packages for AWS
import boto3

client = boto3.client('rekognition')
base_path = 'C:/Users/290002943/Documents/Personal/Venmo Project'

# ************************** Establish AWS Database **************************

# Read pickle file for list of Venmo users
all_user_pics_df = pickle.load(open( '{}/Data/all_user_pics_df.pkl'.format(base_path), "rb" ))

# drop index if needed
try:
    all_user_pics_df = all_user_pics_df.drop('index',axis=1)
except:
    pass

all_user_pics_df = all_user_pics_df.sort_values('username')


# Create AWS collection of faces

if 'venmo_users' not in client.list_collections()['CollectionIds']:
    try:
        response = client.create_collection(CollectionId='venmo_users')
        print('venmo_users collection created')
        print(response)
    except:
        print('Error - collection could not be created')
else:
    print('venmo_users collection already exists')


# Add images to AWS Collection
for row in range(all_user_pics_df.shape[0]):
    try: # Get bytes from image
        with open('{}/Images/{}.jpg'.format(base_path, all_user_pics_df['username'].iloc[row])
                  , 'rb') as target_image:
            target_bytes = target_image.read()
            target_image.close()
        
        #Add bytes to AWS collection with external ID of username
        response = client.index_faces(CollectionId='venmo_users', Image={'Bytes':target_bytes}, ExternalImageId='{}'.format(all_user_pics_df['username'].iloc[row]))
        print('{} successfully added'.format(all_user_pics_df['username'].iloc[row]))
    except:
        print('No image added for {}'.format(all_user_pics_df['username'].iloc[row]))
        