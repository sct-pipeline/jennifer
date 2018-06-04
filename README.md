# jennifer
Pipeline to standardize intensity ranges between a set of images.

Images have different intensity ranges that make it difficult to compare/process.
This script aims at transforming a set of images intensity ranges to a common standard intensity space using a multi-segment linear transformation model.
Once learned, this model can be applied to unseen images to map them to the same standard intensity space.

It is inspired from the paper:
```
Nyul, L.G.; Udupa, J.K.; Xuan Zhang, “New variants of a method of MRI scale standardization,” Medical Imaging, IEEE Transactions on , vol.19, no.2, pp.143-150, Feb. 2000
```

## Dependencies
[SCT v3.1.2](https://github.com/neuropoly/spinalcordtoolbox/releases/tag/v3.1.2) or above.

## File structure
```
input_folder
  |- 001.nii.gz
  |- 002.nii.gz
  |- 003.nii.gz
  |- ...
```

## How to run

- Download (or `git clone`) this repository.
- Run
~~~
python run_standardization.py -i_folder <> -sliceWise <> -trained_model <> -o_folder <>
~~~
with:

`-i_folder`: indicates the input folder with data organized as described above in section `File Structure` [Mandatory]

`-sliceWise`: 1: slice-wise standardization; 0: volume-wise standardization. If you want to perform a slice-wise standardization, please make sure that the last dimension of your input images is the one you want to go through (e.g. Superior-to-Inferior if you want to standardize the axial slices).

`-trained_model`: If a trained model is provided (pickle file), it will be used to perform the standardization without re-training a model.

`-o_folder`: output folder where the output images will be saved. If this parameter is not specified, a folder `standardized_data` will be created inside the `i_folder`

## Contributors

Charley Gros

## License

The MIT License (MIT)

Copyright (c) 2018 École Polytechnique, Université de Montréal

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
