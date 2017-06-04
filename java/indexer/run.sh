#!/bin/sh
abspath=$(cd "$(dirname "$0")"; pwd)
rm -rf $abspath/bin
mkdir $abspath/bin
CLASSPATH=$CLASSPATH:$abspath/lib/*:$abspath/bin
javac -classpath $CLASSPATH -d $abspath/bin $abspath/src/edu/mit/csail/confer/Indexer.java
target=$abspath/../../server/static/conf/$1/data
src=$abspath/../../data/$1
index=$abspath/../../index/$1
rm -rf $index
mkdir $index
export CLASSPATH
java -classpath $CLASSPATH edu.mit.csail.confer.Indexer $src/papers.json $target/offline_recs.json $index