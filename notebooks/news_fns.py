'''
    Take care of all data storage functions within this file
'''
from keras.preprocessing.text import text_to_word_sequence
from keras.preprocessing.text import one_hot
import numpy as np
from sklearn.model_selection import train_test_split

import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import TensorDataset, Dataset, DataLoader


###  take all the words and convert them to tokens. Return the hash size, vocab size, etc.
'''
    input: titles needs to be a list of all the titles only
    return: tokenized versions of all titles; plus total vocab size
'''
def tokenize_titles(titles):
    allwds = ' '.join(titles)
    vocab_size = len(set( text_to_word_sequence(allwds) ))
    hash_size = int(vocab_size * 1.3)
    
    #tokenize all the training data.
    titles_tokenized = [np.array(one_hot(t, hash_size)) for t in titles]
    titles_tokenized = np.array(titles_tokenized)
    
    ### note: you need to pad out the above ^^ to make the batch line up. 
    
    print("tokenized titles: ")
    print(titles_tokenized.shape)
    print(titles_tokenized[0])
    print(titles_tokenized[1])
    print(titles_tokenized[2])
    return titles_tokenized, hash_size


def tokenize_pad_titles(titles_raw):
    #first, tokenize
    titles, hash_size = tokenize_titles(titles_raw)
    #debug
    #print("### debug: titles input: {}".format(titles))
    titles_tokenized = [torch.tensor(t) for t in titles]
    title_lens = [len(t) for t in titles_tokenized]
    maxlen = max(title_lens)
    print("\ntitle lengths: ")
    print(title_lens[:10])
    print("max length:")
    print(maxlen)
    
    #now add padding to all arrays (this also concatenates all tensors!)
    print("\nadding padding to titles...")
    titles_tok_padded = pad_sequence(titles_tokenized, batch_first=True, padding_value=0)
    print(titles_tok_padded)
    return titles_tok_padded, title_lens, hash_size

#----------------------------------------------------#
### create a dataset and a dataloader

# new class: dataset with the news headline sentences
class SentencesDataset(Dataset):
  def __init__(self, titles_nparr, title_lens, labels):
    self.titles = titles_nparr
    self.title_lens = title_lens
    self.labels = labels
  def __len__(self):
    return len(self.titles)
  def __getitem__(self, idx):
    t = self.titles[idx]
    s = self.title_lens[idx]
    l = self.labels[idx]
    return {'title': t, 'length':s, 'label': l}


'''
    this function takes article titles & labels, and converts them into a proper dataset.
'''
def create_dataset_dataloader(titles_raw, labels, bsize=32, test_ratio=0.1):
    #preprocessing steps...
    titles_tok_padded, title_lens, hash_size = tokenize_pad_titles(titles_raw)
    print("\ntokenized & padded titles array shape: {}".format(titles_tok_padded.shape))
    
    #split into train & validation
    print("\nsplitting into training & test datasets...")
    tr_test_data = train_test_split(titles_tok_padded, labels, title_lens, 
                                  random_state=2018, test_size=test_ratio)
    train_inputs, validation_inputs, train_labels, validation_labels, train_lens, validation_lens = tr_test_data
    
    print(validation_inputs[:10])
    print(validation_labels[:10])
    print(validation_lens[:10])
    
    #create a dataloader.
    train_1 = SentencesDataset(train_inputs, train_lens, train_labels)
    train_loader = DataLoader(train_1, batch_size= bsize)
    
    val_1 = SentencesDataset(validation_inputs, validation_lens, validation_labels)
    val_loader = DataLoader(val_1, batch_size= bsize)
    
    #check dataloader appearance
    print("\nchecking dataloader apppearance:")
    for batch in train_loader:
        print(batch)
        break
    
    return train_loader, val_loader, titles_tok_padded, title_lens, hash_size