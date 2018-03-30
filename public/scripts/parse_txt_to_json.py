#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys
import json
import logging
import subprocess

###############################################################################################################
# 2018.03.20
# Gavin Luo
#
# This script is used to convert a folder of text files to a folder of json files.
# You can use the script like this:
#   $ python parse_txt_to_json.py [INPUT FOLDER PATH] [OUTPUT FOLDER PATH]
# Before you use this script, please make sure that the text file has the following format:
#   1 line - Category.
#   2 line - Title of the article. 
#   3 line - Author of the article.
#   >3 line - Content of the article.
# if one article doesn't have category or title or author, do leave a blank line.
#
###############################################################################################################

# GenerateJsonFile
#   This function takes in a text file path and generate a json file that contains all the information about this file.
# Parameters:
#   filename - text file path
#   inputPath - the location of the text file, no trailing slash please.
#   outputPath - destination of the output json file, no trailing slash please.
# Output:
#   Create a Json file with the same name and save it in the provided directory. 
def GenerateJsonFile(filename, inputPath, outputPath):
    filenameWithoutExtension = filename[:len(filename)-4]

    originalFile = open(inputPath + "/" + filename, "r")

    outputFile = open(outputPath + "/" + filenameWithoutExtension + ".json", "w")

    text = []

    text.append("{")
    text.append("   \"id\": \"" + filenameWithoutExtension + "\",")

    theme = originalFile.readline()
    if theme:
        theme = theme.rstrip()
        text.append("   \"category\": \"" + theme + "\",")

    title = originalFile.readline()
    if title :
        title = title.rstrip()
        text.append("   \"title\": \"" + title + "\",")

    author = originalFile.readline()
    if author :
        author = author.rstrip()
        text.append("   \"author\": \"" + author + "\",")

    line = originalFile.readline()
    if line:
        text.append("   \"content\": [")
        while line:
            line = line.rstrip()
            content_line = "       \"" + line + "\""
            line = originalFile.readline()
            if line:
                content_line += ","
            text.append(content_line)

        text.append("   ]")
    text.append("}")

    for i in range(0, len(text)):
        text[i] = text[i] + "\n"

    outputFile.writelines(text)

    originalFile.close()
    outputFile.close()


# GenerateTableOfContent
# This function is used for generating a json file that contains the table of contents for the current folder.
# This file will open all .json files in the current folder, assuming that each .json file is a content file containing an article that is consisted
# with the following keys:
# - category
# - title
# - author
# - content
# i.e.:
# {
#   "category" : "YOUR CATEGORY HERE",
#   "title"    : "YOUR TITLE HERE",
#   "author"   : "YOUR AUTHOR HERE",
#   "content"  : ["YOUR ARTICLE CONTENT", "YOUR ARTICLE CONTENT", "YOUR ARTICLE CONTENT"]
# }
#
def GenerateTableOfContent(filenames, inputPath, outputPath):

    # main json object
    main_json_obj = {"table_of_content":[]}

    for one_file_name in filenames:
        with open(inputPath + "/" + one_file_name, 'r') as content_file:
            article_detail = {}

            category = content_file.readline()
            title = content_file.readline()
            author = content_file.readline()

            if category:
                category = category.rstrip()

            article_detail["title"] = ""
            if title:
                title = title.rstrip()
                article_detail["title"] = title

            article_detail["author"] = ""
            if author:
                author = author.rstrip()
                article_detail["author"] = author

            article_detail["id"] = one_file_name[:len(one_file_name)-4];
            article_detail["file"] = one_file_name[:len(one_file_name)-4] + ".json";

            need_new_category = True
            for each_category in main_json_obj["table_of_content"]:
                if (category and each_category["category"] == category) or (not category and each_category["category"] == ""):
                    each_category["articles"].append(article_detail)
                    need_new_category = False

            if need_new_category :
                if category:
                    main_json_obj["table_of_content"].append({"category":category, "articles":[article_detail]})
                else:
                    main_json_obj["table_of_content"].append({"category":"", "articles":[article_detail]})


    with open(outputPath + "/table_of_content.json", 'w') as output_file:
        text = []
        text.append("{")
        text.append("   \"table_of_content\":[")
        category_objects = main_json_obj["table_of_content"];
        for cat in range(0, len(category_objects)):
            category = category_objects[cat]
            text.append("       {")
            text.append("           \"category\":\"" + category["category"] + "\",")
            text.append("           \"articles\":[")
            for art in range(0, len(category["articles"])):
                article = category["articles"][art]
                text.append("               {")
                text.append("                   \"title\":\"" + article["title"] + "\",")
                text.append("                   \"author\":\"" + article["author"] + "\",")
                text.append("                   \"id\":\"" + article["id"] + "\",")
                text.append("                   \"file\":\"" + article["file"] + "\"")
                text.append("               }")
                if art != len(category["articles"]) - 1:
                    text.append("               ,")

            text.append("           ]")
            text.append("       }")
            if cat != len(category_objects) - 1:
                text.append("       ,") 

        text.append("   ]")
        text.append("}")

        for i in range(0, len(text)):
            text[i] = text[i] + "\n"

        #print(text)

        output_file.writelines(text);

def main():
    # create logger.
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    inputPath = "."
    outputPath = "."
    if len(sys.argv) > 1:
        inputPath = sys.argv[1]

    if not os.path.exists(inputPath) :
        logger.info("Error: " + inputPath + " does not exist.")

    if len(sys.argv) > 2:
        outputPath = sys.argv[2]

    if not os.path.exists(outputPath) :
        logger.info("Error: " + outputPath + " does not exist.")

    files = os.listdir(inputPath)

    textFiles = []

    for oneFile in files:
        if oneFile.endswith(".txt") and oneFile != "List.txt" :
            GenerateJsonFile(oneFile, inputPath, outputPath)
            textFiles.append(oneFile)
            logger.info(oneFile)

    GenerateTableOfContent(textFiles, inputPath, outputPath)

main()