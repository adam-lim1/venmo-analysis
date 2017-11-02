# ************************** Initialization **************************

import pandas as pd
import pickle
import time

# Text cleaning packages
import emoji
import unicodedata as uni
from unidecode import unidecode
import re
from nltk.corpus import stopwords # had to use nltk.download('stopwords') to download stopwords
from nltk.stem import WordNetLemmatizer
import string
from bs4 import BeautifulSoup
from codes import codes # emoji codes py file

# Packages for downloading images
import urllib

# Define list of stop words, punctuation to remove
stopWords = set(stopwords.words('english'))
exclude = set(string.punctuation)

## FUNCTION FIND EMOJIS IN TEXT
def extract_emojis(str):
    return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)

def remove_punctuation(s):
    s = ''.join([i for i in s if i not in exclude])
    return s

class Emoji:
  def __init__(self, const):
    if len(const) == 1:
      self.__fromUnicode(const)
    elif const[0] == ":":
      self.__fromAlias(const)
    else:
      self.__fromEscape(const)
    self.aliases = codes[self.escape]
    self.alias = self.aliases[0]
    self.char = bytes("\\u"+self.escape, "ascii").decode("unicode-escape")[0]
    self.is_supported = hex(ord(self.char))[2:] == self.escape

  def __fromUnicode(self, char):
    escape = hex(ord(char))[2:]
    if escape in codes:
      self.escape = escape
    else:
      raise ValueError

  def __fromAlias(self, alias):
    for k, v in codes.items():
      if alias in v:
        self.escape = k
        break
    else:
      raise ValueError

  def __fromEscape(self, escape):
    if escape in codes.keys():
      self.escape = escape
    else:
      raise ValueError

def replaceAliases(text, trailingSpaces=0, force=False):
  """ Replaces all supported emoji-cheat-sheet aliases in a text with the corresponding emoji. """
  def replAlias(m):
    alias = ":"+m.group(1)+":"
    if not Emoji(alias).is_supported and not force:
      return alias
    try:
      return Emoji(alias).char + trailingSpaces * " "
    except ValueError:
      return alias
  return re.sub(":([^s:]?[\w-]+):", replAlias, text)

def replaceEmoji(text, trailingSpaces=0):
  """ Replaces all emojis with their primary emoji-cheat-sheet alias. """
  i = 0
  while i < len(text):
    escape = hex(ord(text[i]))[2:]
    if escape in codes.keys():
      text = text.replace(text[i] + trailingSpaces*" ", Emoji(escape).alias)
      i += len(Emoji(escape).alias)
    else:
      i += 1
  return text

base_path = 'C:/Users/290002943/Documents/Personal/Venmo Project'


# ************************** Clean Data **************************


# Read in dataframe
venmo_trans = pickle.load(open( '{}/Data/venmo_trans.pkl'.format(base_path), "rb" ) )

# Remove punctuation
venmo_trans['message_no_punc'] = venmo_trans['message'].apply(remove_punctuation)

# Remove stop words
venmo_trans['message_no_stop'] = venmo_trans['message_no_punc'].apply(lambda x: [item for item in x.split() if item not in stopWords])

# Stem words
wordnet_lemmatizer = WordNetLemmatizer()
venmo_trans['message_stemmed'] = venmo_trans['message_no_stop'].apply(lambda msg_list: [wordnet_lemmatizer.lemmatize(element) for element in msg_list])

# Remove emojis
venmo_trans['emoji_replaced'] = venmo_trans['message_stemmed'].apply(lambda msg_list: [replaceEmoji(word).replace("::", ": :") for word in msg_list])

venmo_trans['message_lol'] = venmo_trans['emoji_replaced'].apply(lambda msg_list: [element.split() for element in msg_list])

venmo_trans['message_cleaned']= venmo_trans['message_lol'].apply(lambda msg_list: [val for sublist in msg_list for val in sublist])


# Create subset df with columns we are interested in
trans_subset = venmo_trans[['actor.username', 
                            'actor.picture', 
                            'created_time',
                            'message',
                            'message_cleaned',
                            'story_id', 
                            'target.username', 
                            'target.picture', 
                            'type']]


trans_cols = ['actor_username', 'actor_picture', 'created_time', 'message', 'message_cleaned','story_id', 'target_username', 'target_picture', 'type']
trans_subset.columns = trans_cols

# Write trans subset to pickle
trans_subset.to_pickle('{}/Data/trans_subset.pkl'.format(base_path), compression='infer')

# ************************** Get User Pictures **************************

# Get Actors
actor_pics_df = trans_subset[['actor_username', 'actor_picture']]
actor_pics_df = actor_pics_df.rename(columns={'actor_username':'username', 'actor_picture':'picture'})

# Get Targets
target_pics_df = trans_subset[['target_username', 'target_picture']]
target_pics_df = target_pics_df.rename(columns={'target_username':'username', 'target_picture':'picture'})

# Combine and drop duplicates
all_user_pics_df = actor_pics_df.append(target_pics_df)
all_user_pics_df.drop_duplicates(inplace=True)
all_user_pics_df.reset_index(inplace=True, drop=True)

all_user_pics_df = all_user_pics_df.sort_values('username')

# Drop users that have no picture
all_user_pics_df = all_user_pics_df[all_user_pics_df['picture'] != 'https://s3.amazonaws.com/venmo/no-image.gif']

# Write users to pickle
all_user_pics_df.to_pickle('{}/Data/all_user_pics_df.pkl'.format(base_path), compression='infer')

# Open and download all pics
for i in range(0,all_user_pics_df.shape[0]):
    try:
        urllib.request.urlretrieve(all_user_pics_df['picture'][i], 
                               '{}/Images/{}.jpg'.format(base_path, all_user_pics_df['username'][i]))
        if i%10 == 0:
            print(i,'/', all_user_pics_df.shape[0], 'done')
    except:
        print("Couldn't find picture")

