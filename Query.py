# ************************** Initialization **************************
get_ipython().magic('matplotlib inline')

import pandas as pd
import pickle

# PACKAGES FOR WEBCAM IMAGES
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

# PACKAGES FOR AWS
import boto3

# TOPIC MODELING PACKAGES
import gensim 
from gensim import corpora

base_path = 'C:/Users/290002943/Documents/Personal/Venmo Project'

# Define function to take picture from webcam
camera_port = 0 
ramp_frames = 30 

def take_pic():
    camera = cv2.VideoCapture(camera_port)
    for i in range(ramp_frames):
        temp = camera.read()
    retval, camera_capture = camera.read() # Get image
    filename = '{}/Images/webcam_capture.jpg'.format(base_path)
    cv2.imwrite(filename,camera_capture)
    del(camera)
    
    img=mpimg.imread('{}/Images/webcam_capture.jpg'.format(base_path))
    plt.axis('off')
    imgplot = plt.imshow(img)
    return('Picture captured')


# Read in transaction dataframe
trans_subset = pickle.load(open( '{}/Data/trans_subset.pkl'.format(base_path), "rb" ))

client = boto3.client('rekognition')

# ************************** Get image from webcam **************************
take_pic()


# ************************** Search AWS database for match **************************

with open('{}/Images/webcam_capture.jpg'.format(base_path), 'rb') as target_image:
        target_bytes = target_image.read()
        target_image.close()

response = client.search_faces_by_image(CollectionId='venmo_users', Image={'Bytes':target_bytes}, MaxFaces=1, FaceMatchThreshold=75)


if len(response['FaceMatches'])==0:
    print('Face not found in database')
else:
    image_id = (response['FaceMatches'])[0]['Face']['ExternalImageId']
    print('Face found in database as', image_id)
    img=mpimg.imread('{}/Images/{}.jpg'.format(base_path, image_id))
    plt.axis('off')
    imgplot = plt.imshow(img)

# ************************** Get insights on user **************************

actor_transactions = trans_subset.query('actor_username == "{}" or target_username=="{}"'.format(image_id, image_id))
actor_transactions

sender = actor_transactions[actor_transactions['actor_username']!='{}'.format(image_id)]['actor_username'].mode().loc[0]
send_count = actor_transactions[actor_transactions['actor_username']=='{}'.format(sender)].shape[0]
print('{} was paid the most number of times by {} ({})'.format(image_id, sender, send_count))

reciever = actor_transactions[actor_transactions['target_username']!='{}'.format(image_id)]['target_username'].mode().loc[0]
recieve_count = actor_transactions[actor_transactions['target_username']=='{}'.format(sender)].shape[0]
print('{} paid {} the most number of times ({})'.format(image_id, reciever, recieve_count))


# ### Topic Modeling

text_doc = actor_transactions['message_cleaned']

text_doc.tolist()

dictionary = corpora.Dictionary(text_doc)

# Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
doc_term_matrix = [dictionary.doc2bow(doc) for doc in text_doc]

# Creating the object for LDA model using gensim library
Lda = gensim.models.ldamodel.LdaModel

# Running and Trainign LDA model on the document term matrix
ldamodel = Lda(doc_term_matrix, num_topics=3, id2word = dictionary, passes=50)

print(ldamodel.print_topics(num_topics=3, num_words=3))