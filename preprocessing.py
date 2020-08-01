
import string
import re
from nltk.corpus import stopwords
import networkx
import pandas as pd

# Dataset: http://snap.stanford.edu/data/amazon-meta.html
fhr = open('./amazon-meta.txt', 'r', encoding='utf-8', errors='ignore')
amazonProductsND = {}

# read the data from the amazon-meta file;
# populate amazonProductsND nested dicitonary;
(Id, ASIN, Title, Categories, Group, Copurchased, SalesRank, TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff) = \
    ("", "", "", "", "", "", 0, 0, 0.0, 0, 0.0)
for line in fhr:
    line = line.strip()
    # a product block started
    if(line.startswith("Id")):
        Id = line[3:].strip()
    elif(line.startswith("ASIN")):
        ASIN = line[5:].strip()
    elif(line.startswith("title")):
        Title = line[6:].strip()
        Title = ' '.join(Title.split())
    elif(line.startswith("group")):
        Group = line[6:].strip()
    elif(line.startswith("salesrank")):
        SalesRank = line[10:].strip()
    elif(line.startswith("similar")):
        ls = line.split()
        Copurchased = ' '.join([c for c in ls[2:]])
    elif(line.startswith("categories")):
        ls = line.split()
        Categories = ' '.join((fhr.readline()).lower() for i in range(int(ls[1].strip())))
        Categories = re.compile('[%s]' % re.escape(string.digits+string.punctuation)).sub(' ', Categories)
        Categories = ' '.join(set(Categories.split())-set(stopwords.words("english")))
    elif(line.startswith("reviews")):
        ls = line.split()
        TotalReviews = ls[2].strip()
        AvgRating = ls[7].strip()

    elif (line==""):
        try:
            MetaData = {}
            if (ASIN != ""):
                amazonProductsND[ASIN]=MetaData
            MetaData['Id'] = Id            
            MetaData['Title'] = Title
            MetaData['Categories'] = ' '.join(set(Categories.split()))
            MetaData['Group'] = Group
            MetaData['Copurchased'] = Copurchased
            MetaData['SalesRank'] = int(SalesRank)
            MetaData['TotalReviews'] = int(TotalReviews)
            MetaData['AvgRating'] = float(AvgRating)
            MetaData['DegreeCentrality'] = DegreeCentrality
            MetaData['ClusteringCoeff'] = ClusteringCoeff
        except NameError:
            continue
        (Id, ASIN, Title, Categories, Group, Copurchased, SalesRank, TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff) = \
            ("", "", "", "", "", "", 0, 0, 0.0, 0, 0.0)
fhr.close()

# create books-specific dictionary exclusively for books
amazonBooksND = {}
for asin,metadata in amazonProductsND.items():
    if (metadata['Group']=='Book'):
        amazonBooksND[asin] = amazonProductsND[asin]
    
# remove any copurchased items from copurchase list 
# if we don't have metadata associated with it 
for asin, metadata in amazonBooksND.items(): 
    amazonBooksND[asin]['Copurchased'] = \
        ' '.join([cp for cp in metadata['Copurchased'].split() \
            if cp in amazonBooksND.keys()])

copurchaseGraph = networkx.Graph()
for asin,metadata in amazonBooksND.items():
    copurchaseGraph.add_node(asin)
    for a in metadata['Copurchased'].split():
        copurchaseGraph.add_node(a.strip())
        similarity = 0        
        n1 = set((amazonBooksND[asin]['Categories']).split())
        n2 = set((amazonBooksND[a]['Categories']).split())
        n1In2 = n1 & n2
        n1Un2 = n1 | n2
        if (len(n1Un2)) > 0:
            similarity = round(len(n1In2)/len(n1Un2),2)
        copurchaseGraph.add_edge(asin, a.strip(), weight=similarity)

dc = networkx.degree(copurchaseGraph)
for asin in networkx.nodes(copurchaseGraph):
    metadata = amazonBooksND[asin]
    metadata['DegreeCentrality'] = int(dc[asin])
    ego = networkx.ego_graph(copurchaseGraph, asin, radius=1)
    metadata['ClusteringCoeff'] = networkx.clustering(ego, asin)
    amazonBooksND[asin] = metadata

# convert amazonBooks metadata to pandas dataframe and drop redundant columns
amazonBooks = pd.DataFrame(amazonBooksND).T
amazonBooks.drop(columns=['Copurchased', 'Group'], axis=1, inplace=True)
amazonBooks.to_csv('./amazon-books.csv', index=True, header=True)

fhw=open("amazon-books-copurchase.edgelist",'wb')
networkx.write_weighted_edgelist(copurchaseGraph, fhw)
fhw.close()