import conf.conf as conf

from core.image.image_operator import *
from core.image.pixel_analyzer import *
from core.io.load_handler import *
from core.io.save_handler import *
from multiprocessing import Pool, cpu_count

def get_shape(x, partition, k):
    # partition is sorted based on min_j
    obj = partition[k]
    [min_i, min_j], [max_i, max_j] = obj
    py = (max_i - min_i) + 1
    px = (max_j - min_j) + 1

    if (py < conf.MINIMUM_OBJECT_DIMENSION) or (px < conf.MINIMUM_OBJECT_DIMENSION):
        return []

    shape = np.zeros((py, px))

    start_i = min_i
    start_j = min_j

    # find other images from partition that exist in current frames
    # find images with  frames_min_j < min_j < frames_max_j
    # therefore only need to check next images
    for i in range(py):
        for j in range(px):
            shape[i][j] = x[start_i + i][start_j + j]

    # remove any overlap object in current frames
    lo = k - 1
    while (lo >= 0 and partition[lo][1][1] > min_j):
        ImageOperator.remove_overlap(shape, obj, partition[lo])
        lo -= 1

    hi = k + 1
    while (hi < len(partition) and partition[hi][0][1] < max_j):
        ImageOperator.remove_overlap(shape, obj, partition[hi])
        hi += 1

    # clean images from any noise and enhance all image features
    # shape = clean_image(shape)

    # center the image then scale to appropriate dimension
    shape = ImageOperator.center_image(shape)
    shape = ImageOperator.scale_image(shape)
    
    # preprocess image pixel intensity and enhance loop portion of images
    shape_ = ImageOperator.to_serial(shape, 28, 28)
    ImageOperator.loop_enhance(shape_, 28, 28)

    return ImageOperator.to_matrix(shape_, 28, 28)
  
def get_shape_wrapper(data):
    img, partition, j, idx = data
    shape = get_shape(img, partition, j)

    if len(shape) == 0:
        return []

    if conf.DEBUG_MODE:
        SaveHandler.save_image(shape, "shape{}.png".format(idx))

    return shape
  
def detection(model, mat, s):
    # Detection Process
    data = []
    idx = 0
    for i in range(len(s)):
        partition = s[i]
        for j in range(len(partition)):
            data.append([mat, partition, j, idx])
            idx += 1

    # Process frames to images in parallel
    with Pool(cpu_count()) as pool:
        numbers = pool.map(get_shape_wrapper, data)

    # filter images that has dimension lower than minimum dimension
    numbers = [num for num in numbers if len(num) > 0]
    numbers = np.array(numbers)

    # do prediction
    total_shapes = len(numbers)

    prediction_ = model.predict(numbers.reshape(total_shapes, 28, 28, 1))
    prediction = list(map(lambda x: np.argmax(x), prediction_))

    return prediction

def preprocess(filename):
    # load image
    img = LoadHandler.load_image(filename)
    
    # convert image to grayscale
    img = ImageOperator.to_grayscale(img)

    # removce shadow
    img = ImageOperator.shadow_remove(img)
    
    # remove noise
    img = ImageOperator.remove_noise(img)
    
    # serialize array
    ny, nx = np.shape(img)
    pixels = ImageOperator.to_serial(img, nx, ny)

    # Find thresh and thresh images
    thresh = PixelAnalyzer.findThreshold(pixels)
    ImageOperator.thresh_images(pixels, nx, ny, thresh)
    pixels = ImageOperator.close_image(pixels, nx, ny)

    # Image Detection
    # Find frames
    objs = ImageOperator.object_detect(pixels, nx, ny)

    # Change serialize pixels to matrix
    mat = ImageOperator.to_matrix(pixels, nx, ny)
    
    return objs, mat


def routine_single_file(result):
    objs, mat = preprocess(conf.FILENAME)
    model = LoadHandler.load_model()
    
    if conf.DEBUG_MODE:
          conf.DEBUG_OUT_PATH = conf.DEBUG_OUT_PATH_SHAPE.format(conf.FILENAME)
          PathHandler.check_path(conf.DEBUG_OUT_PATH, not_exist_create=True)
          
    result[0] = detection(model, mat, objs)

def routine_batch_files(result):
    # load image in batch
    # get image list
    img_list = PathHandler.list_image()
  
    if conf.BATCH_SIZE == -1:
        with Pool(cpu_count()) as pool:
            objs_batch = pool.map(preprocess, img_list)
            
    elif conf.BATCH_SIZE == 1:
        objs_batch = []
        for img_name in img_list:
            objs_batch.append(preprocess(img_name))
    
    else:
        N = len(img_list) // conf.BATCH_SIZE
        start = 0
        end = conf.BATCH_SIZE
        objs_batch = [None for i in range(len(img_list))]
        for i in range(N):
            end = min(len(img_list), end) # deal with edge condition
    
            with Pool(cpu_count()) as pool:
                objs_batch_ = pool.map(preprocess, img_list[start: end])
                for j in range(start, start + conf.BATCH_SIZE):
                    objs_batch[j] = objs_batch_[j - start]
            
            # increment start and end
            start += conf.BATCH_SIZE
            end += conf.BATCH_SIZE

    results = []
    model = LoadHandler.load_model()
    for (file, (objs, mat)) in zip(img_list, objs_batch):
      conf.FILENAME = file

      if conf.DEBUG_MODE:
          conf.DEBUG_OUT_PATH = conf.DEBUG_OUT_PATH_SHAPE.format(conf.FILENAME)
          PathHandler.check_path(conf.DEBUG_OUT_PATH, not_exist_create=True)

      _ = detection(model, mat, objs)
      results.append([file, _])

    result[0] = results
    
  
