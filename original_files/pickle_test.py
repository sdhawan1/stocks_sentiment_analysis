import pickle as pkl

st = 'sample string'

'''
#initial code: create a file for pickling.
with open('./testfile.pickle', 'wb') as f:
    pkl.dump(st, f)
'''


with open('./testfile.pickle', 'rb') as f:
    data = pkl.load(f)
    print(data)

## works!
