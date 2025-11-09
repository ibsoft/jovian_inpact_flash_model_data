import argparse
import json
import glob
import os
import random
from datetime import datetime
import shutil

# Change to match your labels and give a unique number starting at 0
LABELS = {'Impact': 0, 'Satellite': 1, 'Shadow': 2}

def convert2yolo(annotarray, origwidth, origheight):
    boxheight = float(annotarray[0])
    boxwidth = float(annotarray[1])
    boxleft = float(annotarray[2])
    boxtop = float(annotarray[3])

    # Calculate x center and y center, then scale 0-1
    x_center = (boxleft + (0.5 * boxwidth)) / origwidth
    y_center = (boxtop + (0.5 * boxheight)) / origheight

    # Scale box width, height to 0-1
    boxwidth, boxheight = boxwidth / origwidth, boxheight / origheight

    return [x_center, y_center, boxwidth, boxheight]

def getannot(annotdict):
    filename = annotdict['asset']['name']
    origwidth = annotdict['asset']['size']['width']
    origheight = annotdict['asset']['size']['height']

    regions = annotdict['regions']
    regions2 = []
    for r in regions:
        label = LABELS[r['tags'][0]]  # Should only be one
        bbox = r['boundingBox']
        h = bbox['height']
        w = bbox['width']
        left = bbox['left']
        top = bbox['top']  # distance from top
        yoloarray = [label]
        yoloarray.extend(convert2yolo([h, w, left, top], origwidth, origheight))
        regions2.append(yoloarray)
    return regions2, filename

def extractannots(filelist, outdir):
    justfilenames = []

    for file in filelist:
        with open(file, 'r') as fptr:
            filedata = json.load(fptr)
            yoloregions, filename = getannot(filedata)
        ending = filename.split('.')[-1]
        with open(os.path.join(outdir, filename.replace(ending, 'txt')), 'w') as fptr:
            for annot in yoloregions:
                annot = [str(a) for a in annot]
                fptr.write(' '.join(annot) + '\n')
        justfilenames.append(filename)

    trainset = []
    testset = []
    
    for f in justfilenames:
        r = random.choice(range(10))
        if r < 2:
            testset.append(os.path.join('data', 'obj', f.replace('.jpg', '.txt')))
        else:
            trainset.append(os.path.join('data', 'obj', f.replace('.jpg', '.txt')))
    with open('train.txt', 'w') as fptr:
        for samp in trainset:
            fptr.write(samp + '\n')
    with open('test.txt', 'w') as fptr:
        for samp in testset:
            fptr.write(samp + '\n')
            
def copy_images(source_folder, destination_folder):
    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

    # Iterate through files in the source folder
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)

        # Check if the file is a JPEG or PNG image
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            destination_path = os.path.join(destination_folder, filename)

            # Copy the file
            shutil.copy2(source_path, destination_path)
            print(f"Copied: {filename}")

if __name__ == "__main__":
    
    source_folder = 'vott/vott-json-export'
    destination_folder = 'vott2yolo'
    
    training_folder = 'data'
    
    # Create a new folder with the current datetime as its name
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join(destination_folder, current_datetime)
    os.makedirs(output_folder, exist_ok=True)

    # Create 'images' and 'labels' folders inside the new folder
    images_folder = os.path.join(output_folder, 'images')
    labels_folder = os.path.join(output_folder, 'labels')
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(labels_folder, exist_ok=True)
    
    try:
        # Copy images to the 'images' folder inside the new datetime folder
        copy_images(source_folder, images_folder)
    except Exception as em:
        print(em)
    else:
        print("Images copied successfully.")
    
    
    json_annot_files = glob.glob(os.path.join('vott', '*-asset.json'))
    
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
        
    extractannots(json_annot_files, labels_folder)
    
    print("Removing old /data")
    
    if os.path.exists(training_folder+"\\test\\"):
        # Delete the directory and its contents
        shutil.rmtree(training_folder+"\\test\\")
        print(f"The directory '{training_folder}'\test has been deleted.")
    else:
        print(f"The directory '{training_folder}\test' does not exist.")
        
    if os.path.exists(training_folder+"\\train\\"):
        # Delete the directory and its contents
        shutil.rmtree(training_folder+"\\train\\")
        print(f"The directory '{training_folder}'\train has been deleted.")
    else:
        print(f"The directory '{training_folder}\train' does not exist.")  
         
    if os.path.exists(training_folder+"\\val\\"):
            # Delete the directory and its contents
            shutil.rmtree(training_folder+"\\val\\")
            print(f"The directory '{training_folder}'\val has been deleted.")
    else:
        print(f"The directory '{training_folder}\val' does not exist.")

    
    print("Setting /data/test")
    shutil.copytree(labels_folder, training_folder+"\\test\\labels")
    shutil.copytree(images_folder, training_folder+"\\test\\images")
    
    print("Setting /data/val")
    shutil.copytree(labels_folder, training_folder+"\\val\\labels")
    shutil.copytree(images_folder, training_folder+"\\val\\images")
    
    print("Setting /data/train")
    shutil.copytree(labels_folder, training_folder+"\\train\\labels")
    shutil.copytree(images_folder, training_folder+"\\train\\images")
    
    
    
