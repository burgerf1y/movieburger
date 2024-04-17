from dnn import DNN
import torch
import csv, random

def handlerating(scores):
	ret = scores.copy()
	avai_scores = []
	for score in scores:
		if score > 0:
			avai_scores.append(score)
	avg = sum(avai_scores) / len(avai_scores)
	for i in range(250):
		if scores[i] > 0:
			ret[i] -= avg
		else:
			ret[i] = -0.4
	return ret

def predict(rt):
	rt = [int(i) for i in rt]
	rt_cnt = 0
	for i in rt:
		if i > 0:
			rt_cnt += 1
	if rt_cnt < 5:
		return '<p class="inf">评分数量不足（请至少评价五部）</p>'
	res = torch.zeros(250)
	#models = ['cv_0_1712924931.pt', 'cv_1_1712928010.pt', 'cv_2_1712931007.pt', 'cv_3_1712933854.pt', 'cv_4_1712936559.pt', 'cv_5_1712939586.pt', 'cv_6_1712942603.pt', 'cv_7_1712945916.pt', 'cv_8_1712950346.pt', 'cv_9_1712954250.pt']
	models = ['../models/cv_2_1712931007.pt']
	for i in range(len(models)):
		model = DNN(hidden_size=500, dropout=0)
		model.load_state_dict(torch.load(models[i], map_location='cpu'))
		res += model(torch.Tensor(handlerating(rt)))
	
	for i in range(250):
		if rt[i] > 0:
			res[i] = float('-inf')
	out_num = min(20, 250 - rt_cnt)
	return generation(sorted(enumerate(res), key=lambda x: x[1], reverse=True)[:out_num])

def generation(indices):
	name = []
	id = []
	with open('../data/top250.csv', encoding='utf-8') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			id.append(row[0])
			name.append(row[1])
		
	ret = '<p class="inf">已根据您的评分推荐了至多20部您可能喜欢的电影：</p><p class="add">注意：目前的预测模型仅仅根据一千名用户的观影评分记录学习得到，故预测结果相当不准确。未来我们将努力爬取更多信息，争取为您提供更加可信的预测服务。</p><p class="ans"></p><li>'
	for i in range(len(indices)):
		ret += '<div class="box"><img src="images/burgers/h' + str(random.randint(0,5)) + '.png" width="6%" height="6%" class="burger"><p class="mv_name"><a href="https://movie.douban.com/subject/' + id[indices[i][0]] + '/" target="_blank">' + name[indices[i][0]] + '</a></p></div>'
	ret += '</li>'
	return ret