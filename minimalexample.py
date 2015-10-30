# Minimal example.py
# Had to change imports a little :3 It hurt my eyes :P
from json import loads
from time import strptime, localtime

if __import__('sys').version_info[0] == 2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

todayEvents = []
# Can't post links on HF, so I had to get creative. :P
req = urlopen("http ://adigov. stud.if .ktu.lt/wordpress/?json=1".replace(' ', ''))
content = req.read().decode("utf-8")
jsonObj = loads(content)

if jsonObj["status"] and jsonObj["status"] == "ok":
    posts = jsonObj["posts"]
    if posts:
        for post in posts:
            if post["categories"] and len(post["categories"]) > 0:
                category = post["categories"][0]
                parseTime = strptime(category["title"], "%m/%d/%Y")
                today = localtime()

                # Far shorter. :P
                if parseTime[:3] == today[:3]:
                    todayEvents.append(post["title"])

print(todayEvents) 
