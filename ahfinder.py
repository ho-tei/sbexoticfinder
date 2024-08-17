import os
import requests
import struct
import json
import ast
import nbt
import io
import base64
import time
import traceback
import threading

oldauctions = {} # Global

def getLastUpdated():
    return requests.get("https://api.hypixel.net/v2/skyblock/auctions").json()["lastUpdated"]

def every(delay, task):
  r = requests.get("https://api.hypixel.net/v2/skyblock/auctions").json()
  next_time = getLastUpdated()/1000 + delay
  while True:
    time.sleep(max(0, next_time - time.time()))
    try:
      task()
    except Exception:
      traceback.print_exc()
      # in production code you might want to have this instead of course:
      # logger.exception("Problem while executing repetitive task.")
    # skip tasks if we are behind schedule:
    next_time += (time.time() - next_time) // delay * delay + delay

def parse_tuple(string):
    try:
        s = ast.literal_eval(str(string))
        if type(s) == tuple:
            return s
        return
    except:
        return

def rgbstringToHex(rgb):
    tup = parse_tuple(rgb)
    return bytes.hex(struct.pack('BBB',*tup))

def decimalToHex(decimal):
    newhex = f'{decimal:0x}'
    if len(newhex) < 6:
        newhex = newhex.rjust(6, "0")
    return newhex

def updateList():
    _items = {}
    r = requests.get("https://api.hypixel.net/resources/skyblock/items").json()

    for i in r["items"]:
        if not "LEATHER" in i["material"]:
            continue

        if not 'color' in i:
            continue

        _items[i["id"]] = rgbstringToHex(i["color"])

    _items["lastUpdated"] = r["lastUpdated"]

    with open("items.json", "w") as o:
        o.write(json.dumps(_items))

def isCrystalColor(hex):
    _colors = ["1f0030", "46085e", "54146e", "5d1c78", "63237d", "6a2c82", "7e4196", "8e51a6", "9c64b3", "a875bd",
            "b88bc9", "c6a3d4", "d9c1e3", "e5d1ed", "efe1f5", "fcf3ff"]
    
    if hex in _colors:
        return True
    
    return False

def isFairyColor(item, hex):
    _colors = ["ffcce5", "ff3399", "99004c", "ff99cc", "ff007f", "660033", "ff66b2", "cc0066"]
    _ogColors = ["ff99ff", "ffccff", "e5ccff", "cc99ff", "cc00cc", "ff00ff", "ff33ff", "ff66ff", "b266ff", "9933ff", "7f00ff", "660066", "6600cc", "4c0099", "330066", "990099"]
    _ogChestplate = ["660033", "ffcce5", "ff99cc"]
    _ogLeggings = ["ffcce5", "660033", "99004c"]
    _ogBoots = ["660033", "99004c", "cc0066"]
    _ogHelmet = ["ffcce5", "ff99cc", "ff66b2"]
    
    if "HELMET" in item and hex in _ogHelmet:
        return "OG Fairy"
    
    if "CHESTPLATE" in item and hex in _ogChestplate:
        return "OG Fairy"
    
    if "LEGGINGS" in item and hex in _ogLeggings:
        return "OG Fairy"

    if "BOOTS" in item and hex in _ogBoots:
        return "OG Boots"
    
    if hex in _colors:
        return "Fairy"
    
    if hex in _ogColors:
        return "OG Fairy"

    
    return False

def isGlitched(item, hex):
    _items = {
        "RANCHERS_BOOTS": "000000",
        "REAPER_BOOTS": "ff0000",
        "REAPER_LEGGINGS": "ff0000",
        "REAPER_CHESTPLATE": "ff0000",
        "SHARK_SCALE_LEGGINGS": "ffdc51",
        "SHARK_SCALE_CHESTPLATE": "ffdc51",
        "SHARK_SCALE_BOOTS": "ffdc51",
        "FROZEN_BLAZE_CHESTPLATE": "f7da33",
        "FROZEN_BLAZE_LEGGINGS": "f7da33",
        "FROZEN_BLAZE_BOOTS": "f7da33",
        "BAT_PERSON_CHESTPLATE": "606060",
        "BAT_PERSON_LEGGINGS": "606060",
        "BAT_PERSON_BOOTS": "606060",
        "POWER_WITHER_CHESTPLATE": "e7413c",
        "POWER_WITHER_LEGGINGS": "e75c3c",
        "POWER_WITHER_BOOTS": "e76e3c",
        "TANK_WITHER_CHESTPLATE": "45413c",
        "TANK_WITHER_LEGGINGS": "65605a",
        "TANK_WITHER_BOOTS": "88837e",
        "SPEED_WITHER_CHESTPLATE": "4a14b7",
        "SPEED_WITHER_LEGGINGS": "5d2Fb9",
        "SPEED_WITHER_BOOTS": "8969c8",
        "WISE_WITHER_CHESTPLATE": "1793c4",
        "WISE_WITHER_LEGGINGS": "17A8c4",
        "WISE_WITHER_BOOTS": "1cd4e4",
        "WITHER_CHESTPLATE": "000000",
        "WITHER_LEGGINGS": "000000",
        "WITHER_BOOTS": "000000",
    }
    if not item in _items:
        return False
    
    if _items[item] == hex:
        return True

def isNormal(item, hex):
    _specialItems = [{
        "CRYSTAL_HELMET": "c6a3d4",
        "CRYSTAL_LEGGINGS": "1f0030",
        "CRYSTAL_BOOTS": "1f0030"
    }]
    _spookColors = ["000000", "070008", "0e000F", "150017", "1b001f", "220027", "29002e", "300036", "37003e", "3e0046",
            "45004d", "4c0055", "52005d", "590065", "60006c", "670074", "6E007c", "750084", "7c008b", "830093",
            "89009b", "9000a3", "9700aa", "993399", "9e00b2"]
    if items[item] == hex:
        return True
    
    if ("GREAT_SPOOK" in item) and (hex in _spookColors):
        return True

# Checks if item is Exotic, Fairy, Crystal or Undyed
def getItemType(item, hex):
    if not item in items:
        return "Unknown"
    
    if isNormal(item, hex):
        return "Normal"

    if "DYE" in hex:
        return "Dyed"

    _fairy = isFairyColor(item, hex)
    if _fairy != False:
        return _fairy
    
    if isCrystalColor(hex):
        return "Crystal"
    
    if isGlitched(item, hex):
        return "Glitched"
    
    return "Exotic"

def getColorFromNbt(itemBytes):
    nbtfile = nbt.nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(itemBytes)))
    try:
        color = nbtfile["i"][0]["tag"]["display"]["color"].value
    except:
        return -1
    
    try:
        itemDye = nbtfile["i"][0]["tag"]["ExtraAttributes"]["dye_item"].value
    except:
        itemDye = "None"
    
    if not itemDye == "None":
        return itemDye
    
    return decimalToHex(color)

def getItemIdFromNbt(itemBytes):
    nbtfile = nbt.nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(itemBytes)))
    try:
        id = nbtfile["i"][0]["tag"]["ExtraAttributes"]["id"].value
    except:
        return -1
    return id

#def checkForNewElements(itemType, newdict, oldDict):
#    newElements = {}
#    for x in newdict:
#        if x not in oldDict:
#            newElements[x] = newdict[x]
#            sendItemToDiscord(x, itemType, newdict[x][0], newdict[x][1], newdict[x][2])

def sendItemToDiscord(auctionId, itemType, itemId, color, price):
    json_data = {
      "content": f"@no **New {itemType} found\n\nItem Type: **{itemId}\nItem Color: **#{color}**\n\nPrice: **{price}**\n\n\n```/viewauction {auctionId}```",
    }
    
    webhook_url = ""
    if itemType == "Exotic":
        webhook_url = "https://discord.com/api/webhooks/1274174024615854202/dnRMtyxU_VXsaXg1Rlu2p6PuwZooAn91CJMKgbMGtbZ9iVb0vrL8fSO9dvl44nivJGqd"
    elif itemType == "Crystal":
        webhook_url = "https://discord.com/api/webhooks/1274174190702035037/VwxREQMjE9jNx5XCFgga2DJET7IjZy7JR5JrxuhYa6FrxTiXWy_jgKBd013LUbq6RLIV"
    elif itemType == "Fairy" or itemType == "OG Fairy":
        webhook_url = "https://discord.com/api/webhooks/1274174289196744815/l8CXRBj4ikpzzUax0vYB0lxCPOHBV5ei-0PxbWvNIgYuHdZXoT_xImFaxSrweI5kmlGE"

    result = requests.post(webhook_url, json=json_data)

def loadOldAuctions():
    global oldauctions;
    with open("auctions.json", "r") as o:
        try:
            oldauctions = json.load(o)
        except Exception as e:
            oldauctions = {}
            print(e)

def saveData():
    with open("auctions.json", "w") as o:
        try:
            o.write(json.dumps(auctions))
        except Exception as e:
            print(e)

    with open("dyed.json", "w") as o:
        try:
            o.write(json.dumps(itemdyed))
        except Exception as e:
            print(e)

    with open("crystal.json", "w") as o:
        try:
            o.write(json.dumps(crystals))
        except Exception as e:
            print(e)

    with open("exotics.json", "w") as o:
        try:
            o.write(json.dumps(exotics))
        except Exception as e:
            print(e)

    with open("fairys.json", "w") as o:
        try:
            o.write(json.dumps(fairys))
        except Exception as e:
            print(e)

    with open("glitched.json", "w") as o:
        try:
            o.write(json.dumps(glitched))
        except Exception as e:
            print(e)

    with open("unknown.json", "w") as o:
        try:
            o.write(json.dumps(unknowns))
        except Exception as e:
            print(e)
    print("Saved")

items = {}

# Download list of items with their corresponding hex value if items.json doesn't exist
if not os.path.isfile("./items.json"):
    updateList()

# Load Items
with open("items.json", "r") as o:
    try:
        items = json.loads(o.read())
    except Exception as e:
        print(e)

auctions = {}
exotics = {}
glitched = {}
fairys = {}
crystals = {}
itemdyed = {}
unknowns = {}
def scanAH(page):
    print(f"Started Thread for page {str(page)}")
    # Relevant auctions


    ## Get all auctions

    #init = requests.get("https://api.hypixel.net/v2/skyblock/auctions").json()
    #pages = init["totalPages"]

    #! Asynchronize
    
    r = requests.get(f"https://api.hypixel.net/v2/skyblock/auctions?page={page}").json()
    for i in r["auctions"]:
        #if i in auctions:
        #    continue

        if not "armor" in i["category"]:
            continue
        
        color = getColorFromNbt(i["item_bytes"])
        if color == -1:
            continue
        
        id = getItemIdFromNbt(i["item_bytes"])
        if id == -1:
            continue
        
        itemType = getItemType(id, color)
        if itemType == "Normal":
            continue


        price = str(i["starting_bid"])
        data = [id, color, f"BIN: ${price}"]

        if i["bin"] == False:
            data = [id, color, f"Starting Bid: ${price}", f"Current Bid: ${i["highest_bid_amount"]}"]

        if itemType == "Dyed":
            itemdyed[i["uuid"]] = data
        
        if itemType == "Crystal":
            crystals[i["uuid"]] = data

        if itemType == "Exotic":
            exotics[i["uuid"]] = data
        
        if itemType == "Fairy":
            fairys[i["uuid"]] = data
        
        if itemType == "OG Fairy":
            data.append("OG")
            fairys[i["uuid"]] = data

        if itemType == "Glitched":
            glitched[i["uuid"]] = data
        
        if itemType == "Unknown":
            unknowns[i["uuid"]] = data
        
        if (i["uuid"] not in oldauctions) and (itemType == "Crystal" or itemType == "Exotic" or itemType == "Fairy" or itemType == "OG Fairy"):
            if itemType == "OG Fairy":
                sendItemToDiscord(i["uuid"], f"OG {itemType}", id, color, price)
            else:
                sendItemToDiscord(i["uuid"], itemType, id, color, price)


        auctions[i["uuid"]] = [id, color, itemType, f"Price: ${price}"]

    print(f"[*] Finished Thread {str(page)}")

def start():
    loadOldAuctions()
    init = requests.get("https://api.hypixel.net/v2/skyblock/auctions").json()
    threads = []
    pages = init["totalPages"]
    starttime = time.time()
    for i in range(pages):
        t = threading.Thread(target=scanAH, args=(i,), name=f"t{str(i)}")
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()
    
    #compareAuctions()
    print(time.time())
    print(init["lastUpdated"]/1000)
    print(starttime - time.time())
    saveData()

print("~~~~AHFINDER~~~~")
print("Select an option:\n")
print("1 - Automate")
print("2 - Run once")
user = input(" > ")

if int(user) == 1:
    every(60, start)
elif int(user) == 2:
    start()
#every(60, start)