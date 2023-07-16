from notion_client import Client
from datetime import datetime
from tenacity import retry, wait_exponential, stop_after_attempt

class FlomoDatabase:
	def __init__(self, api_key, database_id, logger, update_tags=True, skip_tags=['', 'welcome']):
		self.notion = Client(auth=api_key)
		self.database_id = database_id
		self.logger = logger
		self.update_tags = update_tags
		self.skip_tags = skip_tags
		self.logger.log('1')

	@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
	def fetch_flomo_memos(self, last_sync_time=None):
		self.logger.log('2')
		all_memos = []
		## get 100 pages at a time
		result_list = self.notion.databases.query(self.database_id)
		while result_list:
			## save content of each page
			for page in result_list['results']:
				flomo_memo = self.fetch_flomo_memo(page, last_sync_time=last_sync_time)
				if flomo_memo:
					all_memos.append(flomo_memo)
			self.logger.log('3')
			## get next 100 pages, until no more pages
			if "next_cursor" in result_list and result_list["next_cursor"]:
				result_list = self.notion.databases.query(self.database_id, start_cursor=result_list["next_cursor"])
			else:
				break
		self.logger.log('4')
		return all_memos
	
	@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
	def fetch_flomo_memo(self, page, last_sync_time=None):
		# Skip pages edited before last_sync_time
		last_edit_time_str = page['last_edited_time'] # format: '2023-04-17T00:00:00.000Z' and it's UTC time
		last_edit_time = datetime.strptime(last_edit_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
		if last_sync_time and last_edit_time < last_sync_time:
			return None

		# Get tags, which are separated by slash in flomo
		tags = self.fetch_and_seperate_tags(page)
		for skip_tag in self.skip_tags:
			if skip_tag=='' and len(tags)==0:
				return None
			if skip_tag in tags:
				return None

		# Store seperated tags as a new Multi-select property in Notion
		if self.update_tags:
			self.update_seperated_tags(page, tags)
		
		# Get content text, flomo memo has only one block
		page_blocks = self.notion.blocks.children.list(page['id'])
		text_content = page_blocks['results'][0]['paragraph']['rich_text'][0]['plain_text']
		
		flomo_memo = {
			'tags':			tags,
			'flomo_url':	page['properties']['Link']['url'],
			'edit_time':	last_edit_time_str,
			'text':			text_content
		}

		if "得到" in tags:
			memo = self.parse_dedao_content(tags, text_content)
			flomo_memo.update(memo)
		
		if flomo_memo['text'] == '':
			return None

		return flomo_memo
	
	""" Tools """
	
	def test_connection(self):
		## Need 'Read user information' permission in Notion Integration
		list_users_response = self.notion.users.list()
		self.logger.log(list_users_response)

	def fetch_and_seperate_tags(self, page):
		# Get tags, which are separated by slash in flomo
		tags_property = page['properties']['Tags']['multi_select']
		if len(tags_property) == 0:
			return []
		tags_slashs = [tag['name'] for tag in tags_property]
		tags = []
		for tags_slash in tags_slashs:
			tags += tags_slash.split('/')
		return tags

	def update_seperated_tags(self, page, tags):
		# add new property to the database if not exist
		if 'Seperated Tags' not in page['properties']:
			self.add_multi_select_property('Seperated Tags')
		# update property if not match
		st = page['properties']['Seperated Tags']['multi_select']
		if len(st) != len(tags) or not all([st[i]['name'] == tags[i] for i in range(len(tags))]):
			self.notion.pages.update(page['id'], properties={
				'Seperated Tags': {
					'multi_select': [{'name': tag} for tag in tags]
				}
			})

	def add_multi_select_property(self, property_name, options=[]):
		# Get the database schema
		database = self.notion.databases.retrieve(self.database_id)
		properties = database['properties']
		# Check if the property already exists
		if property_name in properties:
			return
		# Add the property
		properties[property_name] = {
			'type': 'multi_select',
			'multi_select': {
				'options': options
			}
		}
		# Update the database schema
		self.notion.databases.update(self.database_id, properties=properties)
	
	def parse_dedao_content(self, tags, text):
		all_tags = '_'.join(tags)
		# category
		category = None
		if '电子书' in all_tags:	category = 'books'
		elif '课程' in all_tags:	category = 'podcasts'
		elif '其他' in all_tags:	category = 'podcasts'
		elif '城邦' in all_tags:	category = 'tweets'
		# author
		author = None
		author_list = ['万维钢', '卓克', '刘擎', '刘嘉', '何帆', '吴军', '刘润',
						'薛兆丰', '林楚方', '徐弃郁', '施展', '王立铭', '薄世宁',
						'王煜全', '香帅', '冯雪', '贾宁', '李筠', '梁宁', '刘苏里']
		if category == 'podcasts':
			for author_name in author_list:
				if author_name in all_tags:
					author = author_name
					break
		# text
		# remove the first line, which is tags
		# remove the last two lines, which is "来源：https://dedao.cn"
		text = text.split('\n')
		title = text[0].split('/')[-1]
		text = text[1:-2]
		text = '\n'.join(text)
		# return as a dict
		return {
			'text': text,
			'title': title,
			'author': author,
			'category': category
		}
