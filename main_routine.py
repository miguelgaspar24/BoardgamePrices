
import datetime as dt
import logging
import os
import sys
import time

import pandas as pd

import jogonamesa_spyder as spyder1
import gameplay_spyder as spyder2
import jogartabuleiro_spyder as spyder3


def set_custom_logger(logger_level, savepath, log_filename):
	'''
	Creates a custom logger. Takes the following parameters:

	logger_level (logging.LEVEL): logging level.
	savepath     (str): path to where to save the logger output.
	log_filename (str): name of the saved logger.

	Returns a logger object with its associated handler and formatter.
	'''

	logger = logging.getLogger(log_filename.split('.')[0])
	logger.setLevel(logger_level)

	fh = logging.FileHandler(os.path.join(savepath, log_filename), mode='a')
	#fh.setLevel(logging.DEBUG)

	info_format = '%(asctime)s line%(lineno)d %(levelname)s: %(message)s'
	formatter = logging.Formatter(
								  fmt=info_format,
								  datefmt='%Y/%m/%d %H:%M:%S',
								 )

	fh.setFormatter(formatter)

	logger.addHandler(fh)

	return logger


def main(logger, savepath):
	'''
	Collects the scraping results of different spyder scripts and saves their joint output to an
	Excel file.	Takes the following arguments:

	logger 	  	  (logger.log): a logger object created by the set_custom_logger function.
	savepath      (str): path where we want to save our price data in.
	'''

	logger.info('Prcoess Start')
	
	try:
		logger.info("Spyder 1 start")
		start_time1 = time.time()
		game_list, table1 = spyder1.get_prices()
		end_time1 = time.time()
		duration1 = end_time1 - start_time1
		if duration1 >= 60:
			logger.info("Spyder 1 end: duration = " + str(int((end_time1 - start_time1) / 60)) + " minutes")
		else:
			logger.info("Spyder 1 end: duration = " + str(int(end_time1 - start_time1)) + " seconds")
	except Exception as e:
		logger.error("Process Interrupted:\n", e)

	try:
		logger.info("Spyder 2 start")
		start_time2 = time.time()
		table2 = spyder2.get_prices(game_list)
		end_time2 = time.time()
		duration2 = end_time2 - start_time2
		if duration2 >= 60:
			logger.info("Spyder 2 end: duration = " + str(int((end_time2 - start_time2) / 60)) + " minutes")
		else:
			logger.info("Spyder 2 end: duration = " + str(int(end_time2 - start_time2)) + " seconds")
	except Exception as e:
		logger.error("Process Interrupted:\n", e)

	try:
		logger.info("Spyder 3 start")
		start_time3 = time.time()
		table3 = spyder3.get_prices(game_list)
		end_time3 = time.time()
		duration3 = end_time3 - start_time3
		if duration3 >= 60:
			logger.info("Spyder 3 end: duration = " + str(int((end_time3 - start_time3) / 60)) + " minutes")
		else:
			logger.info("Spyder 3 end: duration = " + str(int(end_time3 - start_time3)) + " seconds")
	except Exception as e:
		logger.error("Process Interrupted:\n", e)

	try:
		logger.info("Tables Merge Start")
		temp_merge1 = table1.merge(table2, on='names', how='left')
		full_table = temp_merge1.merge(table3, on='name', how='left')
		logger.info("Tables Merge Complete")
	except Exception as e:
		logger.error("Process Interrupted:\n", e)

	try:
		logger.info("Save File Folder Creation Start")
		today = dt.datetime.today()
		year_folder = os.path.join(savepath, today.strftime('%Y') + '_prices')
		if not os.path.isdir(year_folder):
			try:
				os.mkdir(year_folder)
				print('Folder created!')
			except OSError:
				print('Folder already exists!')
		logger.info("Save File Folder Creation Complete")
	except Exception as e:
		logger.error("Process Interrupted:\n", e)

	try:
		logger.info("Data Write Start")
		filename = os.path.join(savepath, os.path.basename(year_folder), today.strftime('%B') + '.xlsx')
		if not os.path.isfile(filename):
			full_table.to_excel(
								filename,
								index=False,
								sheet_name=today.strftime("%Y-%m-%d"),
								na_rep='NaN',
								)
		else:
			with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
				full_table.to_excel(
									writer,
									index=False,
									sheet_name=today.strftime("%Y-%m-%d"),
									na_rep='NaN',
									)
		logger.info("Data Write Complete")
	except Exception as e:
		logger.error("Process Interrupted:\n", e)


if __name__ == '__main__':

	savepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'data')

	process_logger = set_custom_logger(
									   logger_level=logging.DEBUG,
									   savepath=os.path.join(os.path.dirname(savepath), 'logs'),
									   log_filename='process.log',
									)

	main(process_logger, savepath)
