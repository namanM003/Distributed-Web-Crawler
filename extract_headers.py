#Code to extract headers from HTTP Response

import http.client

url = "www.google.com"

conn = http.client.HTTPConnection(url)

conn.request("HEAD", "/index.html")

res = conn.getresponse()

print(res.getheaders())
