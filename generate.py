#!/usr/bin/env python3.9
from pytube import YouTube
from pydub import AudioSegment
import os
from os import path
import csv
import re
import sys

tossups = {}
sheetsFile = "Sample.csv"
chosen = [*range(66, 71)]
#chosen = [9, 20, 32, 38, 51]

def tokenFinder(tossup, directory):
	pattern = re.compile(sheetsFile+" Tossup "+tossup+"[a-z]?.mp3")
	token = ""
	for filepath in sorted(os.listdir(directory)):
		if pattern.match(filepath):
			token = filepath
	return token

def finalPathGen(token):
	final_filepath = ""
	for potentialDigitIndex in range(len(token)-2,0,-1): ##starts from len(token)-2 to exclude the 3 in mp3
		if(token[potentialDigitIndex].isdigit()):
			if(token[potentialDigitIndex+1].isalpha()):
				final_filepath = token[0:potentialDigitIndex+1]+chr(ord(token[potentialDigitIndex+1])+1)+".mp3"
				break
			else:
				final_filepath = token[0:potentialDigitIndex+1]+"a.mp3"
				break
	return final_filepath

with open('Sheets/'+sheetsFile, mode='r') as csv_file:
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
		try:
			current_vid = YouTube(file[0]).streams.filter(
				only_audio=True, progressive=False, subtype='mp4').first().download("Files", file[1], skip_existing=True)
			tossup_files.append([current_vid, float(file[2]), float(file[3])])
		except Exception as inst:
			print(inst)
			print(file)
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
		directory = "Tossups/"
		token = tokenFinder(tossup, directory)
		final_filepath = sheetsFile+" Tossup "+tossup+".mp3"
		if(token!=""):
			final_filepath = finalPathGen(token)
			if(final_filepath==""):
				raise Exception("final_filepath came back empty")
		print(final_filepath)
		total_song.export(directory+final_filepath, format="mp3")
dir = "Files"
for f in os.listdir(dir):
	os.remove(os.path.join(dir, f))
os.rmdir(dir)