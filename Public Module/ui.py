import sys
import requests
import base64
import json
import uuid

from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QImage, QImageReader
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication
from PyQt5.QtWidgets import QInputDialog, QLabel, QLineEdit, QMessageBox

from qr_code import QrCode

class MobileApp(QMainWindow):
   
    def __init__(self, user):
        
        super().__init__()
        self.title = "Public Portal"
        self.icon_path = 'C:/Users/AKAY/Downloads/logo.png'
        self.location = None
        self.name = None
        self.mobile = None
        self.image = None
        self.key_points = None
        self.user = user
        
        self.initialize()

    def initialize(self):
       
        self.setWindowIcon(QtGui.QIcon(self.icon_path))
        self.setFixedSize(800, 700)
        self.setWindowTitle(self.title)

        upload_image_bt = QPushButton("Image", self)
        upload_image_bt.move(360, 280)
        upload_image_bt.clicked.connect(self.openFileNameDialog)

        save_bt = QPushButton("Save ", self)
        save_bt.move(300, 640)
        save_bt.clicked.connect(self.save)

        qr_bt = QPushButton("QR ", self)
        qr_bt.move(420, 640)
        qr_bt.clicked.connect(self.qr_code)

        self.get_name()
        self.get_mobile_num()
        self.get_location()
        self.show()

    def qr_code(self):
        self.qr_code = QrCode(self.user)

    def get_name(self):
        self.name_label = QLabel(self)
        self.name_label.setText('YOUR NAME')
        self.name_label.move(185,65)

        self.name = QLineEdit(self)
        self.name.move(350, 62)
        self.name.resize(160,35)

    def get_mobile_num(self):
        self.mobile_label = QLabel(self)
        self.mobile_label.setText('CONTACT')
        self.mobile_label.move(192, 140)

        self.mobile = QLineEdit(self)
        self.mobile.move(350, 138)
        self.mobile.resize(160,35)

    def get_location(self):
        self.location_label = QLabel(self)
        self.location_label.setText('LOCATION')
        self.location_label.move(195, 215)

        self.location = QLineEdit(self)
        self.location.move(350, 213)
        self.location.resize(160,35)
        
    def get_facial_points(self, image_url) -> list:
       
        URL = "http://localhost:8002/image"
        f = [('image', open(image_url, 'rb'))]
        try:
            result = requests.post(URL, files=f)
            if result.status_code == 200:
                return json.loads(result.text)['encoding']
            else:
                QMessageBox.about(self, "Error", "Couldn't find face in Image")
                return None
        except Exception as e:
            QMessageBox.about(self, "Error", "Couldn't connect to face encoding API")
            return None

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(
                    self, "QFileDialog.getOpenFileName()",
                    "", "jpg file (*.jpg)", options=options)

        if self.fileName:
            self.key_points = self.get_facial_points(self.fileName)
            if self.key_points:
                label = QLabel(self)
                pixmap = QPixmap(self.fileName)
                pixmap = pixmap.scaled(320, 350)
                label.setPixmap(pixmap)
                label.resize(250, 280)
                label.move(280, 335)
                label.show()

                print("Image Uploaded")

    def get_entries(self):
        entries = {}
        if self.mobile.text() != "" and self.name.text() != "" and self.location.text() != "":
            entries['name'] = self.name.text()
            entries['location'] = self.location.text()
            entries['mobile'] = self.mobile.text()
            return entries
        else:
            return None
        
    def save_to_db(self, entries):
        URL = "http://localhost:8000/user_submission"
        headers = {'Content-Type': 'application/json',
                   'Accept':'application/json'}

        byte_content = open(self.fileName, 'rb').read()
        base64_bytes = base64.b64encode(byte_content)
        base64_string = base64_bytes.decode("utf-8")

        entries['image'] = base64_string
        try:            
            res = requests.post(URL, json.dumps(entries), headers=headers)
            if res.status_code == 200:
                QMessageBox.about(self, "Success", "Saved successfully")
            else:
                QMessageBox.about(self, "Error", "Something went wrong while saving")
                print(res.text)
        except Exception as e:
            print(str(e))
            QMessageBox.about(self, "Error", "Couldn't connect to database")

    def generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def save(self):
        entries = self.get_entries()
        if entries:
            entries['face_encoding'] = self.key_points
            entries['sub_id'] = self.generate_uuid()
            self.save_to_db(entries)
        else:
            QMessageBox.about(self, "Error", "Please fill all entries")


app = QApplication(sys.argv)
style = """
        QWidget{
            background: #232326;
        }
        QLabel{
            font: Big-john;
            font-weight: bold;
            font-size: 16px;
            color: #f70a61;
        }
        QLabel#round_count_label, QLabel#highscore_count_label{
            border: 1px solid #fff;
            border-radius: 8px;
            padding: 2px;
        }
        QPushButton
        {
            color: white;
            background: #f70a61;
            border: 1px #DADADA solid;
            padding: 5px 10px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 9pt;
            outline: none;
        }
        QPushButton:hover{
            border: 1px #C6C6C6 solid;
            color: #fff;
            background: #ad1a50;
        }
        QLineEdit {
            padding: 1px;
            color: #fff;
            font-weight: bold;
            font-size: 14px;
            border-style: solid;
            border: 2px solid #fff;
            border-radius: 8px;
        }
    """
app.setStyleSheet(style)
w = MobileApp('abhinay')
sys.exit(app.exec())
