//this script is created by imamfzn

const fs = require('fs');
const lib = require('./lib');
const request = require('request');
const argv = require('minimist')(process.argv.slice(2));

start();

async function start(){
	const path = `${__dirname}/page_links.json`;
	// parse JSON string into an object
	const contentURLs = JSON.parse(fs.readFileSync(path));
	const startNumOfURL = argv.start || 0;
	const endNumOfURL = argv.end || contentURLs.length;

	// looping, get every content in extractedlink
	for (let i = startNumOfURL ; i < endNumOfURL ; i++){
		lib.logger(`request to ${contentURLs[i]}`);
	
		const pageContent = await getPageContent(contentURLs[i]);

		savePageContentToFile(i+1, pageContent);
		lib.sleep(1000);
	}
}

// get page content from link that has been extracted from every index page
function getPageContent(contentURL){
	return new Promise(function (resolve, reject){
		// visit page from extracted link with request function	
		request(contentURL, function (error, response, body){
			if (error){
				reject(error);
			} else if (response && response.statusCode !== 200){
				reject(response.statusCode);
			} else {
				resolve(body);
			}
		});
	});
}

// scraping HTML content from each page to file .HTML
function savePageContentToFile(numOfContent, pageContent){
	const path = `${__dirname}/page_contents_raw/page_content_${numOfContent}.html`;

	fs.writeFileSync(path, pageContent);
}