# -*- coding: utf-8 -*-
ESCAPIST_URL = 'http://www.escapistmagazine.com'
ESCAPIST_GALERIES =  '%s/videos/galleries' % ESCAPIST_URL
ESCAPIST_HIGHLIGHTS = '%s/ajax/videos_index.php?videos_type=%%s' % ESCAPIST_URL

####################################################################################################
def Start():

	ObjectContainer.title1 = 'The Escapist'
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0'

####################################################################################################
@handler('/video/escapist', 'The Escapist')
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(
		key = Callback(HighlightBrowser, title='Most Recent', mode='latest'),
		title = 'Most Recent'
	))

	oc.add(DirectoryObject(
		key = Callback(HighlightBrowser, title='Most Viewed', mode='popular'),
		title = 'Most Viewed'
	))

	for show in HTML.ElementFromURL(ESCAPIST_GALERIES).xpath('//div[@id="gallery_index_display"]/div[contains(@class, "folders_container")]'):
		title = show.xpath('./a[@class="feedicon"]/@title')[0].split(' : ')[0]
		url = show.xpath('./div[@class="folders_title_card"]/a/@href')[0].rstrip('/')
		summary = show.xpath('./div[@class="article_links_container"]/p//text()')
		summary = ''.join(summary)

		try: thumb = show.xpath('.//a/img/@src')[0]
		except: thumb = ''

		oc.add(DirectoryObject(
			key = Callback(ShowBrowser, show_url=url, show_name=title, show_thumb=thumb),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb)
		))

	return oc

####################################################################################################
@route('/video/escapist/show', page_num=int)
def ShowBrowser(show_url, show_name, show_thumb, page_num=1):

	oc = ObjectContainer(title2=show_name)

	if page_num > 1:
		page_url = "%s?page=%d" % (show_url, page_num)
	else:
		page_url = show_url

	html = HTML.ElementFromURL(page_url)

	for episode in html.xpath('//div[@class="video"]//div[@id="gallery_display"]//div[@class="filmstrip_video"]'):
		title = episode.xpath('.//div[@class="title"]//text()')[0]
		date = episode.xpath('.//div[@class="date"]/text()')[0].strip('Date:').strip()
		date = Datetime.ParseDate(date)
		thumb = episode.xpath('.//img/@src')[0]
		url = episode.xpath('.//a/@href')[0]

		if url[0:4] != 'http':
			url = ESCAPIST_URL + url

		oc.add(VideoClipObject(
			url = url,
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(thumb),
			originally_available_at = date
		))

	# Check for a next page link
	if len(html.xpath('//a[@class="next_page"]')) > 0:
		oc.add(NextPageObject(
			key = Callback(ShowBrowser, show_url=show_url, show_name=show_name, show_thumb=show_thumb, page_num=page_num+1),
			title = 'Next Page...'
		))

	return oc

####################################################################################################
@route('/video/escapist/highlights')
def HighlightBrowser(title, mode):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(ESCAPIST_HIGHLIGHTS % mode)

	for episode in html.xpath('//div[@class="filmstrip_video"]'):
		title = episode.xpath('.//div[@class="title"]//text()')[0]
		date = episode.xpath('.//div[@class="date"]/text()')[0].strip('Date:').strip()
		date = Datetime.ParseDate(date)
		url = episode.xpath('.//a/@href')[0]
		thumb = episode.xpath('.//img/@src')[0]

		if url[0:4] != 'http':
			url = ESCAPIST_URL + url

		oc.add(VideoClipObject(
			url = url,
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(thumb),
			originally_available_at = date
		))

	return oc
