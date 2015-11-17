#!/bin/bash

################################################################
## init_env.sh
##
##   Initializes ENV variables containing
##   Superphy config settings from INI file
## 
##   To run:
##     source init_env.sh
##
##   INI config settings are loaded from path set in ENV variable
##   "SUPERPHY_CONFIGFILE" or from default relative path:
##
##      ../../config/superphy.cfg
##
##   The INI file format supports the following features:
##
##      Sections:   [section]
##      Properties: name=value
##      Comments:   ; comment 
##                  # comment
##
##   Name cannot contain any special characters. See below for 
##   further details on the INI formatting.
##
##   Global variables in the INI file will be exported as:
##   
##     SUPERPHY_${NAME} # variable names will be capitalized
## 
##   Section variables in the INI file will be exported as:
##
##     SUPERPHY_${SECTION}_${NAME} # section and variable names 
##                                 # will be capitalized
##
##
## author = Matt Whiteside
## copyright = Copyright 2015, Public Health Agency of Canada
## license = CC-SY
## version = 4.0
## maintainer = Matt Whiteside
## email = matthew.whiteside@canada.ca
##
################################################################


# Load INI parsing functions
#
# Obtained Nov 17, 2015 from https://github.com/paulchakravarti/ini-parser/blob/master/ini_parser.sh
#
# Introduction
# ------------
#
# Functions for parsing INI-style file natively in bash.
# 
# The INI file format supports the following features:
#
# Sections:   [section]
# Properties: name=value
# Comments:   ; comment 
#             # comment
#
# Blank lines and trailing writespace are ignored as is whitespace around 
# the '=' - ie. 
# 
#    name  =  value
# 
# is equivalent to 
# 
#    name=value
#
# Whitespace and quotes within a value are preserved (though values don't 
# in general need to be quoted and will not be subject to shell parameter 
# splitting)
#
# Values can be continuted onto subsequent lines if these are prefixed with
# whitespace - ie.
#
#    name=line1
#         line2
#
# is equivalent to: 
# 
#    name = line1 line2
#
# Properties are stored in the global SUPERPHY array as ( k1 v1 k2 v2 ... ) with
# keys in the format "<section>.<name>" (properties without an associated
# section are stored as ".<name>". In most cases this is transparent as the
# list/get commands can be used to query the data
#
# The functionality is more or less equivalent to the Python ConfigParser 
# module with the following exceptions
# 
# - Properties are allowed outside sections
# - Multi-line properties are joined with ' ' rather than '\n' (due to shell
#   quoting issues)
#
# Usage
# -----
#
# Given the following ini file (test.ini) -
# 
#   ; A test ini file
#   global = a global value
#   [section1]
#   abc = def ; a comment
#   ghi = jkl
#   [section2]
#   xyz = abc ; extends over two lines
#         def
# 
# Parse config file -
#
# $ parseIniFile < test/t2.ini
#
# $ listKeys
# .global
# section1.abc
# section1.ghi
# section2.xyz
#
# $ listAll
# .global a global value
# section1.abc def
# section1.ghi jkl
# section2.xyz abc def
#
# $ listSection section1
# section1.abc def
# section1.ghi jkl
#
# $ getProperty global
# a global value
#
# $ getProperty section2.xyz
# abc def
#
# $ getPropertyVar XYZ section2.xyz && echo OK
# OK
#
# $ echo ">${XYZ}<"
# >abc def<
#

shopt -s extglob

SUPERPHY=()

# Commands
# --------
#
# parseIniFile < file
#
#   Parse ini file (reads from stdin) and saves data to global SUPERPHY var
#

function parseIniFile() {

    local LINE=""
    local SECTION=""
    local KEY=""
    local VALUE=""

    local IFS=""

    while read LINE 
    do
        LINE=${LINE%%[;#]*}                             # Strip comments
        LINE=${LINE%%*( )}                              # Strip trailing whitespace

        if [[ -n $KEY && $LINE =~ ^[[:space:]]+(.+) ]]  # Continuation - append value
        then
            VALUE+=" ${BASH_REMATCH[1]}"
        else
            if [[ -n $KEY ]]                            # No continuation
            then
                SUPERPHY=(${SUPERPHY[@]} "${SECTION}.${KEY}" "${VALUE}")
                KEY=""
                VALUE=""
            fi

            if [[ $LINE =~ ^\[([[:alnum:]]+)\] ]]       # Section
            then
                SECTION=${BASH_REMATCH[1]}
                KEY=""
            elif [[ $LINE =~ ^([^[:space:]]+)[[:space:]]*=[[:space:]]*(.+) ]] # Property
            then 
                KEY=${BASH_REMATCH[1]}
                VALUE="${BASH_REMATCH[2]}"
            fi
        fi
    done

    if [[ -n $KEY ]]
    then
        SUPERPHY=(${SUPERPHY[@]} "${SECTION}.${KEY}" "${VALUE}")
    fi
}

# listKeys
#
#   List keys present in config file in format "<section>.<property>"
#

function listKeys() {
    local -i i
    for ((i=0; i<${#SUPERPHY[@]}; i+=2))
    do
        echo ${SUPERPHY[i]}
    done
}

# listAll
#
#   List keys and data in format "<section>.<property> <value>"
#

function listAll() {
    local -i i
    for ((i=0; i<${#SUPERPHY[@]}; i+=2))
    do
        echo ${SUPERPHY[i]} ${SUPERPHY[((i+1))]}
    done
}

# exportAll
#
#   export keys and data in format "<SECTION>.<PROPERTY>=<VALUE>"
#   Note: names will be capitalized.
#

function exportAll() {
    local -i i
    for ((i=0; i<${#SUPERPHY[@]}; i+=2))
    do
        VAR="SUPERPHY_${SUPERPHY[i]}"
        VAR=${VAR^^}
        VAR=${VAR//\./_}
        echo "setting $VAR=${SUPERPHY[((i+1))]}"
        export ${VAR}="${SUPERPHY[((i+1))]}"
    done
}

# listSection <section>
#
#   List keys and data for given section (sepcified as $1) in format
#   "<property> <value>"
#

function listSection() {
    local -i i
    local SECTION=$1
    for ((i=0; i<${#SUPERPHY[@]}; i+=2))
    do
        if [[ ${SUPERPHY[$i]} =~ ^${SECTION}\.(.+) ]]
        then
            echo ${SUPERPHY[i]} ${SUPERPHY[((i+1))]}
        fi
    done
}

# getProperty [name|section.name]
#
#   Print value for given property (sepcified as $1) 
#   Properties without a section can be queried directly as
#   "name" (rather than ".name")
#
#   Returns 0 (true) if property found otherwise 1 (false)
#

function getProperty() {
    local -i i
    local KEY=$1
    for ((i=0; i<${#SUPERPHY[@]}; i+=2))
    do
        if [[ ${SUPERPHY[$i]} =~ ^\.?${KEY} ]]
        then
            echo ${SUPERPHY[((i+1))]}
            return 0
        fi
    done
    return 1
}

# getPropertyVar <variable> [name|section.name]
#
#   Save value for given property (sepcified as $2) 
#   into shell variable (specified as $1)
#   Properties without a section can be queried directly as
#   "name" (rather than ".name")
#
#   Returns 0 (true) if property found otherwise 1 (false)
#

function getPropertyVar() {
    local -i i
    local VAR=$1
    local KEY=$2
    for ((i=0; i<${#SUPERPHY[@]}; i+=2))
    do
        if [[ ${SUPERPHY[$i]} =~ ^\.?${KEY} ]]
        then
            local VAL=${SUPERPHY[((i+1))]}
            eval ${VAR}="\${VAL}"
            return 0
        fi
    done
    return 1
}

function testIniParser() {
    echo $ parseIniFile \< test/t2.ini
    parseIniFile < test/t2.ini
    echo $ listKeys
    listKeys
    echo $ listAll
    listAll
    echo $ listSection section1
    listSection section1
    echo $ getProperty global
    getProperty global
    echo $ getProperty section2.xyz
    getProperty section2.xyz
    echo $ getPropertyVar XYZ section2.xyz \&\& echo OK
    getPropertyVar XYZ section2.xyz && echo OK
    echo $ echo ">\${XYZ}<"
    echo ">${XYZ}<"
}

# Check for ENV var or use default
CFGFILE="${SUPERPHY_CONFIGFILE:-../../config/superphy.cfg}"

# Initialize ENV variables
echo "Initializing enviroment using config file: $CFGFILE"
parseIniFile < "$CFGFILE"

# Export to session
exportAll


