Data Source : http://snap.stanford.edu/data/amazon-meta.html
Use Amazon Product Co-purchase data to make Book Recommendations using Network Analysis.

**Logic Behind Top 5 Recommendations**

After Scaling the features using minmaxscaler and MaxAbsScaler we go ahead to calculate our composite Score. The composite Score is scaled using MaxAbsScaler.

Reasons behind the parameters used to calculate the Composite score.

 Average Ratings are based on the Total Reviews. Hence if the product is graded by 5 people and we get a rating of 5 and if the same product is rated by 1000 people we get a rating of 4.5, we have to prefer the 1000 people rating as that would a representative sample with less bias and variance. Hence, we multiply the AvgRating with Total Reviews and create a new column called Weighted Reviews.

We want nodes that are fully connected and have the maximum number of connections to give best recommendations as they are ego neighbors at depth 1 meaning they are close and Clustering coefficient shows how those neighbors are connected to each other . Thus, we pick degree centrality and Clustering coefficient to decide our composite score.
Degree centrality is the number of nodes at depth one. The nodes with more degree tend to have more power and is more visible. Clustering Coefficient which measures the proportion of ego’s friend that are also friends with each other ranges from having a single broadcast node having low coefficient to fully connected network called as clique(star 0<=Clustering Coefficient(v)<=1(clique), where ‘v’ is the node for which the clustering coefficient is calculated.

Thus, we multiply the clustering coefficients with degree centrality as we want to prioritize nodes with higher degree and high clustering coefficient score.
 
The composite score calculated gives in good understanding of the books with high value and to recommend. However, we still have not factored SalesRank. Lower Sales Rank means that the product is the best seller. Taking the items with top 5 composite score and recommending them based on the ascending values of the SalesRank makes the most sense here and I proceeded with the same approach.

To Summarize,

Mathematically.

i)	Composite score = Max( degree centrality * clustering coefficient * weighted Reviews)

ii)	Recommendedtop5= sort Composite Score by Sales rank Ascending.



