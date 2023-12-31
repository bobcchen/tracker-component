import os 
import logging

import cv2
import numpy as np
import pkg_resources
import torch
from torchvision.transforms import transforms

from deep_sort_realtime.embedder.mobilenetv2_bottle import MobileNetV2_bottle

log_level = logging.DEBUG
logger = logging.getLogger('Embedder for Deepsort')
logger.setLevel(log_level)
handler = logging.StreamHandler()
handler.setLevel(log_level)
formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

MOBILENETV2_BOTTLENECK_WTS = pkg_resources.resource_filename('deep_sort_realtime', 'embedder/weights/mobilenetv2_bottleneck_wts.pt')
INPUT_WIDTH = 224

def batch(iterable, bs=1):
    l = len(iterable)
    for ndx in range(0, l, bs):
        yield iterable[ndx:min(ndx + bs, l)]

class MobileNetv2_Embedder(object):
    '''
    MobileNetv2_Embedder loads a Mobilenetv2 pretrained on Imagenet1000, with classification layer removed, exposing the bottleneck layer, outputing a feature of size 1280. 

    Params
    ------
    - model_wts_path (optional, str) : path to mobilenetv2 model weights, defaults to the model file in ./mobilenetv2
    - half (optional, Bool) : boolean flag to use half precision or not, defaults to True
    - max_batch_size (optional, int) : max batch size for embedder, defaults to 16
    - bgr (optional, Bool) : boolean flag indicating if input frames are bgr or not, defaults to True

    '''
    def __init__(self, model_wts_path = None, half=True, max_batch_size = 16, bgr=True):
        if model_wts_path is None:
            model_wts_path = MOBILENETV2_BOTTLENECK_WTS
        assert os.path.exists(model_wts_path),f'Mobilenetv2 model path {model_wts_path} does not exists!'
        self.model = MobileNetV2_bottle(input_size=INPUT_WIDTH, width_mult=1.)
        self.model.load_state_dict(torch.load(model_wts_path))
        self.model.cuda() #loads model to gpu
        self.model.eval() #inference mode, deactivates dropout layers

        self.max_batch_size = max_batch_size
        self.bgr = bgr

        self.half = half
        if self.half:
            self.model.half()
        logger.info('MobileNetV2 Embedder for Deep Sort initialised')
        logger.info(f'- half precision: {self.half}')
        logger.info(f'- max batch size: {self.max_batch_size}')
        logger.info(f'- expects BGR: {self.bgr}')

        zeros = np.zeros((100, 100, 3), dtype=np.uint8)
        self.predict([zeros]) #warmup

    def preprocess(self, np_image):
        '''
        Preprocessing for embedder network: Flips BGR to RGB, resize, convert to torch tensor, normalise with imagenet mean and variance, reshape. Note: input image yet to be loaded to GPU through tensor.cuda()

        Parameters
        ----------
        np_image : ndarray
            (H x W x C)

        Returns
        -------
        Torch Tensor

        '''
        if self.bgr:
            np_image_rgb = np_image[...,::-1]
        else:
            np_image_rgb = np_image

        input_image = cv2.resize(np_image_rgb, (INPUT_WIDTH, INPUT_WIDTH))
        trans = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        input_image = trans(input_image)
        input_image = input_image.view(1,3,INPUT_WIDTH,INPUT_WIDTH)
        
        return input_image

    def predict(self, np_images):
        '''
        batch inference

        Params
        ------
        np_images : list of ndarray
            list of (H x W x C), bgr or rgb according to self.bgr
        
        Returns
        ------
        list of features (np.array with dim = 1280)

        '''
        all_feats = []

        preproc_imgs = [ self.preprocess(img) for img in np_images ]

        for this_batch in batch(preproc_imgs, bs=self.max_batch_size):
            this_batch = torch.cat(this_batch, dim=0)
            this_batch = this_batch.cuda()
            if self.half:
                this_batch = this_batch.half()
            output = self.model.forward(this_batch)
            
            all_feats.extend(output.cpu().data.numpy())

        return all_feats
