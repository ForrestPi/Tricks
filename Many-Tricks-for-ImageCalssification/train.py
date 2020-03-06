# -*- encoding: utf-8 -*-
'''
@File    :   train.py    
@Contact :   whut.hexin@foxmail.com
@License :   (C)Copyright 2017-2018, HeXin

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2020/2/21 10:18   xin      1.0         None
'''

import os
import torch
import argparse

from config import cfg
from utils import setup_logger
from dataset import make_dataloader
from model import build_model
from loss import make_loss
from trainer import BaseTrainer


def main():
    parser = argparse.ArgumentParser(description="Baseline Training")
    parser.add_argument("--config_file", default="", help="path to config file", type=str)
    parser.add_argument("opts", help="Modify config options using the command-line", default=None,
                        nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()

    output_dir = cfg.OUTPUT_DIR
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    num_gpus = 0
    device = torch.device("cpu")
    if cfg.MODEL.DEVICE == 'cuda' and torch.cuda.is_available():
        num_gpus = len(cfg.MODEL.DEVICE_IDS)-1
        device_ids = cfg.MODEL.DEVICE_IDS.strip("d")
        print(device_ids)
        device = torch.device("cuda:{0}".format(device_ids))

    logger = setup_logger('baseline', output_dir, 0)
    logger.info('Using {} GPUS'.format(num_gpus))
    logger.info('Running with config:\n{}'.format(cfg))


    train_dl, val_dl = make_dataloader(cfg, num_gpus)

    model = build_model(cfg)

    loss = make_loss(cfg, device)

    trainer = BaseTrainer(cfg, model, train_dl, val_dl,
                                  loss, num_gpus, device)

    logger.info(type(model))
    logger.info(loss)
    logger.info(trainer)
    for epoch in range(trainer.epochs):
        for batch in trainer.train_dl:
            trainer.step(batch)
            trainer.handle_new_batch()
        trainer.handle_new_epoch()


if __name__ == "__main__":
    main()

