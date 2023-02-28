import re
import codecs
import requests
import json
import wikitextparser as wtp

'''
Used to scrape item data from a wiki table.
For each item a lookup is performed where
1) The item page is visited to get various craft and price values
2) A DLC + Lunares Coing lookup is performed
3) A password lookup is performed
The gathered data is then brought into the used format.
'''


class Armour:
    isLunInit = False
    isPWInit = False
    gold = ""
    silver = ""
    goldandsilver = ""
    pwText = ""

    def __init__(self, Name, Usable, Skilllvl, Gender, Stat1Value, Stat2Value, Special, Subtype, DLC, Sold):
        self.Name = Name  # name using table information
        self.Description = ""  # description from infobox
        self.Rarity = 0  # number from 0 to 5 using rarity in infobox
        self.Usable = Usable  # [] with "ALL" or list of Jobs using table information
        self.Skilllvl = Skilllvl  # Number using table information
        self.Gender = Gender  # None or "Male" or "Female"
        self.Stat1 = "D"  # first letter of first stat name in infobox
        self.Stat1Value = Stat1Value  # [] with Number or "?" using table overwritten by Infobox
        self.Stat2 = "M"  # first letter of second stat name in infobox
        self.Stat2Value = Stat2Value  # number or "?" using table overwritten by Infobox
        self.Special = Special  # "P" or string using table information
        self.CraftClass = None  # "CB" / "CA" / "CT" / None using craftClass in Infobox
        self.CraftRank = None  # Craftrank value or None
        self.Ingredients = None  # None or List of Strings using Infobox
        self.Amount = None  # None or List of Strings using Infobox
        self.Exp = None  # None since I didn't find information
        # B if it is buyable with Lunares (doesn't differentiate between G and S!) using table info
        # when not Lunares buyable then Amount of Dosh if entered in Infobox else None
        self.Sold = Sold  # see the two lines above
        self.Sell = ["?", "?", "?", "?", "?"]  # [] with "?" or Number using Infobox
        self.Type = "T"  # only "T"
        self.Subtype = Subtype  # "full" or None using table info
        self.DLC = DLC  # "1" or None using table info

    def __repr__(self):
        return f"{self.Name} {str(self.Usable)} {self.Skilllvl} {self.Stat1Value[0]} {self.Stat2Value[0]} " \
               f"{self.Special} {self.Gender} {self.DLC} {self.Subtype} {self.Sold}\n"

    def __str__(self):
        s = 8 * " "
        ret = "    " + self.Name.replace("[[", '["').replace(']]', '"]') + " = {\n"
        ret += s + 'Description = "' + self.Description.replace('"', r'\"') + '",\n'
        ret += s + f"Rarity = {self.Rarity},\n"
        ret += s + "Usable = { " + ", ".join([f'"{i}"' for i in self.Usable]) + " },\n"
        ret += s + f"SkillLvl = {self.Skilllvl},\n"
        if self.Gender is not None:
            ret += s + f'Gender = "{self.Gender}",\n'
        ret += s + f"Stat1 = {self.Stat1},\n"
        ret += s + "Stat1Value = { "
        if self.CraftClass is not None:
            ret += ", ".join([f'"{i}"' if not i.isnumeric() else i for i in self.Stat1Value])
        else:
            ret += ", ".join([f'"{i}"' if not i.isnumeric() else i for i in [self.Stat1Value[0],
                                                                             "N/A", "N/A", "N/A", "N/A"]])
        ret += " },\n"
        ret += s + f"Stat2 = {self.Stat2},\n"
        ret += s + "Stat2Value = " + (self.Stat2Value if self.Stat2Value.strip().isnumeric() else '"?"') + ",\n"
        ret += s + "Special = " + (self.Special if self.Special == "P" else f'"{self.Special}"') + ",\n"
        if self.CraftClass is not None:
            ret += s + f"CraftClass = {self.CraftClass},\n"
            ret += s + f'CraftRank = "{self.CraftRank}",\n'.replace(' (High Level)"', '"..H')
            ret += s + "Ingredients = { " + ", ".join(f'"{i}"' for i in self.Ingredients) + " },\n"
            if self.Amount is not None:
                ret += s + "Amount = { " + ", ".join(i for i in self.Amount) + " },\n"
            ret += s + 'Exp = "??",\n'
        ret += s + "Sold = " + (self.Sold.replace(",", "") if (self.Sold.isnumeric() or self.Sold.strip() in ["G", "S",
                                "B", "W"] or self.Sold.strip().startswith("W..")) else '"?"') + ",\n"
        ret += s + "Sell = { "
        if self.CraftClass is not None:
            ret += ", ".join([f'"{i.replace(",", "").replace(".", "")}"' if not i.isnumeric()
                              else i for i in self.Sell])
        else:
            ret += ", ".join([f'"{i.replace(",", "").replace(".", "")}"' if not i.isnumeric()
                              else i for i in [self.Sell[0], "N/A", "N/A", "N/A", "N/A"]])
        ret += " },\n"
        ret += s + "Type = T"
        if self.Subtype == "full":
            ret += ',\n' + s + 'Subtype = "full"'
        if self.DLC == 1:
            ret += ',\n' + s + 'DLC = 1'
        ret += "\n    },\n"

        return ret

    @staticmethod
    def getWiki(PageName):
        url = f"https://fantasy-life.fandom.com/api.php?action=query&prop=revisions&titles={PageName}"
        url += "&rvslots=*&rvprop=content&formatversion=2&format=json"
        response = requests.get(url)
        response.close()
        return wtp.parse(json.loads(response.content)['query']['pages'][0]['revisions'][0]['slots']['main']['content'])

    @staticmethod
    def initPW():
        pw_page = Armour.getWiki("Passwords")
        Armour.isPWInit = True
        for pwItem in re.findall(r"\[\[([^\[.]*?)]]", str(pw_page.sections[5])):
            Armour.pwText += str(Armour.getWiki(pwItem))

    def password_check(self, wiki):
        if not Armour.isPWInit:
            Armour.initPW()
        if self.Name.replace("[", "").replace("]", "") in Armour.pwText or "password" in str(wiki).lower():
            self.Sold = "W"

    @staticmethod
    def initLun():
        lunares_page = Armour.getWiki("Lunares Coins")
        Armour.isLunInit = True
        sections = str(lunares_page.get_sections()).split("Section(")[8:]
        lines = []
        for section in sections:
            lines.extend(section.split("Coins"))
        gold = []
        goldandsilver = []
        silver = []
        for i in range(1, len(lines)):
            compareTo = lines[i-1].lower().strip()
            if compareTo.endswith("gold") or compareTo.endswith("gold lunares"):
                gold.append(lines[i])
            elif compareTo.endswith("gold and silver"):
                goldandsilver.append(lines[i])
            elif compareTo.endswith("silver"):
                silver.append(lines[i])

        Armour.gold = "".join(gold).replace(r"\'", "'")
        Armour.silver = "".join(silver).replace(r"\'", "'")
        Armour.goldandsilver = "".join(goldandsilver).replace(r"\'", "'")
        for goldItem in re.findall(r"\[\[([^\[.]*?Pack.*?)]]", Armour.gold):
            Armour.gold += str(Armour.getWiki(goldItem))
        for silverItem in re.findall(r"\[\[([^\[.]*?Pack.*?)]]", Armour.silver):
            Armour.silver += str(Armour.getWiki(silverItem))
        for silverAndGoldItem in re.findall(r"\[\[([^\[.]*?Pack.*?)]]", Armour.goldandsilver):
            Armour.goldandsilver += str(Armour.getWiki(silverAndGoldItem))

    def lunares_check(self):
        if not Armour.isLunInit:
            self.initLun()
        isW = False
        if self.Sold == "W":
            isW = True
        if self.Name in Armour.gold:
            self.Sold = "G"
        elif self.Name in Armour.silver:
            self.Sold = "S"
        elif self.Name in Armour.goldandsilver:
            self.Sold = "B"
        if isW and self.Sold in ["G", "S", "B"]:
            self.Sold = 'W.." and "..' + self.Sold

    def scrape(self):
        if self.Name == "":
            return "No Name"
        while self.Name.startswith(" "):
            self.Name = self.Name[1:]
        pageName = self.Name.replace('[', '').replace(']', '')
        wiki = Armour.getWiki(pageName)
        if "REDIRECT" in str(wiki):
            self.Name = str(wiki).split("#")[1][9:]
            return self.scrape()
        if "Silver Lunares" in str(wiki) or "Silver [[Lunares" in str(wiki):
            self.Sold = "S"
        if "Gold Lunares" in str(wiki) or "Gold [[Lunares" in str(wiki):
            if self.Sold == "S":
                self.Sold = "B"
            else:
                self.Sold = "G"
        self.Rarity = 0
        for argument in wiki.templates[0].arguments:
            argument.name = argument.name.strip().lower()
            if argument.value.startswith(" "):
                argument.value = argument.value[1:]
            argument.value = argument.value.replace("\n", "")
            if "description" in argument.name:
                self.Description = argument.value
            elif "rarity" in argument.name:
                self.Rarity = argument.value
            elif "stat1" == argument.name:
                self.Stat1 = argument.value.replace("'", "").strip()[0].upper()
            elif "stat1value" == argument.name and argument.value.strip().isnumeric():
                self.Stat1Value[0] = argument.value.strip()
            elif "stat1good" == argument.name and argument.value.strip().isnumeric():
                self.Stat1Value[1] = argument.value.strip()
            elif "stat1great" == argument.name and argument.value.strip().isnumeric():
                self.Stat1Value[2] = argument.value.strip()
            elif "stat1top" == argument.name and argument.value.strip().isnumeric():
                self.Stat1Value[3] = argument.value.strip()
            elif "stat1divine" == argument.name and argument.value.strip().isnumeric():
                self.Stat1Value[4] = argument.value.strip()
            elif "stat2" == argument.name:
                self.Stat2 = argument.value.replace("'", "").strip()[0].upper()
            elif "stat2value" in argument.name and argument.value.strip().isnumeric():
                self.Stat2Value = argument.value.strip()
            elif "craftclass" in argument.name:
                if "tailor" in argument.value.lower():
                    self.CraftClass = "CT"
                elif "blacksmith" in argument.value.lower():
                    self.CraftClass = "CB"
                elif "alchemist" in argument.value.lower():
                    self.CraftClass = "CA"
            elif "craftrank" in argument.name:
                self.CraftRank = argument.value
            elif "ingredient" in argument.name:
                if self.Ingredients is None:
                    self.Ingredients = [None for _ in range(20)]  # very large maximum estimate
                index = int(argument.name[10]) - 1
                self.Ingredients[index] = argument.value
            elif "amount" in argument.name:
                if self.Amount is None:
                    self.Amount = [None for _ in range(20)]
                index = int(argument.name[6]) - 1
                self.Amount[index] = argument.value
            elif "sold" in argument.name:
                if not self.Sold.strip().isnumeric():
                    if "dosh" in argument.value.lower():
                        val = argument.value.split(" ")[0]
                    elif argument.value.strip().isnumeric():
                        val = argument.value.strip()
                    else:
                        val = "?"
                    self.Sold = val
            elif "sell" in argument.name:
                if "dosh" in argument.value.lower():
                    val = argument.value.split(" ")[0]
                elif argument.value.strip().isnumeric():
                    val = argument.value.strip()
                else:
                    val = "?"
                if "sell" == argument.name:
                    self.Sell[0] = val
                elif "sellgood" == argument.name:
                    self.Sell[1] = val
                elif "sellgreat" == argument.name:
                    self.Sell[2] = val
                elif "selltop" == argument.name:
                    self.Sell[3] = val
                elif "selldivine" == argument.name:
                    self.Sell[4] = val
        if self.Ingredients is not None:
            self.Ingredients = [i for i in self.Ingredients if i is not None]
        if self.Amount is not None:
            self.Amount = [i for i in self.Amount if i is not None]

        self.password_check(wiki)
        self.lunares_check()
        return self

    @staticmethod
    def readTable(filename):
        entries = []
        tableFile = codecs.open(filename, encoding='utf-8')
        text = tableFile.read()
        tableFile.close()
        lines = text.splitlines()
        first = True
        for line in lines:
            if first:
                text = line
                first = False
                continue
            else:
                if line.startswith("|"):
                    text += "\n"
                else:
                    text += " "
            text += line
        text = text.split("|-")[2:]
        for entry in text:
            Subtype = None
            Skilllvl = "0"
            Special = "P"
            Usable = []
            Gender = None
            DLC = None
            Sold = "?"
            entry = [line for line in entry.splitlines() if line != ""]
            if "style" in entry[0]:
                if "aquamarine" in entry[0] or "wheat" in entry[0]:
                    DLC = 1
                indexes = [s.start() for s in re.finditer(r"\|", entry[0])]
                entry[0] = entry[0][indexes[1]:]
            if "<br" in entry[0]:
                Subtype = "full"
                entry[0] = entry[0].split("<br")[0]
            entry[0] = entry[0][1:]
            if "|" in entry[0]:
                entry[0] = entry[0].split("|")[0] + "]]"
            Name = entry[0].replace("'''", "")
            if "_" not in entry[1]:
                Skilllvl = entry[1][1:]
            Stat1Value = [entry[2][1:], "?", "?", "?", "?"]
            Stat2Value = entry[3][1:]
            if entry[4].strip() != "|":
                Special = entry[4][1:].replace("<br />", " ").replace("<br/", " ").replace("<br>", " ")
            if "all" in entry[5].lower():
                Usable = ["All"]
            else:
                for Job in ["Paladin", "Mercenary", "Hunter", "Magician", "Miner", "Woodcutter",
                            "Angler", "Cook", "Blacksmith", "Carpenter", "Tailor", "Alchemist"]:
                    if Job in entry[5]:
                        Usable.append(Job)
            if entry[6].strip() != "|":
                for g in [":Male", ":Female"]:
                    if g in entry[6]:
                        Gender = g[1:]
            entry = Armour(Name, Usable, Skilllvl, Gender, Stat1Value, Stat2Value, Special, Subtype, DLC, Sold)
            entries.append(entry)
        return entries


part = "Feet"
res = Armour.readTable("../data/wiki" + part + "Table.txt")

file = []
for item in res:
    file.append(str(item.scrape()))
    print(f"Done: {item.Name}")

f = codecs.open("../data/scraped" + part + ".txt", "w", encoding='utf-8')
[f.write(x) for x, _ in sorted(zip(file, res), key=lambda x: (int(x[1].Skilllvl), int(x[1].Rarity), x[1].Usable))]
f.close()
