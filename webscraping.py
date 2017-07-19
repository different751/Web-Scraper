import os
import sys
from bs4 import BeautifulSoup
from lxml import etree, objectify
import requests
import re #using this for regular expressions

#concat action for search url
def setAction(whatAction):
	return 'action='+whatAction+'&'

#concat format for search url
def setFormat(whatFormat):
	return 'format='+whatFormat+'&'

#concast search in search url and add search limit
def searchFor(searchTerms, limit):
	return 'search='+searchTerms+'&limit='+limit+'&'

#concat titles to search url using the given titles
def titles(whatTitles):
	listOfTitles = ''
	for title in whatTitles:
		listOfTitles += title+"_"
	return 'titles='+listOfTitles[:-1]

#concat prop for search ulr
def setProps(whatProp):
	return 'prop='+whatProp+'&'

#get web page
def getPage(url):
	page = requests.get(url)
	return page

#begin to set up search url for link
def searchWikiURL(wikiURL, searchTerms, limit):
	return wikiURL+setAction('opensearch')+setFormat('xml')+searchFor(searchTerms, limit)

#begin to set up query url for link
def queryWikiURL(wikiURL, queryTerms):
	return wikiURL+setAction('query')+setProps('extracts')+setFormat('xml')+titles(queryTerms)
	
#unused method	
#def pp(e):
   #print etree.tostring(e, pretty_print=True)
    #print ''

#make xml tree for use
def strip_ns(tree):
    for node in tree.iter():
        try:
            has_namespace = node.tag.startswith('{')
        except AttributeError:
            continue
        if has_namespace:
            node.tag = node.tag.split('}', 1)[1]

#method to get description from websites
def getdes(website):
	rawSite = getPage(website) #grab page details
	otherRoot = etree.fromstring(rawSite.content) #make tree from site
	strip_ns(otherRoot) #make xml tree ready to use
	#xpath to the description text in the xml
	des = otherRoot.xpath('/SearchSuggestion/Section/Item/Description/text()')
	#dirtyDes = re.findall(r"<p>(.*)<\/p>", des[0])
	#print des
	if des != []: #if to check for empty return
		parseDes = BeautifulSoup(des[0], "lxml").text #print correct html
		cleanDes = re.sub(r"\/(.*)\/",'',parseDes) #parse unneeded chars
		return cleanDes
	else:
		return 'There is no description for this object'

#method to get image url from websites
def getimage(website):
	rawSite = getPage(website) #get content from site
	otherRoot = etree.fromstring(rawSite.content) # make tree from site
	strip_ns(otherRoot) #make tree for use
	#use xpath to return image url
	imag = otherRoot.xpath('/SearchSuggestion/Section/Item/Image/@source')
	if imag == []:#check if image is empty or not
		return 'There is no image link for this object'
	else:
		return imag[0]
#method to get real url
def getwikiurl(website):
	rawSite = getPage(website) #get website content
	otherRoot = etree.fromstring(rawSite.content) # make tree from site
	strip_ns(otherRoot) # make tree for use
	#use expath to get url from xml
	des = otherRoot.xpath('/SearchSuggestion/Section/Item/Url/text()')
	return des[0]	
	
	
def main():
	wiki = "https://en.wikipedia.org/w/api.php?" #first part of wiki api
	tutorial = 'http://econpy.pythonanywhere.com/ex/001.html'
	print "\n"
	print "This web scrapper will scrape Wiki Pages looking for dinosaurs "
	print "and related images and discriptions for each dinosaur\n"
	#wikiURL = searchWikiURL(wiki, 'Computer', '5')
	#start the scrape by looking for list in a query search
	wikiURL = queryWikiURL(wiki, ['List', 'of', 'dinosaur', 'genera'])	
	print "Origin link for scrape: "
	print wikiURL #print the link that was used for list search
	print "\n"
	print "Creating XML please wait...\n\n"

	rawPage = getPage(wikiURL)#get content from site
	
	root = etree.fromstring(rawPage.content) #make tree from site

	strip_ns(root)#make tree for use

	#test and example links
	#https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=xml&titles=Scott%20Aaronson
	#https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=xml&titles=List%20of%20computer%20scientists
	#https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=xml&titles=List_of_dinosaur_genera
	#https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=xml&titles=List_of_dinosaur_genera
	#https://en.wikipedia.org/w/api.php?action=query&format=xml&titles=List_of_dinosaur_genera
	#https://en.wikipedia.org/w/api.php?action=opensearch&format=xml&search=Computer&limit=5&
	
	#use xpath to get al lthe text from the site
	urls = root.xpath('/api/query/pages/page/extract/text()')
	
	#parse for links useing findall save into list
	linklist = re.findall(r"<li><i>(.*)<\/i><\/li>", urls[0])

	#set base of xml to root
	base = etree.Element('root')	

	for i in range(0,50):#foor loop to begin parsing and making xml
		Dinosaur = etree.Element('Dinosaur') #make element Dino
		Dinosaur.set("ID",str(i)) #set attribute for Dino
		#name = etree.Element('Name') #make element name
		discription = etree.Element('Discription') #make element Dis
		dinolink = etree.Element('Url') #make element url
		dinoimage = etree.Element('Image') #make element Image
		#clean names that were returned for used in links
		cleanName = re.sub(r"<\/i>(.*)","",linklist[i])		
		#name.text = cleanName #set text for element name
		Dinosaur.set("Name",cleanName)#decided to make name an attribute instead
		#search pages of names of elements
		weblink = searchWikiURL(wiki, cleanName, '1')
		discription.text = getdes(weblink) #get discription from site set text
		dinolink.text =  getwikiurl(weblink) #get link from site set text
		dinoimage.text = getimage(weblink) #get image from site set text
		base.append(Dinosaur) #add dino to tree append to base
		#Dinosaur.append(name) #add name to tree append to dino
		Dinosaur.append(discription) #add des to tree append to dino
		Dinosaur.append(dinolink) #add link to tree append to dino
		Dinosaur.append(dinoimage) #add image to tree append to dino
				
	#make xml tree to string for printing
	s = etree.tostring(base,pretty_print=True)
	newvari = re.sub(r'amp;', '', s) #clean xml tree fixing links
	cleanVari = re.sub(r'&(.*?);',"",newvari)#clean xml tree fixing broken chars
	FILE = open("output.xml", "wb")#make xml file
	FILE.write(cleanVari)#write to xml file
	FILE.close()#close xml file
	print "XML created --- Program Finished\n"




if __name__ == '__main__':
	main()
