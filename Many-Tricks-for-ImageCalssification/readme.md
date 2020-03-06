# 以Fashion-mnist分类任务为例
## 1.解题思路说明
### 1.1待解决的问题
针对`Fashion-MNIST`数据集，设计、搭建、训练机器学习模型，能够尽可能准确地分辨出测试数据地标签。
### 1.2整体思路/方案
本次任务我们使用了开源的深度卷积神经网络resnet34作为我们的baseline backone, 同时通过消融实验，设计了数据增强方法。经过实验调试，我们对比了不同的backbone网络的性能，以及各种超参数对实验结果的影响，最终选择了最优的模型。
具体实现方案如下。
#### 1.2.1选择baseline
考虑到本次任务的原始数据分辨率小(28x28),过深过大的网络可能会导致发生过拟合(overfiting)现象，我们选择了一个参数量较少的深度模型resnet34作为此次的baseline backbone。
#### 1.2.2设计数据增强
经过实验我们发现使用resnet34网络，仍然会发生一定程度的过拟合，数据增强是解决过拟合一个比较好的手段，它的本质是在一定程度上扩充训练数据样本，避免模型拟合到训练集中的噪声，所以设计一个好的数据增强方案尤为必要。在CV任务中，常用的数据增强包括RandomCrop(随机扣取)、Padding(补丁)、RandomHorizontalFlip(随机水平翻转)、ColorJilter(颜色抖动)等。还有一些其他高级的数据增强技巧，比如RandomEreasing(随机擦除)、MixUp、CutMix、AutoAugment，以及最新的AugMix和GridMask等。在此次任务中我们通过实验对比，选择了一个较合适的数据增强方案。
#### 1.2.3对比其他backbone网络
由于resnet34网络提取特征的能力有限，我们在设计了一个合适的数据增强方案后，将backbone换成了其他更强的backbone,例如efficientnet,wideresnet(wrn)等，经过实验发现wrn40-4效果更好。
#### 1.2.4参数调优
针对各种参数的选择，我们利用控制变量法与网格搜索方法，选取最优参数，为了节省训练时间我们选用了收敛更快的Adam优化器
##### (1)学习率(learning rate)的选择
我们分别尝试了3e-2+warmup(初始3e-4)+Cosine衰减、3e-3+warmup(初始3e-5)+Cosine衰减、3e-4+warmup(初始3e-6)+Cosine衰减
##### (2)batch size的选择
考虑到训练时间和机器性能，我们使用128batch size
##### (3)输入图像大小的选择
原则上图像分辨率高对网络识别的效果越好，但是由于机器性能和训练时间限制，我们选择32x32大小的分辨率
##### (4)迭代epoch选择
我们开始设置了一个比较大的epoch，后面观察到网络的收敛的情况，最终选择400个epoch
#### 1.2.5测试增强方法
一个常用提高精度的方法测试时增强（test time augmentation, TTA），可将准确率提高若干个百分点，测试时将原始图像造出多个不同版本，包括不同区域裁剪和更改缩放程度等，并将它们输入到模型中；然后对多个版本进行计算得到平均输出，作为图像的最终输出分数。这种技术很有效，因为原始图像显示的区域可能会缺少一些重要特征，在模型中输入图像的多个版本并取平均值，能解决上述问题。
### 1.3数据处理
#### 1.3.1数据转换
由于原始数据为单通道图片，所以我们有两种选择方案
- 默认1通道图片进行训练
- 将图片转换为3通道图片进行训练

使用默认的单通道图片进行训练无法使用预训练模型，所以比较好的方法是将图片转换为3通道图片进行训练，这样可以用到一些backbone在其他数据集上的预训练模型，这种迁移学习的方法能够加快网络收敛速度并在一定程度上提高性能。
#### 1.3.2数据增强
通过实验对比，选择了一个如下数据增强方案：
- Resize 36x36
- RandomCrop(随机) 32x32
- RandomHorizontalFlip(随机水平翻转)
- RandomEreasing(随机擦除)
- AutoAugment
- CutMix
- Normalation 
### 1.4模型训练
模型训练策略：   
- WarmUp 10 epoch 
- CosineAnnealingLR Scheduler
- Adam 3e-4 + weight_decay 5e-4 / Ranger Optimizer(no warm up) 4e-3
- epoch 400

### 1.5结果分析
| train_size | batch_size | lr | backbone | tricks | test_loss | test_acc |
| :-----| ----: | :----: | :----: | :----: | :----: | :----: |
| 32x32 | 128 | 3e-4 | wrn40_4 | WarmUp + CosineAnnealingLR + RandomCrop + RandomHorizontalFlip + RandomErasing + AutoAugment + CutMix | 0.1739 | 0.9579 |
| 32x32 | 128 | 3e-4 | wrn40_4 | WarmUp + CosineAnnealingLR + RandomCrop + RandomHorizontalFlip + RandomErasing + AutoAugment + CutMix + TTA | 0.1739 | 0.9607 |
| 32x32 | 128 | 4e-3 | wrn40_4(Mish) | Ranger + CosineAnnealingLR + RandomCrop + RandomHorizontalFlip + RandomErasing + AutoAugment + CutMix | 0.1490 | 0.9601 |
| 32x32 | 128 | 4e-3 | wrn40_4(Mish) | Ranger + CosineAnnealingLR + RandomCrop + RandomHorizontalFlip + RandomErasing + AutoAugment + CutMix + TTA | 0.1490 | 0.9621 |     

ps: 参数调一调应该能更高，由于时间和机器限制，大部分参数没仔细调，而且不加TTA最好的是结果是0.9609，但是模型没保存下来，懒得再训了，就用了0.9601，有条件的可以试试增加分辨率，应该会提高一些
## 2.数据和模型的使用
### 2.1数据说明
Fashion-MNIST的目的是要成为MNIST数据集的一个直接替代品。作为算法作者，你不需要修改任何的代码，就可以直接使用这个数据集。Fashion-MNIST的图片大小，训练、测试样本数及类别数与经典MNIST完全相同。
#### 类别标注
在Fashion-mnist数据集中，每个训练样本都按照以下类别进行了标注：
| 标注编号 | 描述 |
| --- | --- |
| 0 | T-shirt/top（T恤）|
| 1 | Trouser（裤子）|
| 2 | Pullover（套衫）|
| 3 | Dress（裙子）|
| 4 | Coat（外套）|
| 5 | Sandal（凉鞋）|
| 6 | Shirt（汗衫）|
| 7 | Sneaker（运动鞋）|
| 8 | Bag（包）|
| 9 | Ankle boot（踝靴）|
#### 数据集大小
| 数据集 | 样本数量 |
| --- | --- |
| 训练集 | 60000|
| 测试集 | 10000|
### 2.2 预训练模型的使用
- resnet34使用image-net上的预训练模型
- efficientnet使用image-net上的预训练模型
- wrn40-4不使用预训练模型
## 3.项目运行环境
该框架支持cpu,单gpu,多gpu/syncbn,支持日志系统，集成了多种实用的tricks方便易用,计划不久开源。项目运行在python3.6, pytorch>0.4。
### 3.1项目所需的工具包/框架
具体依赖如下
- python==3.6
- albumentations==0.4.3
- imageio==2.6.1
- imgaug==0.2.6
- pandas==0.25.1
- hickle==3.4.5
- tqdm==4.36.1
- opencv_python==4.1.1.26
- scikit_image==0.15.0
- mlconfig==0.0.4
- visdom==0.1.8.9
- torch==1.0.0
- torchvision==0.2.0
- yacs==0.1.6
- numpy==1.17.4
- scipy==1.3.1
- Pillow==6.2.1
- skimage==0.0
### 3.2项目运行的资源环境
11G gtx-2080

## 4.项目运行方法

### 4.1项目的文件结构
详情见github文件列表

### 4.2项目运行步骤
请正确安装配置深度学习GPU服务器，建议使用env或者docker确保环境统一。

#### 4.2.1使用编辑器运行
为了方便调试，可以直接使用编辑器运行，步骤如下：
##### (1) 修改config.py中的配置，主要包括硬件环境(cpu/gpu)、输入大小、数据集路径、backbone、优化器、学习率、迭代次数、batchsize、结果日志及模型保存路径等等
```python
_C.MODEL = CN()
_C.MODEL.NAME = "baseline"  # 模型
_C.MODEL.N_CHANNEL = 3  # 输入通道数
_C.MODEL.N_CLASS = 10  # 类别数
_C.MODEL.DEVICE = 'cuda'  # 硬件环境 'cpu' or 'cuda'
_C.MODEL.DEVICE_IDS = '0d' # 指定gpu '0d' for single gpu, '0,1d' for multi gpu
_C.MODEL.BACKBONE = 'wrn40_4' # backone 
_C.MODEL.DROPOUT = 0 # dropout rate
_C.MODEL.USE_NONLOCAL = False # use nonlocal block
_C.MODEL.USE_SCSE = False # use scse block
_C.MODEL.USE_ATTENTION = False # use attention block



_C.DATALOADER = CN()
_C.DATALOADER.NUM_WORKERS = 2


_C.DATASETS = CN()
_C.DATASETS.NAMES = ('minist')# Root PATH to the dataset
_C.DATASETS.DATA_PATH = r'/usr/demo/common_data' # dataset root

_C.DATASETS.TRAIN = CN()
_C.DATASETS.TRAIN.IMAGE_FOLDER = r'train_rs_imgs' # ignore for fanish minist



_C.DATASETS.VAL = CN()
_C.DATASETS.VAL.IMAGE_FOLDER = r'val_rs_imgs' # ignore for fanish minist


_C.INPUT = CN()

_C.INPUT.PIXEL_MEAN = [0.28604059698879547, 0.28604059698879547, 0.28604059698879547] # 归一化均值
_C.INPUT.PIXEL_STD = [0.3202489254311618, 0.3202489254311618, 0.3202489254311618] # 归一化方差

_C.INPUT.RESIZE_TRAIN = (36, 36) # 训练resize 大小
_C.INPUT.SIZE_TRAIN = (32, 32) # 训练crop 大小
_C.INPUT.RESIZE_TEST = (36, 36) # 测试resize 大小
_C.INPUT.SIZE_TEST = (32, 32) # 测试crop大小
_C.INPUT.PROB = 0.5 # random horizontal flip prob



# random erasing
_C.INPUT.RANDOM_ERASE = CN()
_C.INPUT.RANDOM_ERASE.RE_PROB = 0.5 # random erasing prob
_C.INPUT.RANDOM_ERASE.RE_MAX_RATIO = 0.4 # random erasing max_ratio

_C.INPUT.USE_MIX_UP = False # use mixup
_C.INPUT.USE_CUT_MIX = True # use cutmix
_C.INPUT.USE_AUGMIX = False # use augmix
_C.INPUT.USE_AUTOAUG = True # use autoaugment
_C.INPUT.USE_RICAP = False # use ricap

_C.SOLVER = CN()

_C.SOLVER.OPTIMIZER_NAME = "Ranger" # optimizer 'Adam','SGD','Rnager'


_C.SOLVER.MAX_EPOCHS = 320 # max epochs

_C.SOLVER.BASE_LR = 4e-3 # base lr
_C.SOLVER.BIAS_LR_FACTOR = 1 

_C.SOLVER.USE_WARMUP = False # use warm up
_C.SOLVER.MIN_LR = 4e-5 # cosin CosineAnnealing min lr

_C.SOLVER.MOMENTUM = 0.9 # momentum


_C.SOLVER.WEIGHT_DECAY = 0.0005 # weight decay
_C.SOLVER.WEIGHT_DECAY_BIAS = 0.0005 # weight decay bias

_C.SOLVER.GAMMA = 0.1
_C.SOLVER.STEPS = [40, 70]

_C.SOLVER.WARMUP_FACTOR = 0.01
_C.SOLVER.WARMUP_EPOCH = 10
_C.SOLVER.WARMUP_BEGAIN_LR = 3e-6
_C.SOLVER.WARMUP_METHOD = "linear"

_C.SOLVER.CHECKPOINT_PERIOD = 1 # checkpoint频率
_C.SOLVER.LOG_PERIOD = 100 # 日志打印batch频率
_C.SOLVER.EVAL_PERIOD = 1 # 模型验证频率
_C.SOLVER.START_SAVE_EPOCH = 250 # 模型开始保存的轮数

_C.SOLVER.TENSORBOARD = CN()
_C.SOLVER.TENSORBOARD.USE = True # 使用tensorboard
_C.SOLVER.TENSORBOARD.LOG_PERIOD = 20 # tensorboard记录频率

_C.SOLVER.PER_BATCH = 128 # batch size
_C.SOLVER.SYNCBN = False # for multi gpu syncbn
_C.SOLVER.RESUME = False # 模型续训
_C.SOLVER.RESUME_CHECKPOINT = '' # 模型续训checkpoint

_C.OUTPUT_DIR = CN()
_C.OUTPUT_DIR = r'/usr/demo/common_data/minist_outputs' # 保存路径
```
##### (2)运行train.py
#### 4.2.2使用shell脚本运行
##### (1)修改configs/baseline_train.yml，设置参数与config.py中类似
##### (2)在shells/baseline_train.sh脚本中动态设置参数
```bash
#!/usr/bin/env bash

 DATA_DIR='/usr/demo/common_data' # 数据集root path
 SAVE_DIR='/usr/demo/common_data/minist_outputs/ exp-baseline-wrn40_4-warmup10-epo400-32x32-use_nonlocal' # 保存路径
 python train.py --config_file='configs/baseline_train.yml' \
     SOLVER.BASE_LR '3e-4' SOLVER.WARMUP_EPOCH "10" SOLVER.MAX_EPOCHS "400" SOLVER.START_SAVE_EPOCH "300" SOLVER.EVAL_PERIOD "1" \
     SOLVER.PER_BATCH "128" \
     INPUT.SIZE_TRAIN "([32,32])" INPUT.SIZE_TEST "([32,32])" INPUT.RESIZE_TRAIN "([36,36])" INPUT.RESIZE_TEST "([36,36])" INPUT.USE_AUTOAUG "True" INPUT.USE_CUT_MIX "True" \
     MODEL.NAME "baseline" MODEL.BACKBONE "wrn40_4" MODEL.USE_NONLOCAL "True"\
     DATASETS.DATA_PATH "('${DATA_DIR}')" \
     OUTPUT_DIR "('${SAVE_DIR}')"
```
##### (3)运行./shells/baseline.sh   
ps: 注意先修改shell脚本权限   
#### 测试过程
##### (1)修改inference.py中的模型文件
```python
para_dict = torch.load(r'/usr/demo/common_data/baseline_epoch363.pth')
```
##### (2)运行 inference.py

