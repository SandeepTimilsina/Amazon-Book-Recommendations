
import networkx
from operator import itemgetter
import matplotlib.pyplot
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import MinMaxScaler

amazonBooks = pd.read_csv('./amazon-books.csv', index_col=0)
fhr = open("amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph = networkx.read_weighted_edgelist(fhr)
fhr.close()

print("Looking for Recommendations for Customer Purchasing this Book:")
print("--------------------------------------------------------------")
purchasedAsin = '0805047905'

def scaleData(df):
    numericvars = ['AvgRating', 'TotalReviews', 'DegreeCentrality']
    mms = MinMaxScaler()
    dfnumss = pd.DataFrame(mms.fit_transform(df[numericvars]), columns=['mms_' + x for x in numericvars],
                           index=df.index)
    dfnumss = pd.concat([df, dfnumss], axis=1)
    dfnumss = dfnumss.drop(numericvars, axis=1)

    numericabsvars = ['SalesRank']
    mas = MaxAbsScaler()
    dfnummas = pd.DataFrame(mas.fit_transform(dfnumss[numericabsvars]), columns=['mas_' + x for x in numericabsvars],
                            index=df.index)
    dfnummas = pd.concat([dfnumss, dfnummas], axis=1)
    dfnummas = dfnummas.drop(numericabsvars, axis=1)
    return dfnummas

amazonBooks = scaleData(amazonBooks).copy()

'''
def getTop5weights(purchasedAsin):
    my_dict = []
    a = copurchaseGraph[purchasedAsin]

    for k, v in a.items(): my_dict.append((k, v['weight']))
    topList = sorted(my_dict, key=itemgetter(1), reverse=True)
    if topList[5][1]==topList[6][1]:
        return topList[:10]
    else:
        return topList[:5]

a=getTop5weights('0805047905')
'''

amazonBooks = amazonBooks.rename(
    columns={'mas_SalesRank': 'SalesRank', 'mms_TotalReviews': 'TotalReviews', 'mms_AvgRating': 'AvgRating',
             'mms_DegreeCentrality': 'DegreeCentrality'})

# Let's first get some metadata associated with this book
print("ASIN = ", purchasedAsin)
print("Title = ", amazonBooks.loc[purchasedAsin, 'Title'])
print("SalesRank = ", amazonBooks.loc[purchasedAsin, 'SalesRank'])
print("TotalReviews = ", amazonBooks.loc[purchasedAsin, 'TotalReviews'])
print("AvgRating = ", amazonBooks.loc[purchasedAsin, 'AvgRating'])
print("DegreeCentrality = ", amazonBooks.loc[purchasedAsin, 'DegreeCentrality'])
print("ClusteringCoeff = ", amazonBooks.loc[purchasedAsin, 'ClusteringCoeff'])

purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph, purchasedAsin, radius=1)
threshold = 0.5
gIslands = networkx.Graph()
for f, t, e in purchasedAsinEgoGraph.edges(data=True):
    if e['weight'] >= threshold:
        gIslands.add_edge(f, t, weight=e['weight'])
purchasedAsinEgoTrimGraph = gIslands

purchasedAsinNeighbors = []
purchasedAsinNeighbors = [i for i in purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)]


def extractInfoNeighbors(purchasedAsinNeighbors):
    df = amazonBooks[amazonBooks.index.isin(purchasedAsinNeighbors)].copy()
    df['WeightedReviews'] = df['AvgRating'] * df['TotalReviews']
    df['CompositeScore'] = df['WeightedReviews'] * df['ClusteringCoeff'] * df['DegreeCentrality']

    numericabsvars = ['CompositeScore']
    mas_composite = MaxAbsScaler()
    dfnummas = pd.DataFrame(mas_composite.fit_transform(df[numericabsvars]),
                            columns=['mas_' + x for x in numericabsvars],
                            index=df.index)
    dfnummas = pd.concat([df, dfnummas], axis=1)
    dfnummas = dfnummas.drop(numericabsvars, axis=1)

    df.sort_values(by=['CompositeScore', 'SalesRank'], ascending=[False, True], inplace=True)
    # df.to_excel("output.xlsx") vaidate the data by saving into excel
    if (df.__len__())>5:# handling what if the neighbors are less than 5
        return df[:5]
    else:
        return df


top5recommend = extractInfoNeighbors(purchasedAsinNeighbors)

# Recommendations
print("================================================================")
print("Recommendations for ", purchasedAsin, "  in Tabular format")
print("================================================================")
print(top5recommend)
print("================================================================")
print()
print('Recommendation for ',purchasedAsin,' in a dictionary format')
print(top5recommend.to_dict())
