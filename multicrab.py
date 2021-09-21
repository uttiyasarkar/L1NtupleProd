#from WMCore.Configuration import Configuration

from CRABClient.UserUtilities import config
import datetime,sys,os

# This multicrab script is written for L1T TEA shifters to produce Ntuples.
# Last updated: 9.5.2018
config = config()

##############################
### CHANGE THESE SETTINGS: ###
##############################

week_number = 'Fill_6960_54' # two-digit week number, e.g. "01" for the first week of the year
integration_tag='v105p13' # use the tag that was applied in setting up CMSSW, see https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideL1TStage2Instructions#Environment_Setup_with_Integrati
cmssw_version='11_2_0'  # check that this corresponds to the version you are using at the moment
era = "2018C"  # data era

dryRun= False
#dryRun= True # NB! when True, jobs are NOT submitted (for testing only)
NJOBS = -1  # limit total numbers of events processed, normally you should run with -1 (== all events)
runNumbers = [320038,320039,320040]
#runNumbers = [320058,320059,320060,320061,320062,320063,3200064,320065]
#runNumbers = [320023,320024,320025,320026]
#runNumbers = [320002,320003,320004,320005,320006,320007,320008,320009,320010,320011,320012] # run numbers for L1Ntuple production, prererably all runs from one fill
#config.Site.whitelist = ["T2_CH*"] # force jobs to run on certain Tier 2 

### Choose one of these three workflows (and comment out other two):
workflow='ZeroBias'
#workflow='NanoDST'
#workflow='NanoEMU'

#####################################
### END OF SETTINGS TO BE CHANGED ###
#####################################

# Do NOT change these settings unless you are asked to do so by L1T experts:

Nunits = 20
RunOnMC = False
if (RunOnMC):
  Nunits=2
useJSON = False
WriteToCERN = True # Writes the output files to L1T EOS space (/store/group/dpg_trigger/comm_trigger/L1Trigger/TEAshiftNtuples)
useParent=False # allows to run over the related parent files too, e.g., gives access to the RAW data while running over a RECO sample

# Make sure that integration tag has p's instead of dots
integration_tag.replace(".","p")

# Find the correct json file

if "2015" in era:
  JSON='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Reprocessing/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON.txt'
elif "2016" in era:
  JSON='/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/DCSOnly/json_DCSONLY.txt'
elif "2017" in era:
  JSON='/afs/cern.ch/user/d/deguio/public/Certification/Cert_13TeV_2017_HCAL_DCS_GOOD.txt'
elif "2018" in era:
  JSON=''
else:
  sys.exit('%ERROR: Era can be 2015, 2016, 2017 or 2018.')  

# Set the corect PSet according to the workflow

if workflow == 'ZeroBias':
  pSet = 'l1NtupleRAWEMU_2018_RAW2DIGI.py'
  JOBID = 'ZeroBias'+str(era)+'-week'+str(week_number) +'-l1t-integration-'+integration_tag+'-CMSSW-'+cmssw_version

elif workflow== 'NanoDST':
  pSet = 'l1Ntuple_NANO.py'
  JOBID = 'NanoDST'+str(era)+'-week'+str(week_number) +'-l1t-integration-'+integration_tag+'-CMSSW-'+cmssw_version

elif workflow== 'NanoEMU':
  pSet = 'l1Ntuple_NANOEMU.py'
  JOBID = 'NanoEMU'+str(era)+'-week'+str(week_number) +'-l1t-integration-'+integration_tag+'-CMSSW-'+cmssw_version  

print('Nutples will appear in subdiretory '+JOBID)

# Dataset definitions


# Add runs automatically, based on runNumbers list defined in the beginning of file
logbase="Run%s_ZeroBias_noRECO"%era
myJobs={}
dataset = ""
if "Nano" in workflow:
    dataset = "L1Accept"
else:
    dataset = "ZeroBias"    
for runNumber in runNumbers:
    myJobs["%d_%s_Run%s-v1"%(runNumber,dataset,era)] = ["/%s/Run%s-v1/RAW"%(dataset,era),Nunits,runNumber]
#    myJobs["%d_%s_Run%s-v1"%(runNumber,dataset,era)] = ["/ZeroBias/Run2018C-v1/RAW",Nunits,319910,319914,319941]
### ADD DATASETS MANUALLY HERE IF NEEDED ###
# If you want to ignore runNumber list and set the datasets/runs manually, uncomment
# the three lines above and instead use this syntax for defining the datasets:
# myJobs={
# "<name of the dataset in output> : [<[path to dataset>", Nunits, <runs consireded, -1 == all runs>],\
# ... (you can add as many rows as you want) ...
# }
# Example:
# "315506" + "_ZeroBias_Run2018A-v1":["/ZeroBias/Run2018A-v1/RAW",Nunits,315506],\
### END OF DATASET SETTINGS ###

# Job splitting and writing settings
splitting   = 'LumiBased'
theSample = "Data"
if RunOnMC :
    splitting   = 'FileBased'
    theSample = "MC"

if WriteToCERN:
    StorageSite = 'T2_CH_CERN'
    output      = '/store/group/dpg_trigger/comm_trigger/L1Trigger/uttiya/' + JOBID
# Common for all jobs:
config.JobType.allowUndistributedCMSSW = True
config.section_('General')
config.General.transferOutputs = True
config.General.transferLogs = True
config.General.workArea = logbase + '_' + str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
config.section_('JobType')
config.JobType.psetName = pSet
config.JobType.pluginName = 'Analysis'
config.JobType.maxMemoryMB = 2500
config.JobType.outputFiles = ['L1Ntuple.root']
config.section_('Data')
config.Data.ignoreLocality = False # allows jobs to run at any site
config.Site.blacklist = ['T2_FR_GRIF_LLR']
config.Data.inputDBS = 'global'
config.Data.splitting = splitting
config.Data.unitsPerJob = 10
## config.Data.totalUnits = 1
config.Data.useParent = useParent
config.Data.outLFNDirBase = output
config.Data.runRange = ''

if (RunOnMC): useJSON=False

if useJSON :
  config.Data.lumiMask = JSON

config.section_('Site')
config.Site.storageSite = StorageSite

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from CRABClient.ClientExceptions import ClientException
    from httplib import HTTPException
    from multiprocessing import Process

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException as hte:
            print "Failed submitting task: %s" % (hte.headers)
        except ClientException as cle:
            print "Failed submitting task: %s" % (cle)

    if not os.path.exists(pSet):
      print "\nConfiguration file ",pSet,"does not exist.  Aborting..."
      sys.exit(1)

    if useJSON and (not os.path.exists(JSON)):
      print "\nJSON file ",JSON,"does not exist.  Aborting..."
      sys.exit(1)

    print "\n"
    print "About to submit a multicrab job for the following workflow:\n"
    print "\tConfig file:\t",pSet,"\tWorkflow:\t",workflow
    print "\tData or MC:\t",theSample
    print "\tStorage site:\t",StorageSite
    print "\tOutput dir:\t",output,"\n"

    for job in myJobs.keys():
        jobPars=myJobs[job]
        print "\t",job, jobPars
    print "\n"

    cont=raw_input('Press return to continue. Any other key to abort...\n')
    if 0 < len(cont):
        sys.exit(1)

    i=0
    for job in myJobs.keys():

        jobPars=myJobs[job]
        i=i+1
        print "\nSubmitting job ",i," of ",len(myJobs.keys()),":\t",job, jobPars

        config.General.requestName = JOBID + "__" + job
        config.Data.inputDataset = jobPars[0]
        config.Data.unitsPerJob = jobPars[1]
        if NJOBS>0 :
          config.Data.totalUnits = config.Data.unitsPerJob * NJOBS

        if jobPars[2] != -1:
            config.Data.runRange = str(jobPars[2])

        print config
        if not dryRun:
          p = Process(target=submit, args=(config,))
          p.start()
          p.join()
