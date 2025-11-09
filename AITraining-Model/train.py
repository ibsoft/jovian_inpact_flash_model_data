import subprocess
from ultralytics import YOLO
import yaml



try:
    subprocess.run(['python', "convert2yolo.py"], check=True)
    print(f"The script convert2yolo.py has been successfully executed.")
except subprocess.CalledProcessError as e:
    print(f"Error executing the script: {e}")


with open('mydataset.yaml', 'r') as file:
    yaml_content = yaml.safe_load(file)

print(yaml_content)


# Create a new YOLO model from scratch
model = YOLO('models/best.pt')

results = model.train(data="mydataset.yaml", epochs=300)

# Evaluate the model's performance on the validation set
results = model.val()

# Perform object detection on an image using the model
#results = model('best.pt')

# Export the model to ONNX format
#success = model.export(format='onnx')
