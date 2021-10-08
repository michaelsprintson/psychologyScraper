
textValuesDict = {
    # 10 point string
    "MCAT accommodation" : 10,
    "USMLE accommodation" : 10,
    "Step 1 accommodation" : 10,
    "Step 2 accommodation" : 10,
    # 7 point strings
    "Disability" : 7,
    "Disabled" : 7,
    "Medical school" : 7,
    "Medical schools" : 7,
    "Med school" : 7,
    "Med schools" : 7,
    "Medical education" : 7,
    "Med education" : 7,
    "Medical student" : 7,
    "Medical students" : 7,
    "Med student" : 7,
    "Med students" : 7, 
    "#DocsWithDisabilities" : 7,
    "#DisabledDocs" : 7,
    # 3 point strings
    "ADHD" : 3,
    "Anxiety" : 3,
    "Depression" : 3,
    "Autism" : 3,
    "Physical disability" : 3,
    "Chronic illness" : 3,
    "Deaf" : 3,
    "Hard of hearing" : 3,
    "Blind" : 3,
    "Visual impairment" : 3,
    "Mobility impairment" : 3,
    "#MedStudentTwitter" : 3,
    "#MedTwitter" : 3,
    "Accommodation" : 3,
    # 2 point strings
    "Ableism" : 2,
    "Doctor" : 2,
    "Physician" : 2,
    "PGY-1" : 2,
    "PGY-2" : 2,
    "PGY-3" : 2,
    "MS1" : 2,
    "MS2" : 2,
    "MS3" : 2,
    "MS4" : 2,
}

MINIMUM_POINTS = 10

def textPasses(text):
    totalPoints = 0
    for key in textValuesDict:
        if key in text:
            totalPoints += textValuesDict[key]
    return totalPoints > MINIMUM_POINTS