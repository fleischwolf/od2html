#!/usr/bin/python

import sys
import getopt
import re

# lincenced under the GNU Public Licence v3 (or higher)

# FUNCTIONS
# ---------

# getclr:: get different colors for jump-highlighting
def getclr (num):
    pool = ["f57900","edd400","8ae234","4e9a06","729fcf","3465a4","204a87","ad7fa8",
            "75507b","5c3566","ef2929","cc0000","a40000","73d216"]
    return pool[num % len(pool)]


# filterblanks:: kick out empty list entrys in string lists
def filterblanks (redundlist):
    out = []
    for entry in redundlist :
        if entry != '': out.append(entry)
    return out

UNKNOWN_I, DESCR, NO_P, J_MEMORY, J_CODE, U_MEMORY, U_REGISTER, U_ABSOLUTE, U_RELATIVE, B_MEMREG, B_REGMEM, B_REGREG, B_ABSREG, B_MEMMEM, B_ABSMEM, U_ARR, U_ARRN, B_MEMARR, B_MEMARRN, B_MEMREL, B_REGARR, B_REGARRN, B_ABSARR, B_ABSARRN, B_ARRREG, B_ARRMEM, B_ARRARR, B_ARRARRN, B_ARRNREG, B_ARRNMEM, B_ARRNARRN, B_ARRNARR = range(32)

def parseLine (instr):

    # TODO auch die wortlaenge darf <none> sein, wird noch nicht beruecksichtigt
    # (%register)-pointer
    # 4(%register)-basepointer-indexing

    instr = instr.replace("<","&lt;")
    instr = instr.replace(">","&gt;")

    reMemory    = "(0x[a-f0-9]+)"
    reRegister  = "(\%[a-z]+)"
    reAbsolute  = "(\$-*0x[a-f0-9]*)" 
    reRelative  = reAbsolute + "\(" + reRegister + "\)"
    reArrayI    = "\(" + reRegister + "," + reRegister + ",([0-9]+)\)"
    reArrayIn   = "\(," + reRegister + ",([0-9]+)\)"
    linefront   = " *([a-f0-9]+):\t.*\t"
    
    # look for jump instructions
    reJmp       = "(jmp|jae|ja|jbe|jb|jcxz|jc|je|jge|jg|jle|jl|jnae|jna|jnbe|jnc|jne|jnge|jng|jnle|jnl|jno|jnp|jns|jnz|jo|jpe|jpo|jp|js|jz|call)"

    Insjp_code     = re.findall(linefront + reJmp + " *([a-f0-9]+)(.*)",instr)
    Insjp_memory   = re.findall(linefront + reJmp + " *" + reMemory + "(.*)$",instr)    

    # look for other 1-parameter instructions

    # simple
    Insuo_memory   = re.findall(linefront + "([a-z]+) *" + reMemory + "(.*)$",instr)
    Insuo_register = re.findall(linefront + "([a-z]+) *" + reRegister + "(.*)$",instr)
    Insuo_absolute = re.findall(linefront + "([a-z]+) *(\$0x[a-f0-9]*)(.*)$",instr)
    Insuo_relative = re.findall(linefront + "([a-z]+) *" + reRelative + "(.*)$",instr)


    # arrays
    # address(register,register,wordsize)
    Insuo_arr   = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayI + "(.*)$",instr)
    # address(,register,wordsize)
    Insuo_arrN  = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayIn + "(.*)$",instr)


    # ok - this code is clearly written by a lumberjack

    # look for 2-parameter instructions
    Insbo_memmem   = re.findall(linefront + "([a-z]+) *" + reMemory + "," + reMemory + "(.*)$",instr)  
    Insbo_memreg   = re.findall(linefront + "([a-z]+) *" + reMemory + "," + reRegister + "(.*)$",instr)
    Insbo_memarr   = re.findall(linefront + "([a-z]+) *" + reMemory + "," + reMemory + reArrayI + "(.*)$",instr)
    Insbo_memarrn  = re.findall(linefront + "([a-z]+) *" + reMemory + "," + reMemory + reArrayIn + "(.*)$",instr)
    Insbo_memrel   = re.findall(linefront + "([a-z]+) *" + reMemory + "," + reRelative + "(.*)$",instr)


    Insbo_regreg   = re.findall(linefront + "([a-z]+) *" + reRegister + "," + reRegister + "(.*)$",instr)  
    Insbo_regmem   = re.findall(linefront + "([a-z]+) *" + reRegister + "," + reMemory + "(.*)$",instr)
    Insbo_regarr   = re.findall(linefront + "([a-z]+) *" + reRegister + "," + reMemory + reArrayI + "(.*)$",instr)
    Insbo_regarrn  = re.findall(linefront + "([a-z]+) *" + reRegister + "," + reMemory + reArrayIn + "(.*)$",instr)

    Insbo_absreg   = re.findall(linefront + "([a-z]+) *" + reAbsolute + "," + reRegister + "(.*)$",instr)  
    Insbo_absmem   = re.findall(linefront + "([a-z]+) *" + reAbsolute + "," + reMemory + "(.*)$",instr)  
    Insbo_absarr   = re.findall(linefront + "([a-z]+) *" + reAbsolute + "," + reMemory + reArrayI + "(.*)$",instr)
    Insbo_absarrn  = re.findall(linefront + "([a-z]+) *" + reAbsolute + "," + reMemory + reArrayIn + "(.*)$",instr)

    # bug: doesn't recognize arr,reg 
    Insbo_arrreg   = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayI + "," + reRegister + "(.*)$",instr)
    #print linefront + "([a-z]+) *" + reMemory + reArrayI + "," + reRegister + "(.*)$",instr
    Insbo_arrmem   = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayI + "," + reMemory + "(.*)$",instr)
    Insbo_arrarr   = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayI + "," + reMemory + reArrayI + "(.*)$",instr)
    Insbo_arrarrn  = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayI + "," + reMemory + reArrayIn + "(.*)$",instr)


    Insbo_arrnreg  = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayIn + "," + reRegister + "(.*)$",instr)
    Insbo_arrnmem  = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayIn + "," + reMemory + "(.*)$",instr)
    Insbo_arrnarrn = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayIn + "," + reMemory + reArrayIn + "(.*)$",instr)
    Insbo_arrnarr  = re.findall(linefront + "([a-z]+) *" + reMemory + reArrayIn + "," + reMemory + reArrayI + "(.*)$",instr)

    Insnp = re.findall(linefront + "([a-z]+)(.*)$",instr)

    # attention: order is MANDATORY
  
    if Insjp_code :
        return (J_CODE,Insjp_code[0])
    elif Insjp_memory :
        return (J_MEMORY,Insjp_memory[0])

    elif Insbo_memarr :
        return (B_MEMARR,Insbo_memarr[0])
    elif Insbo_memarrn :
        return (B_MEMARRN,Insbo_memarrn[0])

    elif Insbo_regarr :
        return (B_REGARR,Insbo_regarr[0])
    elif Insbo_regarrn :
        return (B_REGARRN,Insbo_regarrn[0])

    elif Insbo_absarr :
        return (B_ABSARR,Insbo_absarr[0])
    elif Insbo_absarrn :
        return (B_ABSARRN,Insbo_absarrn[0])

    elif Insbo_arrreg :
        return (B_ARRREG,Insbo_arrreg[0])
    elif Insbo_arrmem :
        return (B_ARRMEM,Insbo_arrmem[0])
    elif Insbo_arrarr :
        return (B_ARRARR,Insbo_arrarr[0])
    elif Insbo_arrarrn :
        return (B_ARRARRN,Insbo_arrarrn[0])

    elif Insbo_arrnreg :
        return (B_ARRNREG,Insbo_arrnreg[0])
    elif Insbo_arrnmem :
        return (B_ARRNMEM,Insbo_arrnmem[0])
    elif Insbo_arrnarr :
        return (B_ARRNARR,Insbo_arrnarr[0])
    elif Insbo_arrnarrn :
        return (B_ARRNARRN,Insbo_arrnarrn[0])
  
    ############ 
    elif Insuo_arr :
        return (U_ARR,Insuo_arr[0])
    elif Insuo_arrN :
        return (U_ARRN,Insuo_arrN[0])  
    elif Insbo_memreg :
        return (B_MEMREG,Insbo_memreg[0])           
    elif Insbo_regmem :
        return (B_REGMEM,Insbo_regmem[0])
    elif Insbo_absreg :
        return (B_ABSREG,Insbo_absreg[0])
    elif Insbo_absmem :
        return (B_ABSMEM,Insbo_absmem[0])
    elif Insbo_regreg :
        return (B_REGREG,Insbo_regreg[0])
    elif Insbo_memmem :
        return (B_MEMMEM,Insbo_memmem[0])
    elif Insbo_memrel :
        return (B_MEMREL,Insbo_memrel[0])
    elif Insuo_memory :
        return (U_MEMORY,Insuo_memory[0])
    elif Insuo_absolute :
        return (U_ABSOLUTE,Insuo_absolute[0])
    elif Insuo_register :
        return (U_REGISTER,Insuo_register[0])          
    elif Insuo_relative :
        return (U_RELATIVE,Insuo_arr[0])
    elif Insnp :
        return (NO_P,Insnp[0])          
    else :
        return (DESCR,(instr))
    

    
# MAIN::
# read lines from stdin
stdin = sys.stdin
lines = stdin.read().splitlines()

# def
out = []
jumpaddr = {}
fstartpoints = []
jump_oc = ["je","jne","call","jmp","jle"]

# parse lines
for line in lines:

        # parse instructions
        instrP = parseLine(line)
        instrP_type = instrP[0]
        instrP_tokens = instrP[1]

        out.append(instrP)

        # save back-links for jumps
        print instrP, "<br>"
        if instrP_type == J_CODE:
            if not jumpaddr.has_key(instrP_tokens[2]) : # ELEG ?
                jumpaddr[instrP_tokens[2]] = []         # ANCE ?
            jumpaddr[instrP_tokens[2]].append(instrP_tokens[0])                       



# associate color with jump-adress

highlights = {}
for num,key in enumerate(jumpaddr.keys()):
    color = getclr(num)
    highlights[key] = color


# print actual html

print '<html>'
print ' <head>'
print '  <style>'
print '   body {background:#fefefe; font-size:10pt; font-family:monospace;}'
print '   th   {text-align:left;}'
print '   a    {color:black; text-decoration:none;}'
print '   p.linenum {color:#000;font-weight:bold;}'
print '   td {padding-right:10px;}'
print '   th {font-weight:normal;font-size:10pt;}'
print '   span.mnem     {font-weight: bold;}'
print '   span.register {color:#000050;}'
print '   span.abs      {color:#88e032;font-style:italic;}'
print '   span.memory   {color:#b00000;}'
print '   span.tail     {font-weight: bold; font-size:7.5pt; color:#888; font-family:serif;}'
print '   span.descr    {font-weight: bold; font-size:7.5pt; color:#888; font-family:serif;}'
print '  </style>'
print ' </head>'
print ' <body>'

print '  <table>'

for linenum, instrP in enumerate(out):
    print '   <tr>'
    print '    <td>'
    print '     <p class="linenum">' + str(linenum) + '</p>'
    print '    </td>'
    instrP_type = instrP[0]
    instrP_data = instrP[1]
    if instrP_type == DESCR :
        print '    <th colspan="4">'
        print '     <span class="descr">' + instrP_data + '</span>'
        print '    </th>'  
    else : 
        addr        = instrP_data[0]
        mnem        = instrP_data[1]

        # print address and backlinks (if any)
        print '    <td>'
        if addr in jumpaddr.keys():
            print '     <a name="' + addr + '" style="color:#fff;background-color:#' + highlights[addr] + ';">' + addr + '</a>'
            for num,backlink in enumerate(jumpaddr[addr]):
                print '     [<a href="#' + backlink + '">' + str(num) + '</a>]'    
        else :
            print '     <a name="' + addr + '">' + addr + '</a>'
        print '    </td>'

        # print mnem
        print '    <td>'
        print '     <span class="mnem">' + mnem + '</span>'
        print '    </td>'

        print '    <td>'
        # print parameters
        if instrP_type == J_CODE:
            jumpto = instrP_data[2]
            print '     <a href="#' + jumpto + '" style="color:#fff;background-color:',
            print highlights[jumpto] + ';">' + jumpto + '</a>'
        if instrP_type == J_MEMORY:
            jumpto = instrP_data[2]
            print '     <span class="memory">' + jumpto + '</span>'
        if instrP_type == B_MEMREG:
            mem = instrP_data[2]
            reg = instrP_data[3]
            print '     <span class="memory">' + mem + '</span>,',
            print '     <span class="register">' + reg + '</span>' 
        if instrP_type == B_REGREG:
            reg1 = instrP_data[2]
            reg2 = instrP_data[3]
            print '     <span class="register">' + reg1 + '</span>,',
            print '     <span class="register">' + reg2 + '</span>' 
        if instrP_type == B_REGMEM:
            reg = instrP_data[2]
            mem = instrP_data[3]
            print '     <span class="register">' + reg + '</span>,',
            print '     <span class="memory">' + mem + '</span>' 
        if instrP_type == B_ABSREG:
            absn = instrP_data[2]
            reg  = instrP_data[3]
            print '     <span class="abs">' + absn + '</span>,',
            print '     <span class="register">' + reg + '</span>' 
        if instrP_type == B_ABSMEM:
            absn = instrP_data[2]
            mem  = instrP_data[3]
            print '     <span class="abs">' + absn + '</span>,',
            print '     <span class="memory">' + mem + '</span>'
        if instrP_type == B_MEMMEM:
            mem1 = instrP_data[2]
            mem2 = instrP_data[3]
            print '     <span class="memory">' + absn + '</span>,',
            print '     <span class="memory">' + reg + '</span>' 
        if instrP_type == U_REGISTER:
            reg = instrP_data[2]
            print '     <span class="register">' + reg + '</span>',
        if instrP_type == U_MEMORY:
            mem = instrP_data[2]
            print '     <span class="memory">' + mem + '</span>',
        if instrP_type == U_ABSOLUTE:
            absn = instrP_data[2]
            print '     <span class="abs">' + absn + '</span>',
        if instrP_type == U_RELATIVE:
            absn = instrP_data[2]
            reg  = instrP_data[3]
            print '     <span class="abs">' + absn + '</span>',
            print '(<span class="register">' + reg + '</span>)'
        if instrP_type == U_ARR:
            mem       = instrP_data[2]
            offsetreg = instrP_data[3]
            indexreg  = instrP_data[4]
            wordsize  = instrP_data[5]
            print '     <span class="memory">' + mem + '</span>',
            print '(<span class="register">' + offsetreg + '</span>,',
            print '<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'
        if instrP_type == U_ARRN:
            mem       = instrP_data[2]
            indexreg  = instrP_data[3]
            wordsize  = instrP_data[4]
            print '     <span class="memory">' + mem + '</span>',
            print '(,<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'
        if instrP_type == B_MEMARR:
            mem1      = instrP_data[2]
            mem2      = instrP_data[3]
            offsetreg = instrP_data[4]
            indexreg  = instrP_data[5]
            wordsize  = instrP_data[6]
            print '     <span class="memory">' + mem1 + '</span>',
            print '<span class="memory">' + mem2 + '</span>',
            print '(<span class="register">' + offsetreg + '</span>,',
            print '<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'
        if instrP_type == B_MEMARRN:
            mem1      = instrP_data[2]
            mem2      = instrP_data[3]
            indexreg  = instrP_data[4]
            wordsize  = instrP_data[5]
            print '     <span class="memory">' + mem1 + '</span>',
            print '<span class="memory">' + mem2 + '</span>',
            print '(,<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'
        if instrP_type == B_MEMREL:
            mem  = instrP_data[2]
            absn = instrP_data[3]
            reg  = instrP_data[4]
            print '     <span class="memory">' + mem + '</span>',
            print ',<span class="abs">' + absn + '</span>',
            print '(<span class="register">' + reg + '</span>)'
        if instrP_type == B_REGARR:
            reg      = instrP_data[2]
            mem      = instrP_data[3]
            offsetreg = instrP_data[4]
            indexreg  = instrP_data[5]
            wordsize  = instrP_data[6]
            print '     <span class="register">' + reg + '</span>',
            print '<span class="memory">' + mem + '</span>',
            print '(<span class="register">' + offsetreg + '</span>,',
            print '<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'
        if instrP_type == B_REGARRN:
            reg       = instrP_data[2]
            mem       = instrP_data[3]
            indexreg  = instrP_data[4]
            wordsize  = instrP_data[5]
            print '     <span class="register">' + reg + '</span>',
            print '<span class="memory">' + mem + '</span>',
            print '(,<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'
        if instrP_type == B_ABSARR:
            absn     = instrP_data[2]
            mem      = instrP_data[3]
            offsetreg = instrP_data[4]
            indexreg  = instrP_data[5]
            wordsize  = instrP_data[6]
            print '     <span class="abs">' + absn + '</span>',
            print '<span class="memory">' + mem + '</span>',
            print '(<span class="register">' + offsetreg + '</span>,',
            print '<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'
        if instrP_type == B_MEMARRN:
            absn      = instrP_data[2]
            mem       = instrP_data[3]
            indexreg  = instrP_data[4]
            wordsize  = instrP_data[5]
            print '     <span class="abs">' + absn + '</span>',
            print '<span class="memory">' + mem + '</span>',
            print '(,<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>)'

        if instrP_type == B_ARRREG:
            mem       = instrP_data[2]
            offsetreg = instrP_data[3]
            indexreg  = instrP_data[4]
            wordsize  = instrP_data[5]
            reg       = instrP_data[6]
            print '     <span class="memory">' + mem + '</span>',
            print '(<span class="register">' + offsetreg + '</span>,',
            print '<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>),'
            print '<span class="register">' + reg + '</span>'

        if instrP_type == B_ARRMEM:
            mem1      = instrP_data[2]
            offsetreg = instrP_data[3]
            indexreg  = instrP_data[4]
            wordsize  = instrP_data[5]
            mem2      = instrP_data[6]
            print '     <span class="memory">' + mem1 + '</span>',
            print '(<span class="register">' + offsetreg + '</span>,',
            print '<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>),'
            print '<span class="register">' + mem2 + '</span>'

        if instrP_type == B_ARRARR:
            mem1       = instrP_data[2]
            offsetreg1 = instrP_data[3]
            indexreg1  = instrP_data[4]
            wordsize1  = instrP_data[5]
            mem2       = instrP_data[6]
            offsetreg2 = instrP_data[7]
            indexreg2  = instrP_data[8]
            wordsize2  = instrP_data[9]
            print '     <span class="memory">' + mem1 + '</span>',
            print '(<span class="register">' + offsetreg1 + '</span>,',
            print '<span class="register">' + indexreg1 + '</span>,',
            print '<span class="abs">' + wordsize1 + '</span>),'
            print '<span class="memory">' + mem2 + '</span>',
            print '(<span class="register">' + offsetreg2 + '</span>,',
            print '<span class="register">' + indexreg2 + '</span>,',
            print '<span class="abs">' + wordsize2 + '</span>)'

        if instrP_type == B_ARRARRN:
            mem1       = instrP_data[2]
            offsetreg1 = instrP_data[3]
            indexreg1  = instrP_data[4]
            wordsize1  = instrP_data[5]
            mem2       = instrP_data[6]
            indexreg2  = instrP_data[7]
            wordsize2  = instrP_data[8]
            print '     <span class="memory">' + mem1 + '</span>',
            print '(<span class="register">' + offsetreg1 + '</span>,',
            print '<span class="register">' + indexreg1 + '</span>,',
            print '<span class="abs">' + wordsize1 + '</span>),'
            print '<span class="memory">' + mem2 + '</span>',
            print '(,<span class="register">' + indexreg2 + '</span>,',
            print '<span class="abs">' + wordsize2 + '</span>)'

        if instrP_type == B_ARRNREG:
            mem       = instrP_data[2]
            indexreg  = instrP_data[3]
            wordsize  = instrP_data[4]
            reg       = instrP_data[5]
            print '     <span class="memory">' + mem + '</span>',
            print '(,<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>),'
            print '<span class="register">' + reg + '</span>'

        if instrP_type == B_ARRNMEM:
            mem       = instrP_data[2]
            indexreg  = instrP_data[3]
            wordsize  = instrP_data[4]
            mem       = instrP_data[5]
            print '     <span class="memory">' + mem + '</span>',
            print '(,<span class="register">' + indexreg + '</span>,',
            print '<span class="abs">' + wordsize + '</span>),'
            print '<span class="memory">' + mem + '</span>'

        if instrP_type == B_ARRNARRN:
            mem1      = instrP_data[2]
            indexreg1 = instrP_data[3]
            wordsize1 = instrP_data[4]
            mem2      = instrP_data[5]
            indexreg2 = instrP_data[6]
            wordsize2 = instrP_data[7]
            print '     <span class="memory">' + mem1 + '</span>',
            print '(,<span class="register">' + indexreg1 + '</span>,',
            print '<span class="abs">' + wordsize1 + '</span>),'
            print '<span class="memory">' + mem2 + '</span>',
            print '(,<span class="register">' + indexreg2 + '</span>,',
            print '<span class="abs">' + wordsize2 + '</span>),'

        if instrP_type == B_ARRNARR:
            mem1       = instrP_data[2]
            indexreg1  = instrP_data[3]
            wordsize1  = instrP_data[4]
            mem2       = instrP_data[5]
            offsetreg2 = instrP_data[5]
            indexreg2  = instrP_data[6]
            wordsize2  = instrP_data[7]
            print '     <span class="memory">' + mem1 + '</span>',
            print '(,<span class="register">' + indexreg1 + '</span>,',
            print '<span class="abs">' + wordsize1 + '</span>),'
            print '<span class="memory">' + mem2 + '</span>',
            print '(<span class="register">' + offsetreg2 + '</span>',
            print '<span class="register">' + indexreg2 + '</span>,',
            print '<span class="abs">' + wordsize2 + '</span>)'

        tail = instrP_data[len(instrP_data)-1]
        print '    </td>'
        print '    <td>'
        print '     ' + '<span class="tail">' + tail + '</span>'
        print '    </td>'
    
    print '   </tr>'
        
print '  </table>'


print '</body></html>'

print jumpaddr
print fstartpoints
