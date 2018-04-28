const cheerio = require('cheerio');
const fs = require('fs');
const lib = require('./lib');

start();

function start(){
	const path = `${__dirname}/page_contents_raw`;
	const rawContentsFileName = fs.readdirSync(path);

	lib.logger('extracting raw content ...');
	for (const fileName of rawContentsFileName){
		const pageContent = fs.readFileSync(`${path}/${fileName}`).toString();
		const content = extractContent(pageContent);

		saveContentToFile(fileName, content);
	}

	lib.logger('all raw content has been extracted');
}

function extractContent(page){
	const $ = cheerio.load(page);
	// define CSS selector from content that want to be selected
	const selector = {
		link: 'meta[property="og:url"]',
		title: 'meta[property="og:title"]',
		date: '.post-like > .posting',
		category: '.breadcrumbs > li:nth-child(1) > a',
		sub_category: '.breadcrumbs > li:nth-child(2) > a',
		body: '.show-define-text > p'
	};

	const link = $(selector.link).attr('content');
	const title = $(selector.title).attr('content');
	//replace di JS harus pakai regex (g)
	const date = $(selector.date).text().trim().replace(/\n/g, ' ').replace(/\s\s+/g, ' ').split(' | ').slice(1).join(' '); // mastiin dalam satu string ada satu spasi (\s\s)
	//slice : motong suatu string berdasarkan suatu karakter sebanyak n kali
	const category = $(selector.category).text().trim();//trim buat ngehapus \n
	const sub_category = $(selector.sub_category).text().trim();
	const body = $(selector.body).map(function () { return $(this).text().trim(); }).get().filter(isCleanFromLinkingArticle).join(' ');

	return {
		title,link, date, category, sub_category, body
	};
}

function saveContentToFile(fileName, content){
	const path = `${__dirname}/page_contents_extracted/${fileName.replace(/.html/g, '.json')}`;
	const file = JSON.stringify(content, null, 2);

	fs.writeFileSync(path, file);
}

// filtering news content from links or HTML attribute
function isCleanFromLinkingArticle(text){
	return !(text.includes('Read More:') || text.includes('Read Also') || text.includes('Read also') || text.includes('<img src'));
}