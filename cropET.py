import psycopg2 as pg
import datetime
from datetime import date
import db
#from cropCoefficients import *
# define crop coefficients
# Unless stated in code -- source for crop coefficients is derived from NRCS values :
# http://irrigationtoolbox.com/ReferenceDocuments/Extension/BCExtension/577100-5.pdf
##########################################
#ALFALFA
KcINI_ALFALFA = 0.4
KcMID_ALFALFA = 1.2
KcEND_ALFALFA = 1.15
#ALMONDS  - Sanden (2007)
KcINI_ALMONDS = 0.69
KcMID_ALMONDS = 1.02
KcEND_ALMONDS = 0.87
#APPLES
KcINI_APPLES = 0.5
KcMID_APPLES = 1.2
KcEND_APPLES = 0.8
#APRICOTS
KcINI_APRICOTS = 0.45
KcMID_APRICOTS = 1.15
KcEND_APRICOTS = 0.85
#ASPARAGUS
KcINI_ASPARAGUS = 0.3
KcMID_ASPARAGUS = 0.95
KcEND_ASPARAGUS = 0.3
#BEANS
KcINI_BEANS = 0.5
KcMID_BEANS = 1.05
KcEND_BEANS = 0.9
# BEETS
KcINI_BEETS = 0.5
KcMID_BEETS = 1.05
KcEND_BEETS = 0.95
#####################
#BERRY
KcINI_BERRY = 0.3
KcMID_BERRY = 1.05
KcEND_BERRY = 0.5
#BLUBERRRY
KcINI_BLUEBERRY = 0.4
KcMID_BLUEBERRY = 1.0
KcEND_BLUEBERRY = 0.75
#RASPBERRY
KcINI_RASPBERRY = 0.4
KcMID_RASPBERRY = 1.2
KcEND_RASPBERRY = 0.75
#STRAWBERRY
KcINI_STRAWBERRY = 0.4
KcMID_STRAWBERRY = 1.05
KcEND_STRAWBERRY = 0.7
######################
#BROCCOLI
KcINI_BROCCOLI = 0.7
KcMID_BROCCOLI = 1.05
KcEND_BROCCOLI = 0.95
#CABBAGE
KcINI_CABBAGE = 0.7
KcMID_CABBAGE = 1.05
KcEND_CABBAGE = 0.95
#CANOLA (Majnooni-Herris et al : https://www.researchgate.net/publication/267408363_Determination_of_single_and_dual_crop_coefficients_and_ratio_of_transpiration_to_evapotranspiration_for_canola
KcINI_CANOLA = 1.03
KcMID_CANOLA = 1.47
KcEND_CANOLA = 0.57
#CARROTS
KcINI_CARROTS = 0.7
KcMID_CARROTS = 1.05
KcEND_CARROTS = 0.95
#CAULIFLOWER
KcINI_CAULIFLOWER = 0.7
KcMID_CAULIFLOWER = 1.05
KcEND_CAULIFLOWER = 0.95
#CELERY
KcINI_CELERY = 0.7
KcMID_CELERY = 1.05
KcEND_CELERY = 0.95
#CEREAL
KcINI_CEREAL = 0.3
KcMID_CEREAL = 1.15
KcEND_CEREAL = 0.25
#CHERRY
KcINI_CHERRY = 0.5
KcMID_CHERRY = 1.2
KcEND_CHERRY = 0.85
#CORN
KcINI_CORN = 0.3
KcMID_CORN = 1.15
KcEND_CORN = 0.4
#CUCUMBER
KcINI_CUCUMBER = 0.6
KcMID_CUCUMBER = 1
KcEND_CUCUMBER = 0.75
# GRAPE
KcINI_GRAPE = 0.3
KcMID_GRAPE = 0.8
KcEND_GRAPE = 0.5
# GREEN ONION
KcINI_GREENONION = 0.7
KcMID_GREENONION = 1.05
KcEND_GREENONION = 0.95
# LETTUCE
KcINI_LETTUCE = 0.7
KcMID_LETTUCE = 1
KcEND_LETTUCE = 0.95
# ONIONS
KcINI_ONION = 0.7
KcMID_ONION = 1.05
KcEND_ONION = 0.95
# PASTURE
KcINI_PASTURE = 0.4
KcMID_PASTURE = 1.0
KcEND_PASTURE = 0.85
# PEAS
KcINI_PEA = 0.5
KcMID_PEA = 1.15
KcEND_PEA = 1.1
#PEPPERS
KcINI_PEPPER = 0.7
KcMID_PEPPER = 1.05
KcEND_PEPPER = 0.85
# POTATO
KcINI_POTATO = 0.5
KcMID_POTATO = 1.15
KcEND_POTATO = 0.75
# RADISH
KcINI_RADISH = 0.7
KcMID_RADISH = 0.9
KcEND_RADISH = 0.85
# SPINACH
KcINI_SPINACH = 0.7
KcMID_SPINACH = 1.05
KcEND_SPINACH = 0.95
# SQUASH
KcINI_SQUASH = 0.5
KcMID_SQUASH = 0.95
KcEND_SQUASH = 0.75
# STONE FRUIT
KcINI_STONEFRUITS = 0.45
KcMID_STONEFRUITS = 1.15
KcEND_STONEFRUITS = 0.85
# TUBERS
KcINI_TUBERS = 0.5
KcMID_TUBERS = 1.05
KcEND_TUBERS = 0.95
# WATERMELON
KcINI_MELON = 0.4
KcMID_MELON = 1
KcEND_MELON = 0.75
#### Crop Coefficients to use fo "SMALL VEGGIE PATCH" aka various plants in patch
#VARIOUS
KcINI_VARIOUS = 0.7
KcMID_VARIOUS = 1.05
KcEND_VARIOUS = 0.95
##########################################
########### END COEFFICIENT LIST #########

def calculateCropCoef(deviceName):
    #POSTGRES CONNECTION
    conn = db.connect()
    cur = conn.cursor()
    #deviceName = '0212BC9'
    deviceName = deviceName.lower()
    SQL = "SELECT b.crop, b.id FROM blocks b JOIN probes p ON b.id = p.assoc_with_block WHERE p.serial_code LIKE '%" + str(deviceName) + "';"
    cur.execute(SQL)
    rows = cur.fetchall()
    if len(rows) < 1:
        return None

    [cropName, fieldID] = rows[0]
    print(f"field={fieldID} has cropName={cropName}")
    # make caps
    cropName = cropName.upper()
    print(cropName)

    #Crop Coefficient Selector

    #weird error handling for person who put their name as crop type :)
    if cropName == "GRAHAM BUNCKENBURH":
        cropName = "POTATO"

    # load current date with datetime
    today = date.today()
    print(today)

    now = datetime.datetime.now()
    print(now)
    month = now.month
    day = now.day
    print("Month: " + str(month))
    print("Day: " + str(day))

    ###ALFALFA###

    if cropName == "ALFALFA":
        KcINI = KcINI_ALFALFA
        KcMID = KcMID_ALFALFA
        KcEND = KcEND_ALFALFA
        print("Crop type is ALFALFA for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###APPLES###

    elif cropName == "APPLES" or cropName == "APPLE":
        KcINI = KcINI_APPLES
        KcMID = KcMID_APPLES
        KcEND = KcEND_APPLES
        print("Crop type is APPLES for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###APRICOTS###

    elif cropName == "APRICOTS" or cropName == "APRICOT":
        KcINI = KcINI_APRICOTS
        KcMID = KcMID_APRICOTS
        KcEND = KcEND_APRICOTS
        print("Crop type is APRICOTS for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###ASPARAGUS###

    elif cropName == "ASPARAGUS":
        KcINI = KcINI_ASPARAGUS
        KcMID = KcMID_ASPARAGUS
        KcEND = KcEND_ASPARAGUS
        print("Crop type is ASPARAGUS for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 6:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 6:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###BEANS###

    elif cropName == "BEANS" or cropName == "GREENBEANS" or cropName == "GREEN BEANS":
        KcINI = KcINI_BEANS
        KcMID = KcMID_BEANS
        KcEND = KcEND_BEANS
        print("Crop type is BEANS for field " + str(fieldID))

        if month <= 4:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 4 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###BEETS###

    elif cropName == "BEETS" or cropName == "BEET":
        KcINI = KcINI_BEETS
        KcMID = KcMID_BEETS
        KcEND = KcEND_BEETS
        print("Crop type is BEETS for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month <= 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ### BERRIES #############################

    elif cropName == "BERRY" or cropName == "BLACKBERRY" or cropName == "BERRIES" or cropName == "CURRANT":
        KcINI = KcINI_BERRY
        KcMID = KcMID_BERRY
        KcEND = KcEND_BERRY
        print("Crop type is BERRIES for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    elif cropName == "BLUEBERRY" or cropName == "BLUEBERRIES":
        KcINI = KcINI_BLUEBERRY
        KcMID = KcMID_BLUEBERRY
        KcEND = KcEND_BLUEBERRY
        print("Crop type is BLUEBERRY for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    elif cropName == "RASPBERRY" or cropName == "RASPBERRIES":
        KcINI = KcINI_RASPBERRY
        KcMID = KcMID_RASPBERRY
        KcEND = KcEND_RASPBERRY
        print("Crop type is RASPBERRY for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    elif cropName == "STRAWBERRY" or cropName == "STRAWBERRIES":
        KcINI = KcINI_STRAWBERRY
        KcMID = KcMID_STRAWBERRY
        KcEND = KcEND_STRAWBERRY
        print("Crop type is STRAWBERRY for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #######################################

    ###BROCCOLI###

    elif cropName == "BROCCOLI":
        KcINI = KcINI_BROCCOLI
        KcMID = KcMID_BROCCOLI
        KcEND = KcEND_BROCCOLI
        print("Crop type is BROCCOLI for field " + str(fieldID))

        if month <= 2:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 2 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###CABBAGE###

    elif cropName == "CABBAGE":
        KcINI = KcINI_CABBAGE
        KcMID = KcMID_CABBAGE
        KcEND = KcEND_CABBAGE
        print("Crop type is CABBAGE for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###CARROTS###

    elif cropName == "CARROT" or cropName == "CARROTS":
        KcINI = KcINI_CARROTS
        KcMID = KcMID_CARROTS
        KcEND = KcEND_CARROTS
        print("Crop type is CARROTS for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###CAULIFLOWER###

    elif cropName == "CAULIFLOWER":
        KcINI = KcINI_CAULIFLOWER
        KcMID = KcMID_CAULIFLOWER
        KcEND = KcEND_CAULIFLOWER
        print("Crop type is CAULIFLOWER for field " + str(fieldID))

        if month <= 2:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 2 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###CANOLA###

    elif cropName == "CANOLA":
        KcINI = KcINI_CANOLA
        KcMID = KcMID_CANOLA
        KcEND = KcEND_CANOLA
        print("Crop type is CANOLA for field " + str(fieldID))

        if month <= 4:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 4 and month < 7:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 7:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###CELERY###

    elif cropName == "CELERY":
        KcINI = KcINI_CELERY
        KcMID = KcMID_CELERY
        KcEND = KcEND_CELERY
        print("Crop type is CELERY for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 4 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###CEREAL###################

    elif cropName == "CEREAL" or cropName == "OAT" or cropName == "OATS" or cropName == "WHEAT" or cropName == "GRASS" \
        or cropName == "RICE" or cropName == "BARLEY" or cropName == "BARLEY, FORAGE" or cropName == "BUCKWHEAT" \
        or cropName == "SORGHUM" or cropName == "MILLET" or cropName == "BARLEY, MALT BARLEY" \
        or cropName == "SORGHUM, GRAIN SORGHUM" or cropName == "RYEGRASS" or cropName == "RYEGRASS, PERENNIAL" \
        or cropName == "RYEGRASS, ANNUAL" or cropName == "WHEATGRASS" or cropName == "WILDRYE, BEARDLESS" or cropName == "WHEATGRASS TALL" \
        or cropName == "WHEAT, DURUM" or cropName == "WHEATGRASS, FAIRWAY CRESTED" or cropName == "WHEAT, SPRING":
        KcINI = KcINI_CEREAL
        KcMID = KcMID_CEREAL
        KcEND = KcEND_CEREAL
        print("Crop type is CEREAL for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ## CEREAL - WINTER WHEAT (DIFFERENT SEASONAL PARAMETERS"
    elif cropName == "WHEAT, WINTER":
        KcINI = KcINI_CEREAL
        KcMID = KcMID_CEREAL
        KcEND = KcEND_CEREAL
        print("Crop type is WINTER WHEAT for field " + str(fieldID))

        if month >= 8 and month <= 10:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 10 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5 and month < 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ##################################

    ###CHERRY###
    elif cropName == "CHERRY" or cropName == "CHERRIES":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_CHERRY
        KcMID = KcMID_CHERRRY
        KcEND = KcEND_CHERRY
        print("Crop type is CHERRY for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ###CORN###
    elif cropName == "CORN" or cropName == "SWEET CORN" or cropName == "SWEETCORN" or cropName == "MAIZE":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_CORN
        KcMID = KcMID_CORN
        KcEND = KcEND_CORN
        print("Crop type is CORN for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ### CUCUMBER
    elif cropName == "CUCUMBER" or cropName == "CUCUMBERS":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_CUCUMBER
        KcMID = KcMID_CUCUMBER
        KcEND = KcEND_CUCUMBER
        print("Crop type is CUCUMBER for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    ## GRAPES
    elif cropName == "GRAPE" or cropName == "GRAPES" or cropName ==  "GRAPE, TABLE":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_GRAPE
        KcMID = KcMID_GRAPE
        KcEND = KcEND_GRAPE
        print("Crop type is GRAPE for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    # GREEN ONIONS
    elif cropName == "GREEN ONION" or cropName == "GREEN ONIONS":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_GREENONION
        KcMID = KcMID_GREENONION
        KcEND = KcEND_GREENONION
        print("Crop type is GREENONION for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 7:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 7:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    # LETTUCE
    elif cropName == "LETTUCE":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_LETTUCE
        KcMID = KcMID_LETTUCE
        KcEND = KcEND_LETTUCE
        print("Crop type is LETTUCE for field " + str(fieldID))

        if month <= 7:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 7 and month < 9:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 9:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #ONION
    elif cropName == "ONION" or cropName == "ONIONS":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_ONION
        KcMID = KcMID_ONION
        KcEND = KcEND_ONION
        print("Crop type is ONION for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 7:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 7:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))
    #PASTURE
    elif cropName == "PASTURE" or cropName == "GRASS":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_PASTURE
        KcMID = KcMID_PASTURE
        KcEND = KcEND_PASTURE
        print("Crop type is PASTURE for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 7:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 7:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #PEAS
    elif cropName == "PEA" or cropName == "PEAS" or cropName == "SNAP PEA" or cropName == "SNAP PEAS":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_PEA
        KcMID = KcMID_PEA
        KcEND = KcEND_PEA
        print("Crop type is PEA for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #PEPPER
    elif cropName == "PEPPER" or cropName  == "PEPPERS" or cropName == "SWEET PEPPER" or \
        cropName == "SWEEET PEPPERS" or cropName == "JALAPEÑO" or cropName == "HABANERO PEPPER":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_PEPPER
        KcMID = KcMID_PEPPER
        KcEND = KcEND_PEPPER
        print("Crop type is PEPPER for field " + str(fieldID))

        if month <= 4:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 4 and month < 7:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 7:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))


    #POTATO
    elif cropName == "POTATO" or cropName == "POTATOES" or cropName == "SWEET POTATO" or cropName == "SWEET POTATOES":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_POTATO
        KcMID = KcMID_POTATO
        KcEND = KcEND_POTATO
        print("Crop type is POTATO for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 6:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 6:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #PUMPKIN
    elif cropName == "PUMPKIN" or cropName == "PUMPKINS":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_PUMPKIN
        KcMID = KcMID_PUMPKIN
        KcEND = KcEND_PUMPKIN
        print("Crop type is PUMPKIN for field " + str(fieldID))

        if month <= 6:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 6 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #RADISH
    elif cropName == "RADISH" or cropName == "RADISHES":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_RADISH
        KcMID = KcMID_RADISH
        KcEND = KcEND_RADISH
        print("Crop type is RADISH for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #SPINACH
    elif cropName == "SPINACH":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_SPINACH
        KcMID = KcMID_SPINACH
        KcEND = KcEND_SPINACH
        print("Crop type is SPINACH for field " + str(fieldID))

        if month <= 3:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 3 and month < 5:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 5:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #SQUASH
    elif cropName == "SQUASH":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_SPINACH
        KcMID = KcMID_SPINACH
        KcEND = KcEND_SPINACH
        print("Crop type is SPINACH for field " + str(fieldID))

        if month <= 6:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 6 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #STONEFRUITS
    elif cropName == "STONE FRUIT" or cropName == "STONEFRUITS" or cropName == "PLUM" or cropName == "PLUMS" or \
        cropName == "NECTARINE" or cropName == "NECTARINES" or cropName == "MANGO" or cropName == "MANGOES":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_STONEFRUITS
        KcMID = KcMID_STONEFRUITS
        KcEND = KcEND_STONEFRUITS
        print("Crop type is STONE FRUIT for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #TUBERS
    elif cropName == "TUBER" or cropName == "TUBERS" or cropName == "YAM" or cropName == "YAMS" or \
        cropName == "TARO" or cropName == "JERUSALEM ARTICHOKE" or cropName == "CROSNE" or cropName == "JICAMA":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_TUBERS
        KcMID = KcMID_TUBERS
        KcEND = KcEND_TUBERS
        print("Crop type is TUBER for field " + str(fieldID))

        if month <= 4:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 4 and month < 6:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 6:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    #WATERMELON
    elif cropName == "WATERMELON" or cropName == "MELON" or cropName == "MELONS" or cropName == "CANTALOUPE":
        # apply crop Coefficient - beginning - middle - end of plant growth stages
        KcINI = KcINI_MELON
        KcMID = KcMID_MELON
        KcEND = KcEND_MELON
        print("Crop type is MELON for field " + str(fieldID))

        if month <= 5:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 5 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))

    else:
        # in case of no crop identified, default to average values for "Small Vegetable Patch"
        KcINI = KcINI_VARIOUS
        KcMID = KcMID_VARIOUS
        KcEND = KcEND_VARIOUS
        print("No single crop found --> Defaulting to Various Veggie Patch crop coefficients")
        if month <= 6:
            print("Early Growth Stage for " + str(cropName))
            # apply crop coeefficient to use
            KcMAIN = KcINI
            print("Crop Coefficient: " + str(KcMAIN))
        elif month > 6 and month < 8:
            print("Mid Growth Stage for " + str(cropName))
            KcMAIN = KcMID
            print("Crop Coefficient: " + str(KcMAIN))
        elif month >= 8:
            print("Late Growth Stage for " + str(cropName))
            KcMAIN = KcEND
            print("Crop Coefficient: " + str(KcMAIN))


    return {
        "KcMAIN":  KcMAIN,
        "cropName": cropName
    }
