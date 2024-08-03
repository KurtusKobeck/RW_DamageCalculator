#Rimworld Armor and Damage Tester
import itertools
import math

#name       damage  Pen
#Revolver   12      18


gunDict={"Revolver":(12,18),"AutoPistol":(10,15),"MachinePistol":(6,9),"PumpShotgun":(18,14),"LMG":(11,16),"HeavySMG":(12,18),"Minigun":(10,15)
         ,"Hellcat":(10,15),"AssultRifle":(11,16),"ChainShotgun":(18,14),"ChargeRifle":(15,35),"BoltActionRifle":(18,27),"SniperRifle":(25,38)
         ,"ChargeLance":(30,45),"Pila":(25,10),"ShortBow":(11,16),"RecurveBow":(14,21),"Greatbow":(17,15)}
#bluntMeleeDict={"WarhammerUranium":(30,30),"MaceUranium":(23.6,24),"ClubUranium":(21,21),"Zueshammer":(31,46),"PsyStaff":(12,18)}
#sharpMeleeDict={"PowerClaw":(22,33),"":(),"":(),"":(),"":(),"":(),"":(),"":(),"":()}
#print(Dict["Revolver"])
#for gun in gunDict:
#    print(gunDict[gun])

#In Rimworld, when a pawn is "hit", the game begins rolling RNG to determine where the pawn is going to be damaged.
#A pawn is considered "hit" when a ranged attack accuracy check is passed by an attacker and is not blocked by cover
#or when they fail to dodge a melee attack delivered by an attacker who passed their melee accuracy check.
#A pawn who has been hit then rolls a number to determine which part the damage applies to.
#Some parts contain subparts which can be struck after that part has been targeted. Otherwise, the damage applies to
#that part as generic damage.
#Torso [legs = 14% each, shoulders and arms as a unit = 12% each, neck and head as a unit = 7.5%
#Torso=1.0=[leg:14,Leg:14,Shoulder:12,Shoulder:12,neck:7.5,Liver:2.5,Kindey:1.7,Kindey:1.7,Lung:2.5,Lung:2.5,Heart:2,
#   Stomache:2.5, Spine:2.5, Pelvis:2.5, Sternum:1.5, Ribcage:3.6]
#Neck, legs and shoulders each have subparts triggering additional rolls. If no range is rolled, the damage applies to the base generically.
#Neck: Head=80
#Head: Skull:18,
#Skull: Brain:80

#Ultimately, the goal of armor is to reduce the likeliehood of instadeaths and to reduce the overall damage taken.
#Rimworld's instant death conditions are as follows:
#1. over 150 damage taken
#2. the destruction of any of the following organs: Brain, Heart, Both lungs, Both Kidneys, liver.
#3. the destruction of any of the following body parts: Torso, Head, Skull, Neck.
#4. 100% blood loss
#5. 100% pain shock threshold (almost impossible to reach without drugs/mods due to pawns dropping from pain)

#This functionally means that Armor serves 3 goals: overall damage reduction, protect the vitals (head, neck and torso) and prevent dismemberment.

#hitrates,hp,coverageParent
torso=(0.15,40,"torso")

lungs=(0.05,15,"torso")             #no armor slot
ribcage=(0.036,30,"torso")          #no armor slot
kidneys=(0.034,15,"torso")          #no armor slot
liver=(0.025,20,"torso")            #no armor slot
stomache=(0.025,20,"torso")         #no armor slot
spine=(0.025,25,"torso")            #no armor slot
pelvis=(0.025,25,"torso")           #indestructible, no armor slot
heart=(0.02,15,"torso")             #no armor slot
sternum=(0.015,20,"torso")          #indestructible, no armor slot

legs=(0.196,30,"legs")
femurs=(0.028,25,"legs")            #no armor slot #essential for legs
tibias=(0.028,25,"legs")            #no armor slot #essential for legs
feet=(0.01708,25,"feet")
toes=(0.01092,8,"toes")

shoulders=(0.0336,30,"shoulders")   #essential for arms
clavicles=(0.0216,25,"shoulders")   #indestructible
arms=(0.121968,30,"arms")           
humeri=(0.01848,25,"arms")         #no armor slot #essential for arms
radii=(0.01848,20,"arms")          #no armor slot #essential for arms
hands=(0.01655808,20,"hands")    
fingers=(0.00931392,8,"fingers")  

neck=(0.015,25,"neck")
head=(0.0174,25,"head")
skull=(0.00216,25,"head")          #no armor slot
brain=(0.00864,10,"head")          #no armor slot
eyes=(0.0084,10,"eyes")
ears=(0.0084,12,"ears")
nose=(0.006,10,"nose")
jaw=(0.008991,20,"jaw")
tongue=(0.000009,1,"jaw")         #Technically, on taking damage, the tongue is hardcoded to be removed 100% of the time.

#print(torso+legs+femurs+tibias+feet+toes+shoulders+clavicles+arms+humeri+radii+hands+fingers+neck+head+skull+brain+eyes+ears+nose+jaw+tongue+lungs+ribcage+
#      kidneys+liver+stomache+spine+pelvis+heart+sternum)
#print(legs+femurs+tibias+feet+toes)                                         #spot on
#print(shoulders+clavicles+arms+humeri+radii+hands+fingers)                  #spot on
#print(neck[0]+head[0]+skull[0]+brain[0]+eyes[0]+ears[0]+nose[0]+jaw[0]+tongue[0])                      #spot on
#print(lungs[0]+ribcage[0]+kidneys[0]+liver[0]+stomache[0]+spine[0]+pelvis[0]+heart[0]+sternum[0])      #spot on

bodyDict={"torso":torso,"lungs":lungs,"ribcage":ribcage,"kidneys":kidneys,"liver":liver,"stomache":stomache,"spine":spine,"pelvis":pelvis,"heart":heart,
          "sternum":sternum,"legs":legs,"femurs":femurs,"tibias":tibias,"feet":feet,"toes":toes,"shoulders":shoulders,"clavicles":clavicles,"arms":arms,
          "humeri":humeri,"radii":radii,"hands":hands,"fingers":fingers,"neck":neck,"head":head,"skull":skull,"brain":brain,"eyes":eyes,"ears":ears,
          "nose":nose,"jaw":jaw,"tongue":tongue}
deathRolls=[torso,head,skull,neck,brain,heart,liver]
organRolls=[lungs,kidneys,stomache,spine,eyes,ears,nose,jaw,tongue] #tongue is stupid.
limbRolls=[legs,femurs,tibias,shoulders,arms,humeri,radii]
handfoodRolls=[feet,hands]
digitRolls=[toes,fingers]
lesserTorsoRolls=[ribcage,pelvis,sternum]
lesserArmRolls=[clavicles]
bodyGroups=[deathRolls,organRolls,limbRolls,handfoodRolls,digitRolls,lesserTorsoRolls,lesserArmRolls]

layerDict={"skin":100,"middle":200,"outer":300,"head":150}   #Add your custom layers here!

def charMapper(sharps): #Used for determining whether to use .sharps or .blunts, whether to use the ignore armor or partial block statistic and how much damage is dealt
    charMap=""
    for i in range(0,2):
        for j in range(0,len(sharps)):
            if(i==0):
                charMap+='A'
            else:
                charMap+='B'
    #print(charMap)
    things=itertools.permutations(charMap,len(sharps))
    coordinateB=[]
    for thing in things:
        if(thing in coordinateB):
            pass
        else:
            coordinateB.append(thing)
            #print(thing)
    coordinateA=[]
    dig=["A"]
    for thing in coordinateB:
        firstNuller=0
        for char in thing:
            if(firstNuller==0):
                firstNuller=1
            else:
                if(char=="A"):
                    dig.append("A")
                else:
                    dig.append("B")
        trigB=False
        replacementDig=[]
        for charette in dig:
            if(trigB or charette=="B"):
                replacementDig.append("B")
                trigB=True
            else:
                replacementDig.append("A")
        coordinateA.append(replacementDig)
        dig=["A"]
    coordinateA.sort()
    #print(coordinateA)
    #print(coordinateB)
    return coordinateA,coordinateB

#pawn originated damage sources: guns, bows, cut, crush, blunt, poke, demolish, stab, scratch, scratchToxic (venom talon), bite, toxicBite(venom fang).
okpSourceDict={"gun":(0,0.7),"bow":(0,0.7),"cut":(0,0.1),"crush":(0.4,1),"poke":(0.4,1),"demolish":(0.4,1),"stab":(0.4,1),"scratch":(0,0.7),
               "scratchToxic":(0,0.7),"bite":(0,0.1),"toxicBite":(0,0.1)}
def invLerp(source,value):   #InvLerp takes a range between 0-1 and a value between 0-1 and returns the ratio between them.
    lowerBound,upperBound=okpSourceDict[source]
    output=(value-lowerBound)/(upperBound-lowerBound)
    if output > 1:  #caps maximum odds of outcome at 100%
        output=1
    if output <0:   #caps miniumum odds of outcome at 0%
        output=0
    return output
#ex:
#print(invLerp(0.1,0.6,0.35))
#Use Case:
#Overkill Protection uses invLerp with different ranges depending on damage types to determine whether a body part is destroyed.
#lowerBound and upperBound are determined by the damage type's def file, but
#value = (damage-currentHp)/maxHp

def gunPenetrate(armorLayers,bullet,health): #armorLayers is a list of tuples((sharp,blunt),...), bulletValues is a tuple (damage,penValue),
    #Returns odds of target's destruction, average damage delivered and chance to receive damage (and chance of death)->implicitly calculable
    #health is maxHp    where (subLimbScore tallies the dependentLimbs)->implicit ,
    #and isInternalTo determines whether its inside an arm, torso or head.
    #(head parts are not considered inside, with the exception of the skull and brain, which are
    #both 10hp and lethal, so theres very little difference between them beyond a TINY boost to expected damage.
    #isEssential determines whether it's destruction results in a destroyed parent. This is for legs(femur, tibia) and arms (humeri, radii)
    hitDamageValues=[]      #damage variants = n+1
    hitChances=[]           #total outcomes is equal to 2^n, where n=len(armorLayers)
    sharpResults=[]     #lists of tuples (halfDamageAndConvertToBlunt,ignoreArmor)
    bluntResults=[]
    destructionChance=0
    expectedDamage=0
    #print(armorLayers)
    for layer in armorLayers:
        sharpResults.append(processLayer(layer,bullet[1])[0])
        bluntResults.append(processLayer(layer,bullet[1])[1])
        #print("see: "+str(processLayer(layer,bullet[1])))
    #print("sharp results: "+str(sharpResults))
    #print("blunt results: "+str(bluntResults))
    aCoords,bCoords=charMapper(sharpResults)
    #print("Sharp or Blunt: "+str(aCoords))
    #print("Ignore Armor or Partial Block: "+str(bCoords))
    abDict={"A":1,"B":0}
    totalChanceToBeDamaged=0
    for damageInstance in range(0,len(aCoords)):
        odds=1
        damageFactor=1
        for i in range(0,len(sharpResults)):
            if(aCoords[damageInstance][i]=="A"):
                odds=odds*sharpResults[i][abDict[bCoords[damageInstance][i]]]
            else:
                odds=odds*bluntResults[i][abDict[bCoords[damageInstance][i]]]
            if(bCoords[damageInstance][i]=="B"):
                damageFactor=damageFactor/2
        #print("odds: "+str(odds))
        totalChanceToBeDamaged+=odds
        hitDamage=bullet[0]*damageFactor
        if(hitDamage>=health):
            desChance=invLerp("gun",((hitDamage-health)/health))
            destructionChance+=desChance*odds
            hitDamage=((1-desChance)*(health-1))+(desChance*health)  #account for the damage reduction due to Overkill Protection (OKP)
            #!!!bonus damage to parent not accounted for here!!!
        expectedDamage+=hitDamage*odds
    #print("chance to be damaged: "+str(totalChanceToBeDamaged))
    return destructionChance,expectedDamage,totalChanceToBeDamaged

def processLayer(armorLayer,penetrationValue):#tuple of (sharp,blunt),int of pen value
    #print("ex armorLayer"+str(armorLayer))
    #print(armorLayer[0])
    aRs=(armorLayer[0]-penetrationValue)/2
    if(aRs<0):
        aRs=0
    pAs=0
    pBs=0
    if(aRs==100):
        pAs=0
    elif(aRs>50):
        pAs=1-aRs
        pBs=0
    elif(aRs<0):
        pAs=0
        pBs=100.0
    else:
        pAs=aRs
        pBs=100-(2*aRs)
    aRb=(armorLayer[1]-penetrationValue)/2
    if(aRb<0):
        aRb=0
    pAb=0
    pBb=0
    if(aRb==100):
        pAb=0
    elif(aRb>50):
        pAb=1-aRb
        pBb=0
    elif(aRb<0):
        pAb=0
        pBb=100.0
    else:
        pAb=aRb
        pBb=100-(2*aRb)
    return [pAs/100,pBs/100],[pAb/100,pBb/100]
    #itertools.product([a,b],[c,d])
    #this function returns a list containing the ordered permutations of it's contents. (no double dipping within an order!)
    #Returns: ac, ad, bc, bd


#Supported Coverage Regions: head, neck, eyes, ears, nose, jaw, torso, shoulders, arms, hands, fingers, legs, feet, toes
class armor():
    def __init__(self,wornLayer,sharp,blunt,coverage,wealth):
        self.coverage=coverage
        self.sharp=sharp
        self.blunt=blunt
        self.wornLayer=wornLayer
        self.wealth=wealth
    def __str__(self):
        return str(self.coverage)+" "+str(self.sharp)+" "+str(self.blunt)+" "+str(self.wornLayer)+" "+str(self.wealth)
        
class outfit(): #and outfit is a list of armors
    def __init__(self,gear):
        wornLayers=[]
        self.gear=[]
        unsortedGear=[]
        for item in gear:
            #print("item: "+str(item))
            if(item.wornLayer==("middle","outer") or item.wornLayer==("outer","middle")):
                for element in item.wornLayer:
                    #print("element: "+str(item))
                    if layerDict[element] in wornLayers:
                        print("layers overlap!")
                        return
                    else:
                        wornLayers.append(element)
                        unsortedGear.append((layerDict[element],item))
                #print(wornLayers)
            elif layerDict[item.wornLayer] in wornLayers:
                print("layers overlap!")
                return
            else:
                wornLayers.append(item.wornLayer)
                unsortedGear.append((layerDict[item.wornLayer],item))
                #print(wornLayers)
        #Now sort outer->inner
        #print(unsortedGear)
        unsortedGear.sort(reverse=True)
        #print("gear: "+str(unsortedGear))
        for item in unsortedGear:
            self.gear.append(item[1])
            #print(item[1])
        #print(self.gear)
        unsortedGear=None   #get rid of it.
        #Time to handle constructing the armor layers as region:ordered lists of stats pairs, i.e. torso:(sharp,blunt),(sharp,blunt),(sharp,blunt),etc.
        torsoC=[]
        headC=[]
        neckC=[]
        eyesC=[]
        earsC=[]
        noseC=[]
        jawC=[]
        shouldersC=[]
        armsC=[]
        handsC=[]
        fingersC=[]
        legsC=[]
        feetC=[]
        toesC=[]
        for layer in self.gear:
            if "torso" in layer.coverage:
                torsoC.append((layer.sharp,layer.blunt))
            if "head" in layer.coverage:
                headC.append((layer.sharp,layer.blunt))
            if "neck" in layer.coverage:
                neckC.append((layer.sharp,layer.blunt))
            if "eyes" in layer.coverage:
                eyesC.append((layer.sharp,layer.blunt))
            if "ears" in layer.coverage:
                earsC.append((layer.sharp,layer.blunt))
            if "nose" in layer.coverage:
                noseC.append((layer.sharp,layer.blunt))
            if "jaw" in layer.coverage:
                jawC.append((layer.sharp,layer.blunt))
            if "shoulders" in layer.coverage:
                shouldersC.append((layer.sharp,layer.blunt))
            if "arms" in layer.coverage:
                armsC.append((layer.sharp,layer.blunt))
            if "hands" in layer.coverage:
                handsC.append((layer.sharp,layer.blunt))
            if "legs" in layer.coverage:
                legsC.append((layer.sharp,layer.blunt))
            if "feet" in layer.coverage:
                feetC.append((layer.sharp,layer.blunt))
            if "toes" in layer.coverage:
                toesC.append((layer.sharp,layer.blunt))
        self.torsoCoverage=torsoC
        self.headCoverage=headC
        self.neckCoverage=neckC
        self.eyesCoverage=eyesC
        self.earsCoverage=earsC
        self.noseCoverage=noseC
        self.jawCoverage=jawC
        self.shouldersCoverage=shouldersC
        self.armsCoverage=armsC
        self.handsCoverage=handsC
        self.fingersCoverage=fingersC
        self.legsCoverage=legsC
        self.feetCoverage=feetC
        self.toesCoverage=toesC
        #print("ex coverage: "+str(self.torsoCoverage))
    def refCoverage(self,part):
        if(part in ["torso","lungs","ribcage","kidneys","liver","stomache","spine","pelvis","heart","sternum"]):
            return self.torsoCoverage
        elif(part in ["head","brain","skull"]):
            return self.headCoverage
        elif(part in ["neck"]):
            return self.neckCoverage
        elif(part in ["eyes"]):
            return self.eyesCoverage
        elif(part in ["ears"]):
            return self.earsCoverage
        elif(part in ["nose"]):
            return self.noseCoverage
        elif(part in ["jaw","tongue"]):
            return self.jawCoverage
        elif(part in ["shoulders","clavicle"]):
            return self.shouldersCoverage
        elif(part in ["arms"]):
            return self.armsCoverage
        elif(part in ["hands"]):
            return self.handsCoverage
        elif(part in ["fingers"]):
            return self.fingersCoverage
        elif(part in ["legs","femur","tibia"]):
            return self.legsCoverage
        elif(part in ["feet"]):
            return self.feetCoverage
        elif(part in ["toes"]):
            return self.toesCoverage
        else:
            print("unfound part: "+str(part))
            raise ValueError #"Where are you hitting them, the SOUL?! Thats not a real body part!"
            return "Where are you hitting them, the SOUL?! Thats not a real body part!"

def evaluateOutfit(gun,outfit):
    bodyDict={"torso":torso,"lungs":lungs,"ribcage":ribcage,"kidneys":kidneys,"liver":liver,"stomache":stomache,"spine":spine,"pelvis":pelvis,"heart":heart,
          "sternum":sternum,"legs":legs,"femurs":femurs,"tibias":tibias,"feet":feet,"toes":toes,"shoulders":shoulders,"clavicles":clavicles,"arms":arms,
          "humeri":humeri,"radii":radii,"hands":hands,"fingers":fingers,"neck":neck,"head":head,"skull":skull,"brain":brain,"eyes":eyes,"ears":ears,
          "nose":nose,"jaw":jaw,"tongue":tongue}
    deathRollsA=[torso,heart,liver]
    deathRollsB=[head,skull,brain]
    deathRollsC=[neck]
    organRollsA=[lungs,kidneys,stomache,spine] #torso
    organRollsB=[eyes,ears,nose,jaw,tongue] #head
    limbRolls=[legs,femurs,tibias,shoulders,arms,humeri,radii]
    handFootRolls=[feet,hands]
    digitRolls=[toes,fingers]
    lesserTorsoRolls=[ribcage,pelvis,sternum]
    lesserArmRolls=[clavicles]  #deals parent damage to the shoulder
    #initiate dismembermentTier values
    deathChance=0
    organLossChance=0
    limbLossChance=0
    handLossChance=0
    digitLossChance=0
    #initiate expectedDamage value
    expectedDamage=0
    #initiate chanceToReceiveDamage value
    chanceToReceiveDamage=0
    #initialize brain damage value
    chanceBrainIsDamaged=0
    #run the 7 tiers of tests
    for part in deathRollsA:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#torso
        #print("destroyed vital organ through armor chance: "+str(d)+" chance to shoot that organ: "+str(part[0]))
        deathChance+=d*part[0]  #I'm gonna rule that dieing isn't organloss.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in deathRollsB:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#head
        deathChance+=d*part[0]  #I'm gonna rule that dieing isn't organloss.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
        if(part==brain):
            chanceBrainIsDamaged+=c*part[0]
    for part in deathRollsC:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#neck, no parent
        deathChance+=d*part[0]  #I'm gonna rule that dieing isn't organloss.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in organRollsA:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#torso
        organLossChance+=d*part[0]  #You can live without it.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in organRollsB:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#head, but external and therefore no overdamage
        organLossChance+=d*part[0]  #You can live without it.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in limbRolls:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#limbs, and only the ones essential to the entire limb
        limbLossChance+=d*part[0]  #You can live without it.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in handFootRolls:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#hands and feet.
        handLossChance+=d*part[0]  #You can live without it.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in digitRolls:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#fingers and toes.
        digitLossChance+=d*part[0]  #You can live without it.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in lesserTorsoRolls:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#torso and internal
        #these are indestructible and have less HP than the torso, so death from them is impossible from bullets afaik.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    for part in lesserArmRolls:
        d,e,c=gunPenetrate(outfit.refCoverage(part[2]),gun,part[1])#torso and internal
        #this is indestructible and has less HP than the arms, so dismemberment from this is impossible from bullets afaik.
        expectedDamage+=e*part[0]
        chanceToReceiveDamage+=c*part[0]
    print(" death chance:                    "+str(deathChance)+
          "\n organ destruction chance:        "+str(organLossChance)+
          "\n limb destruction chance:         "+str(limbLossChance)+
          "\n hand/foot destruction chance:    "+str(handLossChance)+
          "\n fingers/toes destruction chance: "+str(digitLossChance)+
          "\n expected damage:                 "+str(expectedDamage)+
          "\n chance to receive damage:        " +str(chanceToReceiveDamage)+
          "\n chance brain is damaged:         "+str(chanceBrainIsDamaged))

#SkinLayers
hyperweaveShirtPants=armor("skin",40,10.8,["torso","neck","shoulders","arms","legs"],415+365)
devilstrandShirtPants=armor("skin",28,7.2,["torso","neck","shoulders","arms","legs"],255+225)
#MiddleLayers
flakVest=armor("middle",100,36,["torso","shoulders","neck"],225)
#OuterLayers
devilstrandDuster=armor("outer",42,10.8,["torso","shoulders","neck","arms","legs"],475)
#HeadLayers
    #FlakHelmets
steelFlakHelmet=armor("head",63,31.5,["head","ears"],260)
bioferriteFlakHelmet=armor("head",77,35,["head","ears"],255)
uraniumFlakHelmet=armor("head",75.6,37.8,["head","ears"],450)
plasteelFlakHelmet=armor("head",79.8,38.5,["head","ears"],575)
    #SpacerHelmets
reconHelmet=armor("head",92,40,["head","eyes","ears","nose","jaw"],525)
marineHelmet=armor("head",106,45,["head","eyes","ears","nose","jaw"],635)
cataphractHelmet=armor("head",120,50,["head","eyes","ears","nose","jaw"],745)
#Middle&OuterLayers
    #SpacerArmor
reconArmor=armor(("middle","outer"),92,40,["torso","neck","shoulders","arms","legs"],1540)
marineArmor=armor(("middle","outer"),106,45,["torso","neck","shoulders","arms","legs"],2035)
cataphractArmor=armor(("middle","outer"),120,50,["torso","neck","shoulders","arms","legs"],3120)

lesserFlakTrooper=outfit((flakVest,devilstrandDuster))
flakTrooper=outfit((devilstrandShirtPants,flakVest,devilstrandDuster,steelFlakHelmet))
flakTrooperMarineHelmet=outfit((devilstrandShirtPants,flakVest,devilstrandDuster,marineHelmet))
premiumFlakTrooper=outfit((hyperweaveShirtPants,flakVest,devilstrandDuster))
spaceMarine=outfit((devilstrandShirtPants,marineHelmet,marineArmor))
spaceMarineNoPantsNoShirt=outfit((marineHelmet,marineArmor))
nudist=outfit(())
#print("SpaceMarineHeadProtection: "+str(spaceMarine.headCoverage))

#print("destruction chance, expected damage, chance to receive damage "+str(gunPenetrate(lesserFlakTrooper.torsoCoverage,gunDict["Revolver"],40)))
#print("destruction chance, expected damage, chance to receive damage "+str(gunPenetrate(flakTrooper.headCoverage,gunDict["Revolver"],10)))
#print("destruction chance, expected damage, chance to receive damage "+str(gunPenetrate(premiumFlakTrooper.torsoCoverage,gunDict["Revolver"],40)))
#print("destruction chance, expected damage, chance to receive damage "+str(gunPenetrate(nudist.headCoverage,gunDict["Revolver"],10)))
#print("destruction chance, expected damage, chance to receive damage "+str(gunPenetrate(spaceMarine.headCoverage,gunDict["Revolver"],10)))
#print("destruction chance, expected damage, chance to receive damage "+str(gunPenetrate(nudist.handsCoverage,gunDict["Revolver"],20)))
#print("destruction chance, expected damage, chance to receive damage "+str(gunPenetrate(nudist.handsCoverage,gunDict["Pila"],20)))

#print("Nudist vs Revolver")
#evaluateOutfit(gunDict["Revolver"],nudist)
#print("\nNudist vs Pila")
#evaluateOutfit(gunDict["Pila"],nudist)
#print("\nNudist vs Charge Lance")
#evaluateOutfit(gunDict["ChargeLance"],nudist)
#print("\n")
#evaluateOutfit(gunDict["BoltActionRifle"],lesserFlakTrooper)
#print("\n")
#evaluateOutfit(gunDict["BoltActionRifle"],flakTrooper)
#print("\n")
#evaluateOutfit(gunDict["BoltActionRifle"],premiumFlakTrooper)
gunOfChoice="ChargeLance"
print("\n\nNowTesting: "+gunOfChoice)
print("\nNudist vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],nudist)
print("\nFlakTrooper vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],flakTrooper)
print("\nFlakTrooperMarineHelmet vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],flakTrooperMarineHelmet)
print("\nSpaceMarineNoPantsNoShirt vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],spaceMarineNoPantsNoShirt)
print("\nSpaceMarine vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],spaceMarine)
gunOfChoice="Revolver"
print("\n\nNowTesting: "+gunOfChoice)
print("\nNudist vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],nudist)
print("\nFlakTrooper vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],flakTrooper)
print("\nFlakTrooperMarineHelmet vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],flakTrooperMarineHelmet)
print("\nSpaceMarineNoPantsNoShirt vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],spaceMarineNoPantsNoShirt)
print("\nSpaceMarine vs "+gunOfChoice)
evaluateOutfit(gunDict[gunOfChoice],spaceMarine)

