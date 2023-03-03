import pywikibot
import re
import wikitextparser as wtp

'''
Iterates through every item with an entry in the wikiScrape produced data.
Replaces the {{Gear}} Template with the {{Gear/Automatic}} template.
'''

geartypes = ['Longswords', 'Greatswords', 'Bows', 'Staves', 'Daggers', 'Pickaxes', 'Axes', 'FishingRods', 'FryingPans',
             'Hammers', 'Saws', 'Needles', 'Flasks', 'Head', 'Shields', 'Accessories', 'Body', 'Legs', 'Hand', 'Feet']

catPages = [pywikibot.Page(pywikibot.Site(), f"Module:Gear/{i}/Data") for i in geartypes]
notDone = []
br = False
i = 0
for page in catPages:
    print("Doing " + geartypes[i])
    i += 1
    if br:
        break
    try:
        text = page.text.split("local Data =\n" )[-1].split("\nreturn Data")[0].replace(" =", ":").replace("[", "").replace("]", "").replace("        ", "")
        items = re.findall(r'"(.*)": {', text)
        pages = [pywikibot.Page(pywikibot.Site(), i) for i in items]
        for itemPage in pages:
            if "{{Gear/Automatic}}" not in itemPage.text:
                wiki = wtp.parse(itemPage.text)
                for template in wiki.templates:
                    if "gear" in str(template).lower():
                        print(str(template))
                        itemPage.text = itemPage.text.replace(str(template), "{{Gear/Automatic}}")
                        itemPage.save("Replace Gear Template with Gear/Automatic -- test", minor=False)
                        break
                br = True
    except KeyboardInterrupt:
        br = True
    except Exception as e:
        print(e)
        notDone.append(str(page))

if notDone:
    print(notDone)

