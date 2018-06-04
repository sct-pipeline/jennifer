"""Intensity standardization.

Implementing paper: Nyul et al. 2000
Validated in: Shah et al. 2011 on MRIs of human brain with multiple sclerosis

Created: September 2017
Last Modification: 2017-09-15
Contributors: charley
"""

import pandas as pd
import numpy as np
from msct_image import Image
from scipy.interpolate.interpolate import interp1d


def train_intensity_standardization_model(img_path_lst, i_min, i_max, per_slice=0):
    """Learn the intensity landmarks based on a set of several training images.

    Input:
            - img_path_lst: list containing the filenames of the training images
            - i_min and i_max: determine the intensity range to map the output images
            - per_slice: 1: slice-wise standardization, 0: volume-wise standardization

    Output: the learned landmarks for the minimum and maximum intensities (i_min, i_max)
            and each of the histogram deciles.
    """
    if per_slice == 1:
        print('\nYou are running a standardization per slice. Please make sure that the third dimension of your data is along the Superior to Inferior axis\n')
        objects_lst = []
        for i in range(len(img_path_lst)):
            img = Image(img_path_lst[i])
            for ii in range(img.dim[2]):
                objects_lst.append(img.data[:, :, ii])
    else:
        objects_lst = [Image(ii).data for ii in img_path_lst]

    landmarks_dct = {'img_idx': [str(i) for i in range(len(objects_lst))]}
    landmarks_pd = pd.DataFrame.from_dict(landmarks_dct)

    percent_decile_lst = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]

    for idx, img_data in zip(range(len(objects_lst)), objects_lst):
        vals = list(img_data)

        landmarks_lst_cur = np.percentile(vals, q=percent_decile_lst)
        interpolation_fct = interp1d([landmarks_lst_cur[0], landmarks_lst_cur[-1]], [i_min, i_max])
        landmarks_lst_cur_scale = interpolation_fct(landmarks_lst_cur)

        idx_pd = landmarks_pd[landmarks_pd.img_idx == str(idx)].index
        for i_p_d, p_d in enumerate(percent_decile_lst):
            landmarks_pd.loc[idx_pd, 'l_' + str(p_d)] = landmarks_lst_cur_scale[i_p_d]

    return landmarks_pd.mean(axis=0, numeric_only=True)


def intensity_standardization(img_data, landmarks_pd, max_interp):
    vals = list(img_data)
    percent_decile_lst = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
    landmarks_lst_cur = np.percentile(vals, q=percent_decile_lst)

    # treat single intensity accumulation error
    if not len(np.unique(landmarks_lst_cur)) == len(landmarks_lst_cur):
        raise SingleIntensityAccumulationError('The image shows an unusual single-intensity accumulation that leads to a situation where two percentile values are equal. This situation is usually caused, when the background has not been removed from the image. The only other possibility would be to re-train the model with a reduced number of landmark percentiles landmarkp or a changed distribution.')

    # create linear mapping models for the percentile segments to the learned standard intensity space  
    linear_mapping = interp1d(landmarks_lst_cur, landmarks_pd.values, bounds_error = False)

    # transform the input image intensity values
    output = linear_mapping(img_data)

    # treat image intensity values outside of the cut-off percentiles range separately
    # below_mapping = linear_model(landmarks_lst_cur[:2], landmarks_pd.values[:2])
    below_mapping = exp_model(landmarks_lst_cur[:2], landmarks_pd.values[:2], landmarks_pd.values[0])
    output[img_data < landmarks_lst_cur[0]] = below_mapping(img_data[img_data < landmarks_lst_cur[0]])

    if max_interp == 'exp':
        above_mapping = exp_model(landmarks_lst_cur[-3:-1], landmarks_pd.values[-3:-1], landmarks_pd.values[-1])
    elif max_interp == 'linear':
        above_mapping = linear_model(landmarks_lst_cur[-2:], landmarks_pd.values[-2:])
    elif max_interp == 'flat':
        above_mapping = lambda x: landmarks_pd.values[-1]
    else:
        print 'No model was chosen, will use flat'
        above_mapping = lambda x: landmarks_pd.values[-1]
    output[img_data > landmarks_lst_cur[-1]] = above_mapping(img_data[img_data > landmarks_lst_cur[-1]])

    return output


def apply_intensity_standardization_model(img_path, landmarks_pd, fname_out, max_interp='exp', per_slice=0):
    """Description: apply the learned intensity landmarks to the input image."""
    img = Image(img_path)
    img_data = np.asarray(img.data)

    if per_slice:
        output = np.zeros(img_data.shape)
        for zz in range(img_data.shape[2]):
            output[:, :, zz] = intensity_standardization(img_data[:, :, zz], landmarks_pd, max_interp)
    else:
        output = intensity_standardization(img_data, landmarks_pd, max_interp)

    # save resulting image
    img_normalized = img.copy()
    img_normalized.data = output
    img_normalized.setFileName(fname_out)
    img_normalized.save()


def linear_model((x1, x2), (y1, y2)):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - (m * x1)
    return lambda x: m * x + b


def exp_model((x1, x2), (y1, y2), s2):
    m = (y2 - y1) / (x2 - x1)
    b = y1 - (m * x1)
    mu90 = x2

    # y2 = alpha + beta * exp(gamma * x)
    alpha = s2

    omega = m * mu90 - s2 + b
    beta = omega * np.exp(-m * mu90 * 1.0 / omega)

    gamma = m * 1.0 / omega

    return lambda x: alpha + beta * np.exp(gamma * x)


class SingleIntensityAccumulationError(Exception):
    """
    Thrown when an image shows an unusual single-intensity peaks which would obstruct
    both, training and transformation.
    """
