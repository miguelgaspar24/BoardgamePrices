
import datetime as dt
import logging
import os
import sys

import pandas as pd

import jogonamesa_spyder as spyder1
import gameplay_spyder as spyder2


def set_custom_logger(logger_level, savepath, log_filename):
	'''
	Creates a custom logger. Takes the following parameters:

	logger_level (logging.LEVEL): logging level.
	savepath     (str): path to where to save the logger output.
	log_filename (str): name of the saved logger.

	Returns a logger object with its associated handler and formatter.
	'''

	logger = logging.getLogger('my_logger')
	logger.setLevel(logger_level)

	fh = logging.FileHandler(os.path.join(savepath, log_filename), mode='a')
	fh.setLevel(logging.DEBUG)

	info_format = '%(asctime)s line%(lineno)d %(levelname)s: %(message)s'
	formatter = logging.Formatter(
								  fmt=info_format,
								  datefmt='%Y/%m/%d %H:%M:%S',
								 )

	fh.setFormatter(formatter)

	logger.addHandler(fh)

	return logger


def main(custom_logger, savepath):
	'''
	Collects the scraping results of different spyder scripts and saves their joint output to an
	Excel file.	Takes the following arguments:

	custom_logger (logger object): a logger object created by the above set_custom_logger function.
	savepath      (str): path where we want to save our price data in.
	'''

	game_list, table1 = spyder1.get_prices()
	table2 = spyder2.get_prices(game_list)

	full_table = table1.merge(table2, on='name')

	today = dt.datetime.today()
	custom_logger.info("Today's menu, in separate main functions: " + today.strftime("%Y-%m-%d %H:%M"))

	year_folder = os.path.join(savepath, today.strftime('%Y') + '_prices')
	if not os.path.isdir(year_folder):
		try:
			os.mkdir(year_folder)
			print('Folder created!')
		except OSError:
			print('Folder already exists!')

	filename = os.path.join(savepath, os.path.basename(year_folder), today.strftime('%B') + '.xlsx')
	if not os.path.isfile(filename):
		print('This one')
		full_table.to_excel(
							filename,
							index=False,
							sheet_name=today.strftime("%Y-%m-%d"),
							na_rep='NaN',
							)
	else:
		print('That')
		with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
			full_table.to_excel(
								writer,
								index=False,
								sheet_name=today.strftime("%Y-%m-%d"),
								na_rep='NaN',
								)


if __name__ == '__main__':

	savepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'data')

	custom_logger = set_custom_logger(
									  logger_level=logging.DEBUG,
									  savepath=os.path.join(os.path.dirname(savepath), 'logs'),
									  log_filename='jogonamesa.log',
									 )

	main(custom_logger, savepath)
