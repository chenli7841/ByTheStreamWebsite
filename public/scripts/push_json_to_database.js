////////////////////////////////////////////////////////////////////////////////////////////////////
//
// This script addes all the article json files to mongodb data base.
// Date created: 2018/3/31
// Author: Gavin Luo
//
////////////////////////////////////////////////////////////////////////////////////////////////////

var url = "mongodb+srv://sx2gavin:glXishuipang@xishuipang-db-qo1sq.mongodb.net/"
// var url = "mongodb://127.0.0.1:27017/" // Remember to change this url for the production database.
var mongo = require('mongodb');
var MongoClient = require('mongodb').MongoClient;
var fs = require('fs');
var path = require('path');

// command line arguments
var numArgs = process.argv.length;

// volume
var volume = 0;
if (numArgs >= 3) {
	volume = process.argv[2];
}
else {
	console.error("Error: volume number is not provided in the command line.");
	process.exit(1);
}

var volumeDirectory = "../content/volume_" + volume;

MongoClient.connect(url, function(err, db) {
	if (err) {
		throw err;
	}
	var xishuipangDb = db.db("Xishuipang");

	// go to the volume folder and load each file.
	fs.readdir(volumeDirectory, function(err, files) {
		if (err) {
			console.error("Error: " + volumeDirectory + " doesn't exist. Please make sure that the volume data is available.");
			throw err;
		}
		console.log("In " + volumeDirectory + "...");
		var pending = files.length;
		for (i in files) {
			var filename = files[i];
			var fullFilePath = volumeDirectory + "/" + filename;

			if (filename == "table_of_content.json") {
				// read the table of content file and add it to the database.
				fs.readFile(fullFilePath, function(err, data) {
					if (err) {
						console.error("Error: " + fullFilePath + " doesn't exist or cannot be read.");
						throw err;
					}
					var jsonObj = JSON.parse(data);
					var volumeNum = jsonObj.volume;

					// either insert a new article or update the current one.
					xishuipangDb.collection("TableOfContents").updateOne({volume:volumeNum}, {$set: jsonObj}, {upsert: true}, function(err, res) {
						if (err) {
							throw err;
						}
						console.log("Table of content added.");
						pending--;
						if (pending == 0)
						{
							db.close();
						}
					});
				});
			} else if (path.extname(filename) == ".json") {

				// read the file and add it to the database.
				fs.readFile(fullFilePath, function(err, data) {
					if (err) {
						console.error("Error: " + fullFilePath + " doesn't exist or cannot be read.");
						throw err;
					}
					var jsonObj = JSON.parse(data);
					var articleId = jsonObj.id;
					var volumeNum = jsonObj.volume;

					// either insert a new article or update the current one.
					xishuipangDb.collection("Articles").updateOne({volume:volumeNum,id:articleId}, {$set: jsonObj}, {upsert: true}, function(err, res) {
						if (err) {
							throw err;
						}
						console.log(articleId + " added.");
						pending--;
						if (pending == 0)
						{
							db.close();
						}
					});
				});
			}
		}
	});

	console.log("Xishuipang database connected!");
});