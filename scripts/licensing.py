from pywikibot import pagegenerators

'''
Uses Pywikibot to iterate through all pages in namespace 6 (=File:)
If a page does not include the keywords License it adds a Fairuse License section.
Should the page contain categories, it adds the License section in between the normal content and the Categories.
'''

gen = pagegenerators.PreloadingGenerator(pagegenerators.AllpagesPageGenerator(namespace=6), groupsize=50)
notDone = []
br = False
for page in gen:
    if br:
        break
    try:
        if "Licensing" not in page.text:
            ind = page.text.find("[[Category")
            if ind == -1:
                page.text += "\n== Licensing ==\n{{Fairuse}}\n"
            else:
                after = page.text[ind:]
                page.text = page.text[:ind] + "\n== Licensing ==\n{{Fairuse}}\n" + after
            page.save(summary="Added Fairuse Licensing")
    except KeyboardInterrupt:
        br = True
    except Exception as e:
        print(e)
        notDone.append(str(page))

if notDone:
    print(notDone)
