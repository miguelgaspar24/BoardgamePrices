#!/usr/bin/env python
# coding: utf-8

import datetime as dt
import logging
import os
import sys

import pandas as pd

import jogonamesa_spyder as spyder1
import gameplay_spyder as spyder2


savepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'data')


def set_custom_logger(logger_level, savepath, log_filename):

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


def main(custom_logger):

	game_list, table1 = spyder1.get_prices()
	table2 = spyder2.get_prices(game_list)

	full_table = table1.merge(table2, on='name')

	today = dt.datetime.today()
	custom_logger.info('Todays menu, in separate main functions: ' + today.strftime("%Y-%m-%d %H:%M"))

	year_folder = os.path.join(savepath, today.strftime('%Y') + '_prices')
	if not os.path.isdir(year_folder):
	    try:
	        os.mkdir(year_folder)
	        print('Folder created!')
	    except OSError:
	        print('Folder already exists!')

	filename = os.path.join(savepath, os.path.basename(year_folder), today.strftime('%B') + '.xlsx')
	if not os.path.isfile(filename):
	    full_table.to_excel(
		    	            filename,
		    	            index=False,
		    	            sheet_name=today.strftime("%Y-%m-%d"),
		    	            na_rep='NaN',
		    	           )
	else:
	    with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
	        full_table.to_excel(
		        	            writer,
		        	            index=False,
		        	            sheet_name=today.strftime("%Y-%m-%d"),
		        	            na_rep='NaN',
		        	           )

if __name__ == '__main__':

	custom_logger = set_custom_logger(
		                              logger_level=logging.DEBUG,
		                              savepath=os.path.join(os.path.dirname(savepath), 'logs'),
		                              log_filename='jogonamesa.log',
		                             )

	main(custom_logger)
