import os
from pathlib import Path
import cv2, imutils
import time
import numpy as np
import pyshine as ps
import argparse
import subprocess
from skimage.metrics import structural_similarity as compare_ssim
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage
import ocr
import setROI

captureDevice = 1
saveDir = 'D:/IMG/cvCapture'
w_frame = 1024
h_frame = 576
diff_target = 0.9

class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(w_frame*1.25, h_frame*1.25)
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
		self.gridLayout_2.setObjectName("gridLayout_2")
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.label = QtWidgets.QLabel(self.centralwidget)
		self.label.setText("")
		self.label.setPixmap(QtGui.QPixmap("images/H.png"))
		self.label.setObjectName("label")
		self.horizontalLayout.addWidget(self.label)
		self.gridLayout = QtWidgets.QGridLayout()
		self.gridLayout.setObjectName("gridLayout")
		self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
		self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
		self.verticalSlider.setObjectName("verticalSlider")
		self.gridLayout.addWidget(self.verticalSlider, 0, 0, 1, 1)
		self.verticalSlider_2 = QtWidgets.QSlider(self.centralwidget)
		self.verticalSlider_2.setOrientation(QtCore.Qt.Vertical)
		self.verticalSlider_2.setObjectName("verticalSlider_2")
		self.gridLayout.addWidget(self.verticalSlider_2, 0, 1, 1, 1)
		self.label_2 = QtWidgets.QLabel(self.centralwidget)
		self.label_2.setAlignment(QtCore.Qt.AlignCenter)
		self.label_2.setObjectName("label_2")
		self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
		self.label_3 = QtWidgets.QLabel(self.centralwidget)
		self.label_3.setAlignment(QtCore.Qt.AlignCenter)
		self.label_3.setObjectName("label_3")
		self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)
		self.horizontalLayout.addLayout(self.gridLayout)
		self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 2)
		self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
		self.horizontalLayout_2.setObjectName("horizontalLayout_2")
		self.pushButton = QtWidgets.QPushButton(self.centralwidget)

		self.pushButton.setObjectName("pushButton")
		self.horizontalLayout_2.addWidget(self.pushButton)
		self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_3.setObjectName("pushButton_3")	
		self.horizontalLayout_2.addWidget(self.pushButton_3)
		self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_2.setObjectName("pushButton_2")
		self.horizontalLayout_2.addWidget(self.pushButton_2)
		self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
		spacerItem = QtWidgets.QSpacerItem(313, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.gridLayout_2.addItem(spacerItem, 1, 1, 1, 1)
		MainWindow.setCentralWidget(self.centralwidget)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.retranslateUi(MainWindow)
		self.verticalSlider.valueChanged['int'].connect(self.brightness_value)
		self.verticalSlider_2.valueChanged['int'].connect(self.blur_value)
		self.pushButton_2.clicked.connect(self.loadImage)
		self.pushButton.clicked.connect(self.setRoiPart)
		self.pushButton_3.clicked.connect(self.setRoiZone)
  
		QtCore.QMetaObject.connectSlotsByName(MainWindow)
		
		# Added code here
		self.filename = 'Snapshot '+str(time.strftime("%Y-%b-%d at %H.%M.%S %p"))+'.png' # Will hold the image address location
		self.tmp = None # Will hold the temporary image for display
		self.tmpPrevious = None # 
		self.brightness_value_now = 0 # Updated brightness value
		self.blur_value_now = 0 # Updated blur value
		self.fps=0
		self.started = False
		self.grayCurrent = 0
		self.grayPrevious = 0
		self.ocrText = ''

	def loadImage(self):
		if self.started:
			self.started=False
			self.pushButton_2.setText('Start')	
		else:
			self.started=True
			self.pushButton_2.setText('Stop')
		
		cam = True # True for webcam
		if cam:
			vid = cv2.VideoCapture(captureDevice)
		else:
			vid = cv2.VideoCapture('video.mp4')
		
		cnt=0
		frames_to_count=20
		st = 0
		fps=0
		
		while(vid.isOpened()):
			
			img, self.image = vid.read()
			self.image  = imutils.resize(self.image ,height = 1080 )
			if cnt == frames_to_count:
				try: # To avoid divide by 0 we put it in try except
					print(frames_to_count/(time.time()-st),'FPS') 
					self.fps = round(frames_to_count/(time.time()-st))
					st = time.time()
					cnt=0
				except:
					pass
			
			cnt+=1
			self.checkDiff(self.image)
			self.update()
			
			key = cv2.waitKey(1) & 0xFF
			if self.started==False:
				break
				print('Loop break')
	
	def setPhoto(self,image):
		self.tmp = image
		image = imutils.resize(image,width=w_frame)
		frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
		self.label.setPixmap(QtGui.QPixmap.fromImage(image))

	def brightness_value(self,value):
		self.brightness_value_now = value
		print('Brightness: ',value)
		self.update()
		
		
	def blur_value(self,value):
		self.blur_value_now = value
		print('Blur: ',value)
		self.update()
	
	
	def changeBrightness(self,img,value):
		hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
		h,s,v = cv2.split(hsv)
		lim = 255 - value
		v[v>lim] = 255
		v[v<=lim] += value
		final_hsv = cv2.merge((h,s,v))
		img = cv2.cvtColor(final_hsv,cv2.COLOR_HSV2BGR)
		return img
		
	def changeBlur(self,img,value):
		kernel_size = (value+1,value+1) # +1 is to avoid 0
		img = cv2.blur(img,kernel_size)
		return img
	
	def update(self):
		img = self.changeBrightness(self.image,self.brightness_value_now)
		img = self.changeBlur(img,self.blur_value_now)
		self.setPhoto(img)
		
	def checkDiff(self,_img):
		gray = cv2.cvtColor(_img, cv2.COLOR_BGR2GRAY)
		img = _img
		if self.tmpPrevious is not None:
			diff_frame = gray - self.tmpPrevious
			diff_frame -= diff_frame.min()
			#disp_frame = np.uint8(255.0*diff_frame/float(diff_frame.max()))
			(score, diff) = compare_ssim(gray, self.tmpPrevious, full=True)
			diff = (diff * 255).astype("uint8")
			#print("SSIM: {}%".format(score*100))
			_text ='{0:.2f}'.format(score)
			text  = f'Diff: {_text} / {diff_target}'
			
			if score < diff_target:
				self.savePhoto()
				img = ps.putBText(_img,text,text_offset_x=250,text_offset_y=100,vspace=20,hspace=10, font_scale=1.0,background_RGB=(222,20,10),text_RGB=(255,255,255))
			else:
				img = ps.putBText(_img,text,text_offset_x=250,text_offset_y=100,vspace=20,hspace=10, font_scale=1.0,background_RGB=(10,20,222),text_RGB=(255,255,255))
		else:
			self.tmpPrevious = gray
		self.tmpPrevious = gray
		self.setPhoto(img)	
  
	def savePhoto(self):
		""" This function will save the image """
		_image,Part,Zone = ocrLenso.main(self.image)
		self.filename = Part+'_'+Zone+'_'+str(time.strftime("%Y-%b-%d_%H_%M_%S"))+'.jpg'
		cv2.imwrite(os.path.join(saveDir, self.filename),_image,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
		print('Image saved as:',self.filename)
	
	def setRoiPart(self):
		if self.started:
			self.started=False
			self.pushButton_2.setText('ROI Set')	
			cv2.imwrite('_T.jpg',self.tmp,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
			self.started=setROI.main(0)	
			self.pushButton_2.setText('Stop')
			print('Image saved as:',self.filename)
		else:
			self.started=True
			self.pushButton_2.setText('Stop')



	def setRoiZone(self):
		if self.started:
			self.started=False
			self.pushButton_2.setText('ROI Set')	
			cv2.imwrite('_T.jpg',self.tmp,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
			self.started=setROI.main(1)		
			self.pushButton_2.setText('Stop')			
			print('Image saved as:',self.filename)
		else:
			self.started=True
			self.pushButton_2.setText('Stop')

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "PyShine video process"))
		self.pushButton_2.setText(_translate("MainWindow", "Start"))
		self.label_2.setText(_translate("MainWindow", "Brightness"))
		self.label_3.setText(_translate("MainWindow", "Blur"))
		self.pushButton.setText(_translate("MainWindow", "Set ROI Part"))
		self.pushButton_3.setText(_translate("MainWindow", "Set ROI Zone"))

if __name__ == "__main__":
	import sys
	Path(saveDir).mkdir(parents=True, exist_ok=True)
	Path(saveDir+"/ocr").mkdir(parents=True, exist_ok=True)
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())