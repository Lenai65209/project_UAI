
from ultralytics import YOLO

# initialize the YOLO class
model = YOLO('yolov5x.pt') # Replace 'model=yolov5x.pt' with new 'model=yolov5xu.pt'
# see the list of classes
classes = model.model.names

# Открываем файл для записи
with open('classes.txt', 'w') as file:
    # Получаем список классов из модели
    classes = model.model.names
    # Записываем каждый класс в файл
    for class_name in classes:
        file.write(str(class_name) + '\n')  # Преобразуем class_name в строку перед записью
        