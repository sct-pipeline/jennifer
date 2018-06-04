"""Intensity standardization.

Pipeline to standardize intensity ranges between a set of images.

Images have different intensity ranges that make it difficult to compare/process.
This script aims at transforming a set of images intensity ranges to a common standard intensity space using a multi-segment linear transformation model.
Once learned, this model can be applied to unseen images to map them to the same standard intensity space.

Created: May 2018
Contributors: charley
"""

import os
import pandas as pd
from intensity_standardization import train_intensity_standardization_model, apply_intensity_standardization_model


def run_standardization(path_process, path_output, param, i_fname_lst, per_slice):
    for i_fname in i_fname_lst:
        o_fname = path_output + i_fname.split('/')[-1]
        if os.path.isfile(i_fname):
            if os.path.isfile(o_fname):
                print('\tOutput file overwritten: ' + o_fname)
            apply_intensity_standardization_model(img_path=i_fname,
                                                landmarks_pd=param,
                                                fname_out=o_fname,
                                                max_interp='exp',
                                                per_slice=per_slice)


def run_main(path_process, path_model, path_output, sliceWise):
    """Main function."""
    img_path_lst = [path_process + img for img in os.listdir(path_process) if img.endswith('.nii') or img.endswith('.nii.gz')]

    if len(img_path_lst):
        if path_model:
            print('\nLoad trained model')
            intensity_norm_model = pd.read_pickle(path_model)
        else:
            print('\nTrain new model')
            intensity_norm_model = train_intensity_standardization_model(img_path_lst=img_path_lst,
                                                                                    i_min=0, i_max=1000,
                                                                                    per_slice=sliceWise)
            intensity_norm_model.to_pickle(path_output + 'intensity_standardization_model.pickle')

        print('\nApply standardization')
        run_standardization(path_process=path_process,
                            path_output=path_output,
                            param=intensity_norm_model,
                            i_fname_lst=img_path_lst,
                            per_slice=sliceWise)
    else:
        print('\nNo image found.')

    print('\n --- END ---')


if __name__ == "__main__":

    from argparse import ArgumentParser

    parser = ArgumentParser()

    # Add more options if you like
    parser.add_argument("-i_folder", "--input_folder", dest="i_fold",
                        help="Input folder containing the images")
    parser.add_argument("-sliceWise", "--sliceWise", dest="sliceWise", type=int,
                        default=0, help="1: standardization per slice; 0: standardization per volume. If you want to perform a slice-wise standardization, please make sure that the last dimension of your input images is the one you want to go through (e.g. Superior-to-Inferior if you want to standardize the axial slices).")
    parser.add_argument("-trained_model", "--trained_model", dest="trained_model",
                        default=None, help="If a trained model is provided (pickle file), it will be used to perform the standardization without re-training a model.")
    parser.add_argument("-o_folder", "--output_folder", dest="o_fold",
                        default=None, help="Output folder where the output images will be saved. If this parameter is not specified, a folder `standardized_data` will be created inside the input_folder")

    args = parser.parse_args()

    path_data = args.i_fold
    path_data = path_data if path_data[-1] == '/' else path_data + '/'

    path_trained_model = args.trained_model
    path_trained_model = path_trained_model if (path_trained_model and os.path.isfile(args.trained_model)) else None

    if args.o_fold and os.path.isdir(args.o_fold):
        path_output = args.o_fold
        path_output = path_output if path_output[-1] == '/' else path_output + '/'
    else:
        path_output = path_data + 'standardized_data/'
        if not os.path.isdir(path_output):
            os.makedirs(path_output)

    print '\nParse arguments:'
    print '\tInput folder: ' + path_data
    print '\tPath to trained model: ' + str(path_trained_model)
    if bool(args.sliceWise):
        print '\tStandardization: slice-wise'
    else:
        print '\tStandardization: volume-wise'
    print '\tOutput folder: ' + path_output


    run_main(path_process=path_data,
            path_model=path_trained_model,
            path_output=path_output,
            sliceWise=bool(args.sliceWise))
