from binascii import hexlify

'''
This is a ghidra script meant to be executed from the script manager
I really don't know shit about Ghidra API this is my first attempt at using it
Also, this doesnt print the full flag due to the way the program is executed
I just didnt feel like scripting out the rest.. You can determine the rest of the flag by examining
the LEA and MOV instructions printed from the script
'''

listing = currentProgram.getListing()
main_func = getGlobalFunctions("check_flag")[0]
addrSet = main_func.getBody()
codeUnits = listing.getCodeUnits(addrSet, True) # true means 'forward'

flag = ""
for codeUnit in codeUnits:
    if codeUnit.toString().startswith("LEA"):
        print(codeUnit.toString())
        try:
            x = toAddr(int(codeUnit.toString().split("[")[1].strip("]"), 16)+4)
            flag += chr(getByte(x))
        except:
            continue
    elif codeUnit.toString().startswith("MOV"):
        print(codeUnit.toString())

print(flag)

