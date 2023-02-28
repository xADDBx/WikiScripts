import pywikibot

'''
Simple scripts which prints all Namespaces of the pywikibot configured Wiki
'''

print(pywikibot.site.Namespace.canonical_namespaces)
