# MovieBurger
MovieBurger是一个基于爬虫和机器学习的豆瓣电影推荐工具。
## crawler
crawler会对豆瓣Top250电影的用户评分信息进行爬取，由三个python文件组成。
### get_top250.py
逐页访问豆瓣Top250电影的页面，使用requests + bs4爬取250部电影的简体中文名称和id，并将结果保存在data目录下的top250.csv文件中。
### get_user.py
为了获取足够数量的用户id，我们采用的方法是给定一个起始用户，递归地查找其关注的用户和其粉丝，从而能迅速地获得海量的用户id。

上述过程的难点在于需要登录豆瓣才可以查看用户的关注列表和粉丝列表。聪明的你需要自行手动登录豆瓣，登录成功后，在终端输入任何字符，程序便会开始递归执行，与此同时将用户id写入data目录下的user.csv文件。

注意，运行get_user.py前，需要先在data目录下的users.csv中写入起始用户的id，例如whiterhinoceros.
### get_rating.py
对于get_user.py中得到的用户进行遍历，选择看过五十部以上的电影、且评分过十部以上Top250电影的用户的评分进行记录，写入data目录下的user_rating.csv文件。
## MLP
MLP将爬取到的用户评分数据传入DNN进行训练。

用户的评分将通过utils.py中的randhandlerating方法进行一定程度的随机化，在经过DNN模型的前向传播后，与原始数据通过ModifiedMarginRankingLoss计算出los
，再进行反向传播。

数据集划分：采用k-fold交叉验证。80%的数据用于训练，且其中10%作为验证集，剩余20%的数据将作为测试集.
