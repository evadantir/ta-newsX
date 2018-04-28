module.exports = {
	dumpJSON, logger, sleep
};

function dumpJSON(object){
	console.log(JSON.stringify(object, null, 2));
}

// buat debug biar ketahuan berapa lama proses berlangsung
function logger(message){
	if (typeof message == "string"){
		console.log(new Date().toLocaleString(), message);
	} else {
		console.log(new Date().toLocaleString());
		dumpJSON(message);
	}
}

// biar ga kedetect sebagai bot (kadang server bisa ngedeteksi kita bot atau bukan), biar requestnya ga terlalu cepet
function sleep(time){
	return new Promise(resolve => setTimeout(resolve, time));
}
