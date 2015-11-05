from xml.dom import minidom
import xml.parsers.expat
import urllib



def main():
	url_str = 'https://www.google.com/sitemap.xml'
	config_page = 5
	flag = 0
	
	try:
		XML_Parser(url_str, config_page)
	except xml.parsers.expat.ExpatError:
                flag = 1
	
	if flag:
		Scrappy()


def XML_Parser(url_str, config_page):
	print "Inside XML_Parser func."
	xml_str = urllib.urlopen(url_str).read()
	xmldoc = minidom.parseString(xml_str)

	tag_values = xmldoc.getElementsByTagName('loc')

	len_tag_values = len(tag_values)

	print len_tag_values
	
	config_page = min(len_tag_values, config_page)

	print config_page

	for tag_val in tag_values[:config_page]:
	    print tag_val.firstChild.nodeValue

	

def Scrappy():
	print "Invlaid site address. Called Scrappy."

main()
