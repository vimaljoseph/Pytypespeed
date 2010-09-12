#!/usr/bin/python 

#pytypespeed 0.04 - for testing
#(c) vimal
#This program is a Free Software, licenced under GNU GPL V3
#This program use some code from pyletters available as GNU GPL V2
#This software is in alpha stage. There may be several bugs. If you find one please mail to 
#vimal@space-kerala.org

import sys, time, random, os, pickle, pango
import time
import gobject
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
  	import gtk.glade
except:
	sys.exit(1)
	
class pytypespeed:
	""" PyTypeSpeed Typing Speed Test """
	
	def __init__(self, datalist = None):
		self.game_time=900
		self.preformat_data(datalist)
		self.password = "pass"
		self.path= "data/.pytypespeed.dat" 
		self.gladefile = "data/pytypespeed.glade"
		self.timeout = False
		self.timer_id = None
		self.seconds = 0
		self.wTree = gtk.glade.XML(self.gladefile,"winTypeSpeed")
		self.dic = { 
		"on_new_activate" : self.new_game, 
		"on_export_activate" : self.export_score,
		"on_quit_activate" : self.quit_pytypespeed, 
		"on_entry_test_key_press_event" : self.entry_test_key_press,
		"on_winTypeSpeed_destroy" : self.quit_pytypespeed,
		}
		self.wTree.signal_autoconnect(self.dic)
		
		self.main_window = self.wTree.get_widget('winTypeSpeed')
		self.entry_data = self.wTree.get_widget('entry_data')
		self.entry_test = self.wTree.get_widget('entry_test')
		self.statusbar = self.wTree.get_widget("statusbar1")
		
		
		self.tbuff1 = gtk.TextBuffer(table=None)
		self.tbuff2 = gtk.TextBuffer(table=None)
		#self.entry_name.set_text(self.name.capitalize())
		self.entry_data.set_buffer(self.tbuff1)
		self.entry_test.set_buffer(self.tbuff2)
		self.tbuff1.set_text("")
		self.tag_completed = self.tbuff1.create_tag("completed")
		self.tag_completed.set_property("foreground", "blue")
		
		self.entry_data.modify_font(pango.FontDescription("Meera 15"))
		self.entry_test.modify_font(pango.FontDescription("Meera 15"))
		self.count, self.score, self.order = 0, 0, 0
		self.words=len(self.rstring.split())
		self.main_window.maximize()
		self.entry_test.set_sensitive(False)
		self.read_score()
		self.new_game()
		
		
	def new_game(self,widget = None):
		dlg = dlgPwd()
		res,self.name,self.regno,password = dlg.run()
		if res == gtk.RESPONSE_OK:
			if password <> self.password:
				self.new_game()
			else:
				self.start_game()
		else :
			self.text_reset()		

	def start_game(self):
		self.timeout=False
		self.entry_test.set_sensitive(True)
		self.entry_test.grab_focus()
		buff2start, buff2end = self.tbuff2.get_bounds()
		self.tbuff1.set_text(self.rstring)
		self.tbuff2.delete(buff2start, buff2end)
		self.count, self.score,self.seconds = 0, 0, 0
		self.display_data()
		
			
	def text_reset(self, widget = None):
		buff2start, buff2end = self.tbuff2.get_bounds()
		self.tbuff1.set_text("")
		self.tbuff2.delete(buff2start, buff2end)
		self.count, self.score, self.seconds = 0, 0, 0
		
		
	def display_data(self):
		"""Display registration details in the status bar"""
		status="Name : %s, Reg. No. : %s" %(self.name,self.regno)
		self.statusbar.push(-1,status)	
	
	def display_result(self):
		"""Display score as a message box and in the status bar"""
		status="RegNo.: %s  CPM: %f  Accuracy: %s  WPM: %f  Seconds: %f  Date: %s" % (\
		self.records[-1][5],self.records[-1][0],self.records[-1][1],self.records[-1][2],self.records[-1][3],self.records[-1][4])
		self.statusbar.push(-1,status)
				
	def entry_test_key_press(self, widget = None, data = None):
			if self.count == 0:
				self.time = time.time()
				self.timer_id = gobject.timeout_add(1000, self.update_clock)
			buff1start, buff1end = self.tbuff1.get_bounds()
			buff2start, buff2end = self.tbuff2.get_bounds()
			buff1offset = self.tbuff1.get_iter_at_offset(self.count + 1)
			if data.string == self.rstring[self.count]:
				self.count += 1
				self.score += 1
				if data.hardware_keycode == 65:
					self.tbuff1.apply_tag(self.tag_completed, buff1start, buff1offset)
				self.tbuff2.insert(buff2end, data.string)
			elif data.string:
				self.score -= 1
			if self.timeout:
				self.calculate_score()	
				status="Your time is over\n\nRegNo: %s  CPM: %f  Accuracy: %s  WPM: %f  Seconds: %f  Date: %s" % (\
				self.records[-1][5],self.records[-1][0],self.records[-1][1],self.records[-1][2],self.records[-1][3],self.records[-1][4])
				dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,message_format=status)
				response  = dialog.run()
				dialog.destroy()
				self.entry_test.set_sensitive(False)	
			elif (self.count == self.rlen):
				self.calculate_score()	
				status="RegNo: %s  CPM: %f  Accuracy: %s  WPM: %f  Seconds: %f  Date: %s" % (\
				self.records[-1][5],self.records[-1][0],self.records[-1][1],self.records[-1][2],self.records[-1][3],self.records[-1][4])
				dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,message_format=status)
				response  = dialog.run()
				dialog.destroy()
				self.entry_test.set_sensitive(False)
				
	def update_clock(self):
		self.seconds=time.time() - self.time
		if self.seconds > self.game_time:
			self.timeout=True
			return False	
		return True
			
	def calculate_score(self):
		seconds = self.seconds
		self.seconds=0
		self.order += 1
		if self.timeout:
			timeout="Timeout :Not Completed"
		else :
			timeout="Completed"
		local_list = [
			self.count / (seconds / 60),					# CPM
			"%f%%"  % (self.score / float(self.rlen) * 100),		# Accuracy
			self.count / (seconds / 60) / 5,					# WPM
			seconds,							# Seconds
			time.strftime("%a %d %b, %H:%M:%S", time.localtime()),		# Date
			self.regno,						# Username
			self.order,							# Order
			timeout 			#Time out
			]
		self.records.append(local_list)
		self.display_result()
		self.save_score()
		self.text_reset()
	
	def preformat_data(self,datalist):
		tstr=""
		for i in datalist:
			line = i[:-1].decode('UTF-8')
			tstr += "%s " % line.strip()
		self.rstring = tstr[:-1]
		self.rlen = len(self.rstring)
		
	def read_score(self):
		if os.path.isfile(self.path):
		 	file = open(self.path, "rb")
			pickle_data = pickle.load(file)
			self.records=pickle_data[0]
			file.close()
		else : 
			self.records=[]
	def save_score(self):
		#path = "/home/%s/.pytypespeed.dat" % os.getlogin()
		file = open(self.path, "wb")
		pickle_data = ( self.records,
				self.order,
				self.name,
				self.regno,
				self.words,)
		pickle.dump(pickle_data, file)
		file.close()
	
	def export_score(self,widget=None):
		path = "/home/%s/typespeed_score.csv" % os.getlogin()
		if os.path.isfile(self.path):
			file = open(self.path, "rb")
			pickle_data = pickle.load(file)
			#print pickle_data[0]
			rec=pickle_data[0]
			file.close()
		file= open(path,'w')
		file.write("Regno., Time(sec), Accuracy,CPM,Date, System Time, Remarks\n")
		for i in rec:
			str="%s,%s,%s,%s,%s,%s,%s" %(i[5],i[3],i[1],i[0],i[4],i[7],"\n")
			file.write(str)
		file.close()
		status="Score saved to your home folder as typespeed_score.csv"
		dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,message_format=status)
		response  = dialog.run()
		dialog.destroy()
	
	def quit_pytypespeed(self, widget = None):
		self.save_score()
		gtk.main_quit()
	

	
class dlgPwd:
	"""Password dialog box"""
	def __init__(self):
		self.gladefile = "data/pytypespeed.glade"
		self.password = ""
				
	def run(self):
		self.wTree = gtk.glade.XML(self.gladefile, "dlgPwd")
		#Get the actual dialog widget
		self.dlg = self.wTree.get_widget("dlgPwd")
		self.entry_password=self.wTree.get_widget("entry_password")
		self.entry_reg=self.wTree.get_widget("entry_reg")
		self.entry_name=self.wTree.get_widget("entry_name")
		self.result= self.dlg.run()
		self.password = self.entry_password.get_text()
		self.name = self.entry_name.get_text()
		self.regno= self.entry_reg.get_text()
		self.dlg.destroy()
		#return the result and password
		return self.result,self.name,self.regno,self.password


if __name__ == "__main__":
	path = "data/typespeed.txt" 
	datalist = open(path, "r").readlines()
	hwg = pytypespeed(datalist)
	gtk.main()
	
