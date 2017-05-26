# import the necessary packages
import uuid
import os

class TempImage:
	def __init__(self, frequency, basePath="./imageconfig/images", ext=".jpg"):
		# construct the file path
		self.path = "{base_path}/{frequency}{ext}".format(base_path=basePath,
			frequency = frequency ,ext=ext)

	def cleanup(self):
		# remove the file
		os.remove(self.path)
