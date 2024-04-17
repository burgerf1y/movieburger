from dnn import DNN
from utils import RtDataset, train_model, evaluate_model, ModifiedMarginRankingLoss
import torch, time, argparse, csv
import torch.optim as optim
import wandb

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="GNN Trainer")
	parser.add_argument("--cross-valid", help="cross-validation num 0-9", default=0, type=int)
	args = parser.parse_args()
	i = args.cross_valid
	device = "cuda:0"

	row = 0
	with open('../data/user_rating.csv', encoding = 'utf-8') as csvfile:
		reader = csv.reader(csvfile)
		for j in reader:
			row += 1
	ratings = list(range(row))
	test_ratings = ratings[-row//5:]
	train_len = row - len(test_ratings)
	val_ratings = ratings[(train_len//10)*i:(train_len//10)*(i+1)]
	train_ratings = ratings[:(train_len//10)*i] + ratings[(train_len//10)*(i+1):train_len]

	train_set = RtDataset(train_ratings)
	val_set = RtDataset(val_ratings)
	test_set = RtDataset(test_ratings)

	wandb.init(
        project="burger",
        config={
        	"des": "3mlp",
			"cv": i
        }
    )
	model = DNN(hidden_size=500, dropout=0).to(device=device)
	optimizer = optim.Adam(model.parameters(), lr = 1e-3, weight_decay=1e-4)
	scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, verbose=True)
	loss_fn = ModifiedMarginRankingLoss(device=device)

	train_losses, val_losses = train_model(model=model, batchSize=1, trainset=train_set, valset=val_set, optimizer=optimizer, scheduler=scheduler, num_epochs=20, device=device, loss_fn=loss_fn)
	res = evaluate_model(model, test_set, loss_fn)
	wandb.log({"test-loss": res[0], "test-best": res[1]})

	FileName = 'cv_' + str(i) + '_' + str(int(time.time()))
	torch.save(model.state_dict(), FileName+".pt")
