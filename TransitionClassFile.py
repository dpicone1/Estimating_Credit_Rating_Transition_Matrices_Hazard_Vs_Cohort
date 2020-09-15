import pandas as pd
import numpy  as np
import datetime as dt
 
# the default rating symbol is D
# the default rating index  is 7

# the NR rating symbol is NR
# the NR rating index  is 8        

# There are 8 initial states AAA, AA, A, BBB, BB, B, CCC, D
# and 9 final states         AAA, AA, A, BBB, BB, B, CCC, D, NR
        
class TransitionClass(object):
    def __init__(self, Dati, yend):
        
        #Dati is a dataframe containing the info to be processed
        #yend  is final year of the analysis
        self.MyDati = Dati        
        self.MyDati = self.MyDati.copy()
        
        self.MyDati['Year']     = pd.DatetimeIndex(self.MyDati['Date']).year                
        self.MyDati['TimeDiff'] = self.MyDati['Date'].diff()
        
        self.defautYes = False #The general status is that the loan/bond has not defaulted for the cohort model
        self.NRYes     = False #The general status is that the loan/bond is not NR for the cohort model
        
        self.DefaultedCheck()# check if the data contains a default
        self.NRCheck()       # check if the data contains a NR
            
        self.size      = len(self.MyDati)
        self.yend      = yend
        self.ybeg      = (self.MyDati.iloc[0].Date).year
        
            
    def DefaultedCheck(self):
        # Is there a default?
        self.defaulted     = self.MyDati[self.MyDati['RatingSymbol'] == 'D']        
        self.defaultedSize = len(self.defaulted)
        
        if (self.defaultedSize > 0):
            
            # remove all the data after the obligor has defaulted            
            DefaultDate = self.MyDati[self.MyDati['RatingSymbol'] == 'D']
            date = DefaultDate.iloc[0].Date
            self.MyDati = self.MyDati.drop(self.MyDati[self.MyDati['Date'] > date].index)            
            
            # After removing all addtional data after defaut, 
            # we should have only one defaulted record, the first one
            self.defaulted     = self.MyDati[self.MyDati['RatingSymbol'] == 'D']        
            self.defaultedSize = len(self.defaulted)        
            self.defaultyear = self.defaulted.iloc[0].Year
            self.defaultYes  = True
                                    
    def NRCheck(self):
        # Is there a NR without a previous Default?
        self.NRSize = 0
        self.NR     = self.MyDati[self.MyDati['RatingSymbol'] == 'NR']        
                
        if (len(self.NR) > 0 & self.defaultedSize == 1): # Remove the NR record. We do not need it as we stop
            # as soon as the borrower defaults
            self.MyDati = self.MyDati.drop(self.MyDati[self.MyDati['RatingSymbol'] == 'NR'].index)
            
        if (len(self.NR) > 0 & self.defaultedSize == 0): # only if there is no default, otherwise the default will
            # overseed and stop the algo as soon as there is a default event
            
            # The obligor might have several NR or after an NR status might come a rating from AAA to C. 
            # We remove all the data after the first NR.
            
            NRDate = self.MyDati[self.MyDati['RatingSymbol'] == 'NR']
            date = NRDate.iloc[0].Date
            self.MyDati = self.MyDati.drop(self.MyDati[self.MyDati['Date'] > date].index)            
            
            # After removing all addtional NR, we should have only one NR record, the oldest one
            self.NR     = self.MyDati[self.MyDati['RatingSymbol'] == 'NR']            
            self.NRSize = len(self.NR)        
            self.NRyear = self.NR.iloc[0].Year
            self.NRYes  = True
            
    def Cohort(self):
        
        self.RatingsBeg = [self.MyDati.iloc[0].RatingSymbol] # containing the rating symbol at the beginning of the period
        self.RatingsEnd = []                                 # containing the rating symbol at the end of the period

        self.RatingsBegIndex = [self.MyDati.iloc[0].RatingNumber]# containing the rating index at the beginning of the period
        self.RatingsEndIndex = []                                # containing the rating index at the end of the period
                    
        if   (self.defaultedSize == 1):
            finalYear = min(self.yend, self.defaultyear)
        elif (self.NRSize > 0):
            finalYear = min(self.yend, self.NRyear)       
        else:
            finalYear = self.yend
        
        for i in range(self.ybeg, finalYear + 1):
                            
            self.MyDatiLoop = self.MyDati[self.MyDati['Year'] == i]
            
            if(len(self.MyDatiLoop) > 0):
                dateCond         = max(self.MyDatiLoop.Date)
                self.MyDatiLoop2 = self.MyDatiLoop[self.MyDatiLoop['Date'] == dateCond]
                self.RatingsEnd.append(self.MyDatiLoop2.iloc[0].RatingSymbol)
                self.RatingsEndIndex.append(self.MyDatiLoop2.iloc[0].RatingNumber)

            else:
                self.RatingsEnd.append(self.MyDatiLoop2.iloc[0].RatingSymbol)
                self.RatingsEndIndex.append(self.MyDatiLoop2.iloc[0].RatingNumber)
                
            self.RatingsBeg.append(self.MyDatiLoop2.iloc[0].RatingSymbol)
            self.RatingsBegIndex.append(self.MyDatiLoop2.iloc[0].RatingNumber)
            
            if(self.RatingsEnd[-1] == 'D' or self.RatingsEnd[-1] == 'NR' ):
                break
                        
        if(self.defautYes):
            self.RatingsEnd[-1]      = 'D'
            self.RatingsEndIndex[-1] = 7
        
        if(self.NRYes):
            self.RatingsEnd[-1]      = 'NR'
            self.RatingsEndIndex[-1] = 8
        
        self.RatingsBeg      = self.RatingsBeg[:-1]
        self.RatingsBegIndex = self.RatingsBegIndex[:-1]
      
    def CohortTransitionMatrix(self):
        self.TransMatrix = np.zeros([8, 9])
        self.TransDen    = np.zeros([8])
        
        for i in range(len(self.RatingsEndIndex)):
            self.TransMatrix[self.RatingsBegIndex[i], self.RatingsEndIndex[i]] +=1
            self.TransDen[self.RatingsBegIndex[i]] +=1
            
    def HazardModel(self):
        
        self.TransDenLambda  = np.zeros([8]) # containing the denominator Hazard Model
        
        self.DefaultYesHazard = False

        for i in range(1, self.size):

            valore = self.MyDati.iloc[i].TimeDiff.days / 365
            self.TransDenLambda[self.MyDati.iloc[i - 1].RatingNumber] += valore
        
            if (self.MyDati.iloc[i].RatingSymbol == 'D' or self.MyDati.iloc[i].RatingSymbol == 'NR'):
                self.DefaultYesHazard = True
                break
        
        #first period
        dbeg = dt.date(self.MyDati.iloc[0].Year, 1, 1)
        valoreBeg = (self.MyDati.iloc[0].Date - dbeg).days/365.0
        self.TransDenLambda[self.MyDati.iloc[0].RatingNumber] += valoreBeg
        
        # Last Period Analysis
        dfinal = dt.date(self.yend, 12, 31)
        if(self.DefaultYesHazard == False):
            valoreEnd = (dfinal - self.MyDati.iloc[self.size - 1].Date).days/365.0
            self.TransDenLambda[self.MyDati.iloc[self.size - 1].RatingNumber] += valoreEnd