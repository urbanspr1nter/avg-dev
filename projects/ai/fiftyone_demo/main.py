import kagglehub
import fiftyone as fo

# Download dice dataset
path = kagglehub.dataset_download("nellbyler/d6-dice")

print("Path to dataset files:", path)

images_path = path + "/d6-dice/Images"
ann_path = path + "/d6-dice/Annotations"

name = "Dice Detection"

# Create the FiftyOne dataset
dataset = fo.Dataset.from_dir(
    dataset_dir=images_path,
    dataset_type=fo.types.ImageDirectory,
    name=name,
)

# View summary info about the dataset
print(dataset)

# Print the first few samples in the dataset
print(dataset.head())


session = fo.launch_app(dataset)


# Loop through for each sample in our dataset
for sample in dataset:
    # Load our annotation file into a list of detections
    sample_root = sample.filepath.split("/")[-1].split(".")[0]
    sample_ann_path = ann_path + "/" + sample_root + ".txt"

    with open(sample_ann_path, 'r') as file:
        list_of_anns = [line.strip().split() for line in file]

    # For each detection, adjust the format and add to our detections list
    detections = []

    for ann in list_of_anns:

        # Make sure to make adjustments to custom formats!
        # Move label up one
        label = str(int(ann[0]) + 1)

        # Adjust bounding box from x_center, y_center, length, width to top_left_x, top_left_y, width, height
        bbox = [float(x) for x in ann[1:]] # x,y,l,w
        bbox_adjusted = [bbox[0]-bbox[3]/2, bbox[1]-bbox[2]/2, bbox[3], bbox[2]] # x,y,w,h

        # Add the object to the sample
        det = fo.Detection(
            label=label, bounding_box=bbox_adjusted
        )

        detections.append(det)

    sample["ground_truth"] = fo.Detections(detections=detections)
    sample.save()


session.show()