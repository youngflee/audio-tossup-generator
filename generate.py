#!/usr/bin/env python3.13
import yt_dlp
from yt_dlp.utils import download_range_func
from pydub import AudioSegment
import os
from os import path
import csv
import re
import sys

os.mkdir("Files")
tossups = {}
sheetsFile = "Private Audio Questions - Ten.csv"
chosen = [1]
#chosen = [*range(1, 8)]

def tokenFinder(tossup, directory):
	pattern = re.compile(sheetsFile+" Tossup "+tossup+"[a-z]?.mp3")
	token = ""
	for filepath in sorted(os.listdir(directory)):
		if pattern.match(filepath):
			token = filepath
	return token

def tokenFinderFiles(name, directory):
	pattern = re.compile(name+"(\(1\))*.m4a")
	token = ""
	for filepath in sorted(os.listdir(directory), reverse=True):
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
		filename = file[1]
		localDirectory = "Files/"
		token = tokenFinderFiles(filename, localDirectory)
		if(token!=""):
			filename = token[:len(token)-4]+"(1)"
			print(filename)
		yt_opts = {
			'format': 'bestaudio[ext=m4a]',
			'outtmpl': 'Files/'+filename+'.m4a',
			'download_ranges': download_range_func(None, [(float(file[2]), float(file[2]) + float(file[3]))]),
			'force_keyframes_at_cuts': True,
			'cookiesfrombrowser': ('chrome',)#, ## uncomment if you need to use this for age-restricted videos
			#'extractor_args': {
			#	'youtube': {
			#		'player_client': ['default','web_safari'],
			#		'player_js_version': ['actual']
			#	}
			#},
			#'postprocessors': [{
			#	'key': 'FFmpegExtractAudio',
			#	'preferredcodec': 'm4a',
			#	'preferredquality': '192'
			#}]
		}
		with yt_dlp.YoutubeDL(yt_opts) as ydl:
			ydl.download(file[0])
		tossup_files.append(["Files/"+filename+'.m4a', float(file[2]), float(file[3])])
	dummy_counter = 0
	total_song = 0
	for clip in tossup_files:
		song = AudioSegment.from_file(clip[0], "m4a")
		faded = song.fade_in(750).fade_out(750)
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