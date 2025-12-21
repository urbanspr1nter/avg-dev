from fastai.vision.all import *
import ipywidgets.widgets as widgets

path = '/home/avgdev/datasets/pokemon-classification/data'

pokemon_block = DataBlock(
    blocks=(ImageBlock, CategoryBlock),
    get_items=get_image_files,
    get_y=parent_label,
    splitter=GrandparentSplitter(train_name='train', valid_name='valid'),
    item_tfms=Resize(224),
    batch_tfms=aug_transforms(mult=2)
)
dls = pokemon_block.dataloaders(path, bs=16)

learn = vision_learner(dls, resnet34, metrics=error_rate)
learn.fine_tune(5) # learn_rate: 1e-2

learn.export()