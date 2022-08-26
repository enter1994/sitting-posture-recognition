import timeit
import time
import os
import wandb
from tqdm.auto import tqdm

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

import torch
from torch import nn, optim

def evaluate(args, experiment, model, test_dataloader, test_size, criterion, ep):
   
    if torch.cuda.is_available():
        device = f'cuda:{args.gpu_number}'
        
    model.eval()
    start_time = timeit.default_timer()

    running_loss = 0.0
    running_corrects = 0.0

    y_pred = []
    y_true = []
    
    for inputs, labels in tqdm(test_dataloader):
        inputs = inputs.to(device)
        labels = labels.to(device)

        with torch.no_grad():
            outputs, corr = model(inputs)

        probs = nn.Softmax(dim=1)(outputs)
        probs = outputs
        preds = torch.max(probs, 1)[1]
        loss = criterion(outputs, labels)
        
        y_true.extend(labels.cpu().numpy())
        y_pred.extend(preds.cpu().numpy())
        # print('y_pred', y_pred)
        # print('y_true', y_true)

        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)

    epoch_loss = running_loss / test_size
    epoch_acc = running_corrects.double() / test_size

    print("[test] Loss: {} Acc: {}".format(epoch_loss, epoch_acc))
    stop_time = timeit.default_timer()
    print("Execution time: " + str(stop_time - start_time) + "\n")

    if ep == 1 and args.wandb:
        cf_matrix = confusion_matrix(y_true, y_pred)
        class_names = ('sit', 'shake', 'cross', 'slouch', 'left', 'right')
        dataframe = pd.DataFrame(cf_matrix, index=class_names, columns=class_names)
        sns.heatmap(dataframe, annot=True, cbar=None,cmap="YlGnBu",fmt="d")

        plt.title("Confusion Matrix")
        plt.ylabel("True Class"), 
        plt.xlabel("Predicted Class")
        plt.savefig('./images/confusion_matrix_test.jpg')
        experiment.log({'test_loss': epoch_loss, 'test_acc': epoch_acc, 'confusion_matrix_test': wandb.Image('./images/confusion_matrix_test.jpg')})
    else:
        experiment.log({'test_loss': epoch_loss, 'test_acc': epoch_acc})

def train_video(args, experiment, model, train_dataloader, test_dataloader, train_size, test_size):
    
    # standard crossentropy loss for classification
    criterion = nn.CrossEntropyLoss()  
    optimizer = optim.SGD(model.parameters(), lr=args.learning_rate)
    # the scheduler divides the lr by 10 every 10 epochs
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)  
    
    if torch.cuda.is_available():
        device = f'cuda:{args.gpu_number}'
    
    model.to(device)
    criterion.to(device)
    print('model loaded')
    
    for epoch in range(args.epochs):
        start_time = timeit.default_timer()

        # reset the running loss and corrects
        running_loss = 0.0
        running_corrects = 0.0

        # scheduler.step() is to be called once every epoch during training
        # scheduler.step()
        model.train()
        
        for inputs, labels in tqdm(train_dataloader):
            inputs = inputs.to(device) 
            # print(inputs.shape)
            labels = labels.to(device) 
            # print(labels.shape)
            optimizer.zero_grad()

            outputs, corr = model(inputs)
            print('logits', outputs)

            probs = nn.Softmax(dim=1)(outputs)
            probs = outputs
            
            preds = torch.max(probs, 1)[1] # indicies

            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            # print(labels.data)

        epoch_loss = running_loss / train_size
        epoch_acc = running_corrects.double() / train_size
            
        print("[{}] Epoch: {}/{} Loss: {} Acc: {}".format('train', epoch+1, args.epochs, epoch_loss, epoch_acc))
        stop_time = timeit.default_timer()
        print("Execution time: " + str(stop_time - start_time) + "\n")

        if args.wandb:
            experiment.log({"train_loss": epoch_loss, "train_acc": epoch_acc})
            
        evaluate(args, experiment, model, test_dataloader, test_size, criterion, 0)

        if epoch + 1 == args.epochs:
            torch.save({
                'epoch': epoch + 1,
                'state_dict': model.state_dict(),
                'opt_dict': optimizer.state_dict(),
            }, os.path.join(args.chkt_filename, 'C3D-video-epoch-' + str(args.epochs) + '.pth'))
            print("Save model at {}\n".format(os.path.join(args.chkt_filename, 'C3D-video-epoch-' + str(args.epochs) + '.pth')))
   
    # Eval using Test set
    evaluate(args, experiment, model, test_dataloader, test_size, criterion, 1)