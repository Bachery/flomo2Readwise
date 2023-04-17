import os
from datetime import datetime
from flomoDatabase import FlomoDatabase
from readwise import Readwise
from logger import loguru_logger

Notion_Integration_Token	= os.environ['NOTION_INTEGRATION_TOKEN']
Notion_Database_ID			= os.environ['NOTION_DATABASE_ID']
Readwise_Access_Token		= os.environ['READWISE_ACCESS_TOKEN']

# Only sync new memos by managing a last sync time
last_sync_time_file = 'last_sync_time.txt'
# Save all logs to a same file
logger = loguru_logger('flomo2readwise')

def get_last_sync_time():
	if not os.path.exists(last_sync_time_file):
		return None
	with open(last_sync_time_file, 'r') as f:
		return datetime.fromisoformat(f.read())

def update_last_sync_time():
	update_time = datetime.now()
	with open(last_sync_time_file, 'w') as f:
		f.write(str(update_time))
	return update_time

def sync_flomo_to_readwise():
	# Get last sync time
	last_sync_time = get_last_sync_time()
	if last_sync_time:
		logger.log('Last sync time:', last_sync_time)
	else:
		logger.log('First sync')

	# Fetch flomo memos
	try:
		flomo_database = FlomoDatabase(Notion_Integration_Token, Notion_Database_ID, logger)
		flomo_memos = flomo_database.fetch_flomo_memos(last_sync_time=last_sync_time)
		logger.log('Number of flomo memos to sync:', len(flomo_memos))
	except Exception as e:
		logger.log('Failed to fetch flomo memos')
		logger.log(e)
		return

	# Sync flomo memos to Readwise
	try:
		readwise = Readwise(Readwise_Access_Token, logger)
		readwise.create_highlights_from_memos(flomo_memos)
	except Exception as e:
		logger.log('Failed to sync flomo memos to Readwise')
		logger.log(e)
		return

	# Update last sync time
	update_time = update_last_sync_time()
	logger.log('Update last sync time:', update_time)
	logger.log('Finished')
	logger.log('')

if __name__ == '__main__':
	sync_flomo_to_readwise()
