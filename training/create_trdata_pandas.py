'''goal of this file: use pandas to organize raw rss files into training data.'''
import pandas as pd
from bs4 import BeautifulSoup
import os
from datetime import datetime as dt
import pickle as pkl

def files_to_simple_df(datadir, max_tr_limit):
    datafiles = os.listdir(datadir)
    print(datafiles[:20])

    list_dfs = []
    for i, fname in enumerate(datafiles):
        if i >= max_tr_limit:
            break

        #open an rss file, convert its html elements to beautiful soup, and extract all links and metadata.
        full_fpath = datadir + '/' + fname
        with open(full_fpath,'rb') as f:
            soup = BeautifulSoup(f.read())
            #print(soup)

            #for each element, need to store it in pandas form. {Can I do this any faster???}
            items = soup.findAll("item")
            for item in items:
                #note: was not able to get the link. That will require some extra work.
                df_item = pd.DataFrame({
                    'title':[item.title.text.strip()],
                    'description':[item.description.text.strip()],
                    'date':[item.pubdate.text.strip()[5:16]]
                })

                #aggregate all "item"-dataframes.
                list_dfs.append(df_item)

    rawitems_df = pd.concat(list_dfs, axis=0).reset_index(drop=True)
    print("#-----------------------------------#\nSimple_DF:")
    print(rawitems_df.head())
    print(rawitems_df.shape)
    return rawitems_df

'''
    Next, convert the html data from raw data to data that is ready for ML:
    Namely, in our input data for ML, we want one row for each ticker and each day.
'''

'''
    Search for tickers within titles, and create a new column for each ticker.
'''
def ticker_label_columns(tickers, rawitems_df):
    l1 = []
    contains_ticker_cols = [rawitems_df]
    for t1 in tickers:
        contains_ti = l1.copy()
        ticker_title = t1.replace(' ','_') #come up with another function, or a dictionary?
        contains_ti = rawitems_df['title'].str.contains(t1, case=False, regex=False).rename(ticker_title)
        contains_ticker_cols.append(contains_ti)
    res1 = pd.concat(contains_ticker_cols, axis=1)
    print("#-----------------------------------#\nSimple_DF with Ticker Label Cols:")
    print(res1.head())
    print(res1.shape)
    return res1


'''
    Group by ticker and date. Combine all the titles into a single list of strings type.
'''
def concat_titles_tk_date(tickers, res1):
    ticker_frames = []
    for t1 in tickers:
        ticker_title = t1.replace(' ','_') ## need something better!
        #selects only the rows of "res1" where the ticker name is present (or res[t1]=True)
        t1_cols = res1[res1[ticker_title]].loc[:,['title','date']]

        #for all the columns sharing a date, merges the titles into a list. Add cols for date & ticker.
        t1_conc_titles = t1_cols.groupby('date')['title'].apply(list).rename('list_titles')
        t1_lengths = t1_conc_titles.agg(len).rename('length')
        r1 = pd.concat([t1_conc_titles, t1_lengths], axis=1)
        t1_res3 = r1.reset_index()
        t1_res3['ticker'] = t1

        ticker_frames.append(t1_res3)
    res2 = pd.concat(ticker_frames,axis=0).reset_index(drop=True) ##this is ready for data analysis.
    print("#-----------------------------------#\nSimple_DF, titles aggregated by Ticker & Date:")
    print(res2.head())
    print(res2.shape)
    return res2


'''
    In this cell, pull in the stock market data from csv files
'''
def extract_combine_historical_stocks(stocks_data_dir, res2):
    stocks_files = os.listdir(stocks_data_dir)

    #for each file, make the file into a pandas dataframe.
    df = pd.DataFrame()
    all_tkr_dfs = []
    for sfile in stocks_files:
        r1 = df.copy()

        full_path = stocks_data_dir + '/' + sfile
        stockdf1 = pd.read_csv(full_path)
        sfile_tkr = sfile[:-4]
        # print(stockdf1.head())

        #convert dates to the right format
        dates = stockdf1['Date'].apply(lambda x: dt.strptime(x,'%m/%d/%Y').strftime('%d %b %Y')).rename('date')
        #require a space (' ') before the key name... Also column names: "stockdf.columns"
        #here we convert string stock price to float.
        close_prc = stockdf1[' Close/Last'].apply(lambda x: float(x.strip()[1:])).rename('Close')
        open_prc = stockdf1[' Open'].apply(lambda x: float(x.strip()[1:])).rename('Open')

        r1 = pd.concat([dates, open_prc, close_prc], axis=1)
        r1['ticker'] = sfile_tkr
        all_tkr_dfs.append(r1)
        #print(r1)

    #combine everything at the end.
    historical_stock_prices = pd.concat(all_tkr_dfs, axis=0).reset_index(drop=True)
    print("#-----------------------------------#\nHistorical Stock movements, FB:")
    print(historical_stock_prices[historical_stock_prices.ticker=='facebook'].head())

    #combine historical stock prices with rss file data.
    r1 = historical_stock_prices
    trdata = res2.join(r1.set_index(['date','ticker']), on=['date', 'ticker'])
    print("#-----------------------------------#\nFinal Training data: Historical Stock Movements + RSS data")
    print(trdata.head())
    return trdata



'''
    MAIN: execute the code listed above.
    Extracts data from the raw files and turns it into pandas trdata.
'''

if __name__ == "__main__":
    ## variables (set manually...)
    datadir = './../test_rss'
    max_tr_limit = 1000
    #come up with more tickers
    tickers = ['facebook','netflix','apple','google','amazon', 'aramco', 'morgan stanley', 'chase']
    stocks_data_dir = '../stock_data'
    trdata_pkl_loc = './pandas_trdata/trdata.pickle'

    #extract data from crawled rss files.
    rawitems_df = files_to_simple_df(datadir, max_tr_limit)
    #add ticker label columns.
    res1 = ticker_label_columns(tickers, rawitems_df)
    #aggregate titles by ticker & date.
    res2 = concat_titles_tk_date(tickers, res1)
    #combine with actual stock data (we will use this as data "labels")
    trdata = extract_combine_historical_stocks(stocks_data_dir, res2)

    #store result as pickle.
    with open(trdata_pkl_loc,'wb') as f:
        pkl.dump(trdata, f)
