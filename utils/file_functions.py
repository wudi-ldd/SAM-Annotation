import numpy as np
from PyQt5.QtWidgets import (QFileDialog, QListWidgetItem, QGraphicsScene,
                             QGraphicsPixmapItem, QGraphicsView, QGraphicsPolygonItem,QGraphicsEllipseItem)
from PyQt5.QtGui import QColor, QPixmap,QPen, QBrush, QPolygonF,QCursor
from PyQt5.QtCore import QPointF,Qt
from PIL.ImageQt import ImageQt
from PIL import Image
import json
import cv2
import os
import sys
sys.path.append("..")
from segment_anything import sam_model_registry, SamPredictor
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

class ImageViewer():
    def __init__(self, listWidget,categoryList,annList,textEdit,graphicsView,parent=None):
        self.listWidget = listWidget
        self.categoryList = categoryList
        self.annList = annList
        self.textEdit = textEdit
        self.graphicsView = graphicsView  # Assign the passed graphicsView to self
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)  # Set the scene of the passed graphicsView
        self.pixmapItem = None
        self.folderPath = ""
        self.isPointButtonClicked = False
        self.polygonItems = []  
        self.pointStack = []  
        self.annotationStack = [] 
        self.ButtonClicked = 0
        self.currentHighlight = None  

        # Connect signals
        self.listWidget.itemClicked.connect(self.displayImageInfo)
        self.listWidget.itemClicked.connect(self.displayImage)
        self.graphicsView.mousePressEvent = self.graphicsViewMousePressEvent  # Override the mousePressEvent for graphicsView
        self.annList.itemClicked.connect(self.highlightMask)

        #初始化SAM模型
        sam_checkpoint = "checkpoints\sam_vit_h_4b8939.pth"
        model_type = "vit_h"
        device = "cuda"
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        sam.to(device=device)
        self.predictor = SamPredictor(sam)


    def openImageFolder(self):
        folder_path = QFileDialog.getExistingDirectory(None, "Select Image Folder")
        if folder_path:
            self.listWidget.clear()
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            for file in files:
                item = QListWidgetItem(file)
                json_filename = os.path.splitext(file)[0] + '.json'
                json_filepath = os.path.join(folder_path, json_filename)
                if os.path.exists(json_filepath):
                    item.setForeground(QColor("red"))
                    self.listWidget.addItem(item)
                else:
                    self.listWidget.addItem(item)
            self.folderPath = folder_path

    def displayImage(self, item):
        self.currentHighlight = None
        image_path = os.path.join(self.folderPath, item.text()).replace('\\', '/')
        self.image = Image.open(image_path)
        pixmap = QPixmap(image_path)
        self.pixmapItem = QGraphicsPixmapItem(pixmap)
        self.scene.clear()
        self.scene.addItem(self.pixmapItem)
        self.annotationStack.clear()

        json_path = image_path.rsplit('.', 1)[0] + '.json'
        if os.path.isfile(json_path):
            with open(json_path, 'r') as json_file:
                data = json.load(json_file)
                shapes = data.get('shapes', [])
                for shape in shapes:
                    self.annotationStack.append(shape)
        self.drawPolygon()
        self.updateAnnList()  

        if hasattr(self, 'maskPixmapItem'):
            self.maskPixmapItem = QGraphicsPixmapItem()
            self.scene.addItem(self.maskPixmapItem)
        else:
            self.maskPixmapItem = QGraphicsPixmapItem()
            self.scene.addItem(self.maskPixmapItem)

    def displayImageInfo(self, item):
        image_path = os.path.join(self.folderPath, item.text())  # Use the stored folder path
        pixmap = QPixmap(image_path)

        width = pixmap.width()
        height = pixmap.height()
        channels = pixmap.depth() // 8

        info_html = f"""
        <html>
        <head/>
        <body>
        <p><b>Image Name:</b> {item.text()}</p>
        <p><b>Width:</b> {width} pixels</p>
        <p><b>Height:</b> {height} pixels</p>
        <p><b>Channels:</b> {channels}</p>
        </body>
        </html>
        """
        self.textEdit.setHtml(info_html)

    def onPointButtonClick(self):
        self.isPointButtonClicked = True  
        self.graphicsView.setCursor(QCursor(Qt.CrossCursor)) 

    

    def graphicsViewMousePressEvent(self, event):
        if not self.isPointButtonClicked:
            QGraphicsView.mousePressEvent(self.graphicsView, event)
            return
        # Get the click position
        position = self.graphicsView.mapToScene(event.pos())

        # Check if the position is within the pixmap item
        if self.pixmapItem and self.pixmapItem.contains(position):
            # Map the position to the pixmap item's coordinate system
            relative_position = self.pixmapItem.mapFromScene(position)
            # Determine the color based on the mouse button
            if event.button() == Qt.LeftButton:
                color = Qt.red
                self.ButtonClicked = 1
            elif event.button() == Qt.RightButton:
                color = Qt.green
                self.ButtonClicked = 0
            else:
                # For other mouse buttons, you can choose to do nothing or handle them differently
                QGraphicsView.mousePressEvent(self.graphicsView, event)
                return

            # Create and add a colored dot to the scene at the click position
            dot = QGraphicsEllipseItem(relative_position.x(), relative_position.y(), 10, 10)
            dot.setBrush(QBrush(color))
            self.scene.addItem(dot)
            point_info = {
            'dot_item': dot,
            'position': [relative_position.x(), relative_position.y()],
            'label_type': self.ButtonClicked,
            'maks':[]
        }
            self.pointStack.append(point_info)
            image=np.array(self.image)
            self.predictor.set_image(image)
            mask, score, logit = self.predictor.predict(
            point_coords=np.array([point_info['position'] for point_info in self.pointStack]).astype(float),
            point_labels=np.array([point_info['label_type'] for point_info in self.pointStack]).astype(float),
            multimask_output=True,
        )
            self.pointStack[-1]['mask'] = mask
            self.displayMask(mask)
            # Optionally, you might want to store or use the click position
            print(f"Clicked position relative to image: ({relative_position.x()}, {relative_position.y()})")

        # Call the base class implementation to preserve the default behaviour
        QGraphicsView.mousePressEvent(self.graphicsView, event)
    
    def undoLastPoint(self):
        if not self.pointStack:
            return
        else: 
            last_point_info = self.pointStack.pop() 
            self.scene.removeItem(last_point_info['dot_item']) 
            
            if self.pointStack:
                mask = self.pointStack[-1]['mask']
            else:
                mask = None
                self.isPointButtonClicked = False
                self.graphicsView.setCursor(QCursor(Qt.ArrowCursor))

            self.displayMask(mask)
            
            last_position = last_point_info['position']
            print(f"Removed point at position: ({last_position})")

    def displayMask(self, mask):
        if mask is None:
            pixmap = self.pixmapItem.pixmap()

            self.scene.clear()
            
            self.pixmapItem = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmapItem)

            self.maskPixmapItem = QGraphicsPixmapItem()
            self.scene.addItem(self.maskPixmapItem)
        else:
            mask_image = Image.fromarray((mask[0] * 255).astype('uint8'))

            mask_image = mask_image.convert('RGBA')
            mask_data = mask_image.getdata()
            new_data = []
            for item in mask_data:
                if item[0] == 255:  
                    new_data.append((255, 0, 0, 100))  
                else:
                    new_data.append((255, 255, 255, 0))  
            mask_image.putdata(new_data)

            qimage = ImageQt(mask_image)

            mask_pixmap = QPixmap.fromImage(qimage)

            if hasattr(self, 'maskPixmapItem'):
                self.maskPixmapItem.setPixmap(mask_pixmap)
            else:
                self.maskPixmapItem = QGraphicsPixmapItem(mask_pixmap)
                self.scene.addItem(self.maskPixmapItem)

        self.scene.update()
    
    def getMaskContourPoints(self, mask):
        binary_mask = np.uint8(mask) * 255
        assert len(mask.shape) == 2, "Mask must be a 2-dimensional array"
    
        binary_mask = np.uint8(mask) * 255
    
        assert np.setdiff1d(binary_mask, [0, 255]).size == 0, "binary_mask must contain only 0 and 255"
            
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            contour_points = contours[0].reshape(-1, 2).tolist()
        else:
            contour_points = []

        return contour_points

    def finishAnnotation(self):
        if self.pointStack: 
            last_annotation_info = self.pointStack[-1]  
            mask_contour_points = self.getMaskContourPoints(last_annotation_info['mask'][0])
            current_item = self.categoryList.currentItem().text()

            annotation_info = {
                "label": current_item,
                "line_color": None,
                "fill_color": None,
                "points": mask_contour_points,
                "group_id": None,
                "shape_type": "polygon",
                "flags": {}
            }

            self.annotationStack.append(annotation_info)
            print(len(self.annotationStack))

            self.pointStack.clear()
            self.displayMask(None)

            self.drawPolygon()
            self.updateAnnList()
            
            self.currentHighlight = None

    def drawPolygon(self):
        for annotation_info in self.annotationStack:
            points = annotation_info['points']
            
            polygon = QPolygonF()
            for point in points:
                polygon.append(QPointF(point[0], point[1]))

            polygon_item = QGraphicsPolygonItem(polygon)

            polygon_item.setPen(QPen(Qt.black, 2))
            
            polygon_item.setBrush(QBrush(QColor(255, 0, 0, 100)))

            self.scene.addItem(polygon_item)
    
    def updateAnnList(self):
        self.annList.clear()  

        for annotation in self.annotationStack:
            label = annotation['label']
            item = QListWidgetItem(label) 
            self.annList.addItem(item) 

    def deleteAnnotation(self):
        currentRow = self.annList.currentRow() 

        if currentRow != -1:
            del self.annotationStack[currentRow] 
            self.annList.takeItem(currentRow)  
            self.drawPolygon()
            self.updateAnnList()
    
    def highlightMask(self):
        currentRow = self.annList.currentRow()  
        annotation_info = self.annotationStack[currentRow] 
        mask_contour_points = annotation_info['points']  

        if self.currentHighlight:
            if self.currentHighlight.scene() == self.scene:
                self.scene.removeItem(self.currentHighlight)
            self.currentHighlight = None

        polygon = QPolygonF()
        for point in mask_contour_points:
            polygon.append(QPointF(point[0], point[1]))

        polygon_item = QGraphicsPolygonItem(polygon)

        polygon_item.setPen(QPen(Qt.red, 4))  
        polygon_item.setBrush(QBrush(Qt.yellow)) 


        self.scene.addItem(polygon_item)
        self.currentHighlight = polygon_item

    def saveAnnotationsToFile(self):
        if hasattr(self, 'image') and self.image is not None:
            image_path = self.image.filename
            json_path = image_path.rsplit('.', 1)[0] + '.json'
            
            json_data = {
                "version": "3.16.7",
                "flags": {},
                "shapes": self.annotationStack,
                "lineColor": [0, 255, 0, 128],
                "fillColor": [255, 0, 0, 128],
                "imagePath": os.path.basename(image_path),
                "imageData": None,
                "imageHeight": self.image.height,
                "imageWidth": self.image.width
            }
            
            dir_name = os.path.dirname(json_path)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=4)


            

