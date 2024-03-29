import cv2
import numpy as np
import os
import sys
import datetime
from samples import coco
from mrcnn import utils
import matplotlib.pyplot as plt
from mrcnn import model as modellib

ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)


class InferenceConfig(coco.CocoConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1


config = InferenceConfig()
config.display()
white_color = (255, 255, 255)

model = modellib.MaskRCNN(
    mode="inference", model_dir=MODEL_DIR, config=config
)
model.load_weights(COCO_MODEL_PATH, by_name=True)
class_names = [
    'BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
    'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
    'cat', 'dog', 'holrse', 'sheep', 'cow', 'elephant', 'bear',
    'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
    'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard',
    'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
    'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
    'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
    'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
    'teddy bear', 'hair drier', 'toothbrush'
]


def random_colors(N):
    np.random.seed(1)
    colors = [tuple(255 * np.random.rand(3)) for _ in range(N)]
    return colors


colors = random_colors(len(class_names))
class_dict = {
    name: color for name, color in zip(class_names, colors)
}


def apply_mask(image, mask, color, alpha=1):
    """apply mask to image"""
    for n, c in enumerate(color):
        image[:, :, n] = np.where(
            mask == 1,
            image[:, :, n] * (1 - alpha) + alpha * c,
            image[:, :, n]
        )
    return image


################################################## DYmodify

def get_matrix_mask(image_mask, mask, label):
    """Apply the given mask to the image matrix.
    """
    # set in the matrix the value of the object label
    positions_mask = np.where(mask == 1)
    for i, j in zip(positions_mask[0], positions_mask[1]):
        image_mask[i][j] = label
    return image_mask


def blur_image(image, masked_image):
    blurred_image = image.astype(np.uint8).copy()
    blurred_image = cv2.blur(blurred_image, (10, 10))
    positions_background = np.where(masked_image == 0)

    for i, j in zip(positions_background[0], positions_background[1]):
        blurred_image[i][j] = image[i][j]

    return blurred_image


def display_blurred(image, boxes, masks, ids, names, scores):
    """
    boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
    masks: [height, width, num_instances]
    class_ids: [num_instances]
    class_names: list of class names of the dataset
    figsize: (optional) the size of the image.
    """
    # if not ax:
    #    fig, ax = plt.subplots(1, figsize=figsize)

    # height, width = image.shape[:2]
    # ax.axis('off')
    # Number of instances
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
    else:
        assert boxes.shape[0] == masks.shape[-1] == ids.shape[0]
    # masked_image = image.astype(np.uint32).copy()
    masked_image = np.zeros(shape=image.shape)
    for i in range(N):
        if not np.any(boxes[i]):
            continue

        y1, x1, y2, x2 = boxes[i]

        # Label
        # class_id = ids[i]
        # label = class_names[class_id]

        if ids[i] == 1:
            label = names[ids[i]]
            color = class_dict[label]
            score = scores[i] if scores is not None else None
            caption = '{} {:.2f}'.format(label, score) if score else label
            # Mask
            mask = masks[:, :, i]
            masked_image = get_matrix_mask(masked_image, mask, ids[i] + 1)
        # masked_image = get_matrix_mask(image, mask, class_id+1)

        # image = apply_mask(image, mask, white_color)

    # blurred_image = blur_image(image, masked_image)
    blurred_image = blur_image(image, masked_image)

    return blurred_image
    # plt.imsave(name, blurred_image.astype(np.uint8))


################################################################

def display_instances(image, boxes, masks, ids, names, scores):
    """
        take the image and results and apply the mask, box, and Label
    """
    n_instances = boxes.shape[0]

    if not n_instances:
        print('NO INSTANCES TO DISPLAY')
    else:
        assert boxes.shape[0] == masks.shape[-1] == ids.shape[0]

    for i in range(n_instances):
        if not np.any(boxes[i]):
            continue

        y1, x1, y2, x2 = boxes[i]
        # label = names[ids[i]]
        # color = class_dict[label]
        # score = scores[i] if scores is not None else None
        # caption = '{} {:.2f}'.format(label, score) if score else label
        # mask = masks[:, :, i]
        #
        # image = apply_mask(image, mask, color)
        # image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        # image = cv2.putText(
        #     image, caption, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2
        # )

        if ids[i] == 1:
            label = names[ids[i]]
            color = class_dict[label]
            score = scores[i] if scores is not None else None
            caption = '{} {:.2f}'.format(label, score) if score else label
            mask = masks[:, :, i]
            image = apply_mask(image, mask, white_color)
        #  image = cv2.rectangle(image, (x1, y1), (x2, y2), white_color, 2)
        #  image = cv2.putText(image, caption, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.7, white_color, 2)

    return image


if __name__ == '__main__':
    """
        test everything
    """

    # input_video = sys.argv[1]
    capture = cv2.VideoCapture(0)

    # these 2 lines can be removed if you dont have a 1080p camera.
    # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Recording Video
    fps = 25.0
    width = int(capture.get(3))
    height = int(capture.get(4))
    fcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
    out = cv2.VideoWriter(datetime.datetime.now().strftime("%d_%H-%M-%S.avi"), fcc, fps, (width, height))

    while True:
        ret, frame = capture.read()
        results = model.detect([frame], verbose=0)
        r = results[0]
        frame = display_blurred(
            frame, r['rois'], r['masks'], r['class_ids'], class_names, r['scores']
        )
        cv2.imshow('frame', frame)

        # Recording Video
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()