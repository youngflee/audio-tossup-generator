#!/usr/bin/env python3.9
from pytube import YouTube
from pydub import AudioSegment
import os
from os import path
import csv
import re
import sys

tossups = {}
prefix = "Pavao and Renert's Listening Room"
#chosen = [*range(66, 71)]
chosen = [9, 20, 32, 38, 51]

with open('Sheets/'+prefix+' - Clips.csv', mode='r') as csv_file:
	csv_reader = csv.DictReader(csv_file)
	for row in csv_reader:
		if(row['Question']!='' and row['Direct link']!='' and int(row['Question']) in chosen):
			if(row['Clip']=='1'):
				tossups[row['Question']] = [[row['Direct link'], row['YouTube video ID'], row['Start at (sec)'], row['Length (sec)']]]
			else:
				tossups[row['Question']].append([row['Direct link'], row['YouTube video ID'], row['Start at (sec)'], row['Length (sec)']])

for tossup in tossups:
	tossup_files = []
	for file in tossups[tossup]:
		if(not path.isfile("Files/"+file[1]+".mp4")):
			try:
				current_vid = YouTube(file[0]).streams.filter(
					only_audio=True, progressive=False, subtype='mp4').first().download("Files", file[1], skip_existing=True)
				tossup_files.append([current_vid, float(file[2]), float(file[3])])
			except Exception as inst:
				print(inst)
				print(file)
		else:
			tossup_files.append(["Files/"+file[1]+".mp4", float(file[2]), float(file[3])])
	dummy_counter = 0
	total_song = 0
	for clip in tossup_files:
		song = AudioSegment.from_file(clip[0], "mp4")
		chopped = song[clip[1]*1000:clip[1]*1000+clip[2]*1000]
		faded = chopped.fade_in(750).fade_out(750)
		if(dummy_counter == 0):
			total_song = faded
		else:
			total_song = total_song + faded
		dummy_counter += 1
	if(total_song!=0):
		pattern = re.compile(prefix+" Tossup "+tossup+"[a-z]?.mp3")
		directory = "Regenerated/"
		token = ""
		for filepath in sorted(os.listdir(directory)):
			if pattern.match(filepath):
				token = filepath
		if(token!=""):
			if(token[-5:-4]!=tossup):
				total_song.export("Regenerated/"+token[:-5]+chr(ord(token[-5:-4])+1)+".mp3", format="mp3")
			else:
				total_song.export("Regenerated/"+prefix+" Tossup "+tossup+"a"+".mp3", format="mp3")
		else:
			total_song.export("Regenerated/"+prefix+" Tossup "+tossup+".mp3", format="mp3")
