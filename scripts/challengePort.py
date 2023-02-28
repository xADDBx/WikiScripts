import re

'''
Used to port old challenge wikitable data into the new {{Challenges Table}} template.
'''

f = open("../data/wikiText.txt", "r")
text = f.read()
f.close()
text = re.split(r"\n\|| \| ", text)
res = []
tiers = ["novice", "fledgling", "apprentice", "adept", "expert", "master", "hero", "godTraining"]
stepName = ["Name", "Instruction", "Star"]
tier = -1
count = 1
step = 0
f = open("../data/wikiProcessed.txt", "w")
isChallenge = False
for t in text:
    t = t.replace("\n''", " ''")
    eq = t.strip()
    isChallenge = "challenges" in eq.lower()
    if not ((eq.startswith("-") or eq.startswith("style=") or eq.startswith("|")) and not isChallenge):
        if isChallenge:
            count = 1
            step = 0
            tier += 1
            isChallenge = False
        else:
            if "'''" not in t:
                t = t.replace(" ''", "<br>(").replace("''", ")").replace(" /", "")
            if step == 3:
                step = 0
                count += 1
            if tier == 0:
                f.write("|" + tiers[tier] + stepName[step] + "=" + t + "\n")
            else:
                f.write("|" + tiers[tier] + str(count) + stepName[step] + "=" + t + "\n")
            step += 1
f.close()
