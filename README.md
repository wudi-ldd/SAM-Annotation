# SAM_Annotation

# Tight Sandstone Image Annotation with SegmenAnything (SAM)

Welcome to our repository that focuses on efficient and precise annotation and segmentation of tight sandstone images. This codebase is dedicated to the data annotation tool designed using PyQt5. For the UNet image segmentation part and the fine-tuning of the SAM model, please refer to our other repositories.

[FineTuneSAM-with-Bounding-Box](https://github.com/wudi-ldd/FineTuneSAM-with-Bounding-Box).

[U-Net_for_Tight_Sandstone_Image_Segmentation](https://github.com/wudi-ldd/U-Net_for_Tight_Sandstone_Image_Segmentation).

## Key Features

- **Point Annotation**: Utilize minimal points to define complex structures in tight sandstone images.
- **Data Masking**: Accurately generate masks that are crucial for further analysis or machine learning applications.
- **Efficiency**: Expedite the annotation process without compromising on precision.
- **Customizable**: Flexible tool design to suit various annotation needs.

## Visualization of SAM Annotation

   ![Annotation GIF](Demonstration/1.gif)  

## Model Usage Instructions

**Step 1**: Download the pre-trained weights of the SAM model and place them in the `checkpoints` folder. [Download Link](https://github.com/facebookresearch/segment-anything)

**Step 2**: Modify the following lines in `utils\file_functions.py` according to the chosen weight type:
```python
   sam_checkpoint = "checkpoints\sam_vit_h_4b8939.pth"
   model_type = "vit_h"
```

For detailed instructions, refer to the [SAM Official Website](https://github.com/facebookresearch/segment-anything).

**Step 3**: For fine-tuning the SAM model, you can refer to my other article: [Link to Article](https://github.com/wudi-ldd/FineTuneSAM-with-Bounding-Box)

## Shortcuts

- **Left Mouse Click**: Click on areas of interest.
- **Right Mouse Click**: Click on areas not of interest to complete the data annotation without manually drawing mask boxes.
- **Z**: Undo to the previous mouse click state.
- **E**: Finish annotation and save the current mask state.

## Installation
"Download and run directly"
```python
python main.py
```

## Contributing

We welcome contributions to this project. If you have suggestions, bug reports, or want to contribute, please feel free to open an issue or submit a pull request.




