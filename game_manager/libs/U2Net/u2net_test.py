import os
from skimage import io, transform
import torch
import torchvision
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms#, utils
# import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import glob

from .data_loader import RescaleT
from .data_loader import ToTensor
from .data_loader import ToTensorLab
from .data_loader import SalObjDataset

from .model import U2NET # full size version 173.6 MB
from .model import U2NETP # small version u2net 4.7 MB

# normalize the predicted SOD probability map
def normPRED(d):
    ma = torch.max(d)
    mi = torch.min(d)

    dn = (d-mi)/(ma-mi)

    return dn

def save_output(pred, image_rgba):

    predict = pred
    predict = predict.squeeze()
    predict_np = predict.cpu().data.numpy()

    im = Image.fromarray(predict_np*255).convert('RGB')

    imo = im.resize((image_rgba.shape[1],image_rgba.shape[0]),resample=Image.BILINEAR)

    pb_np = np.array(imo)

    return pb_np

def main(image_rgba=None):
    # --------- 1. get image path and name ---------
    model_name='u2netp'# fixed as u2netp

    script_dir = os.path.dirname(".")


    model_dir = os.path.join(script_dir, model_name + '.pth') # path to u2netp pretrained weights

    # --------- 2. dataloader ---------
    #1. dataloader
    test_salobj_dataset = SalObjDataset(transform=transforms.Compose([RescaleT(320),
                                        ToTensorLab(flag=0)]), image_rgba=image_rgba)
    test_salobj_dataloader = DataLoader(test_salobj_dataset,
                                        batch_size=1,
                                        shuffle=False,
                                        num_workers=1)

    # --------- 3. model define ---------
    net = U2NETP(3,1)    
    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_dir))
        net.cuda()
    else:        
        net.load_state_dict(torch.load(model_dir, map_location=torch.device('cpu')))

    net.eval()

    # --------- 4. inference for each image ---------
    for i_test, data_test in enumerate(test_salobj_dataloader):
        print(i_test)

        inputs_test = data_test['image']
        inputs_test = inputs_test.type(torch.FloatTensor)

        if torch.cuda.is_available():
            inputs_test = Variable(inputs_test.cuda())
        else:
            inputs_test = Variable(inputs_test)

        d1,d2,d3,d4,d5,d6,d7= net(inputs_test)

        # normalization
        pred = d1[:,0,:,:]
        pred = normPRED(pred)

        alpha = save_output(pred, image_rgba)

        del d1,d2,d3,d4,d5,d6,d7
        return alpha

if __name__ == "__main__":
    main()
