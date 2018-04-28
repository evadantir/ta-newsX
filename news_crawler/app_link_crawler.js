//this script is created by imamfzn

const fs = require('fs');
const lib = require('./lib');
// request buat mengunjungi halaman
const request = require('request');
// ngubah string HTML jadi objek HTML yang bisa diakses (DOM)
const cheerio = require('cheerio');
// get sent argument from console
const argv = require('minimist')(process.argv.slice(2));
const URL = "http://www.thejakartapost.com/news/index/page";

// main function called start
async function start(){
	const startPage = argv.start || 1; //1 is default if there's no argument inputted
	const endPage = argv.end || 50;

	// print status of the crawler
	lib.logger('starting page link crawler from jakarta post index pages...');

	// looping to crawl page, start from the page 1 to latest page (50)
	for (let page = startPage ; page <= endPage ; page++){
		// print status of the crawler
		lib.logger(`request page to ${URL}/${page}`);
		// get index pages
		const pageResponse = await getIndexPage(page);
		// extract link from index page
		const links = extractLink(pageResponse);

		// after link extracted, save link to a file
		savePageLinkToFile(page, links);

		// sleep for 1 sec, bagusnya dirandom
		await lib.sleep(1000);
	}

	// print status
	lib.logger(`${URL} from page ${startPage} to ${endPage} has been crawled`);
}

function getIndexPage(page){
	// Promise structure is used so it can be arranged synchronuously
	return new Promise(function (resolve, reject){
		const indexURL = `${URL}/${page}`;
		// call request function but using Promise structure
		request(indexURL, function (error, response, body){
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

function extractLink(pageResponse){
	// dinamain $ biar mirip jQuery -- syntatic sugar
	// $  = object DOM
	const $ = cheerio.load(pageResponse);
	const selector = '.tjp-latest-entry .detail-latest > a > h5';
	// mundur ke atas buat nyari elemen <a href> terdekat dari h5 (parent a)
	const links = $(selector).map(function (){ return $(this).closest('a').attr('href');}).get(); //habis ada map langsung get di cheerio

	//array of links yang sudah didapat
	return links;
}

function savePageLinkToFile(page, links){
	const path = `${__dirname}/page_links/page_links_${page}.json`;
	// json standar file yang universal
	// json stringify mengubah object jadi string, (data, (null,2) untuk formating)
	const file = JSON.stringify(links, null, 2);

	// fs lib node.js buat access io
	fs.writeFileSync(path, file); // write file secara sync
}

start();