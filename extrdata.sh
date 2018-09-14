#!/bin/bash
[ -z "$*" ]&& exit

[ -z "$1" ]&& exit

pattern_start="$2"
[ -z "$2" ]&& exit

pattern_end="$3"
[ -z "$3" ]&& exit

datadir=./data/

echo "Extracting data between stamps ${pattern_start} and ${pattern_end}"

fn1=`echo $1 | gawk '{gsub(/\.log/,"",$0); print $0}'`
fn2=`echo $2 | gawk '{gsub(/-|:|-0400/,"",$0); print $0}'`
filename="$fn1-${fn2}.txt"

if [ -s $1 ]; then
  cat $1 \
  | gawk -v pat_s=${pattern_start} -v pat_e=${pattern_end} -v fn=${datadir}${filename}\
    'BEGIN {p=0}; \
     { \
        if ( match($0, pat_s)) {p=1;}; \
        if ( match($0, pat_e)) {p=0;}; \
        if(p == 1) { if (match($2, "INFO") && (match($3,"0.0")!=1)) print $1,$3 >> fn;};\
     }; \
     END {print p}'
fi

