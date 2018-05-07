//this script is created by imamfzn
/*
merging link from every page index
link must be merged to check if there's any link that's duplicate and easeness on getting HTML content from every extracted link
*/

const fs = require('fs');

start();

function start(){
	const path = `${__dirname}/page_contents_extracted/`;
	const pageLinksFileName = fs.readdirSync(path);
	const pageLinks = [...new Set([].concat(...pageLinksFileName.map(getPageLinks)))];

	savePageLinksToFile(pageLinks);
}


function savePageLinksToFile(pageLinks){
	const path = `${__dirname}/page_contents.json`;
	const file = JSON.stringify(pageLinks, null, 2);

	fs.writeFileSync(path, file);
}


function getPageLinks(fileName){
	const path = `${__dirname}/page_contents_extracted/${fileName}`;

	return JSON.parse(fs.readFileSync(path));
}