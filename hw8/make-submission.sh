#!/bin/bash

files="*.php *.xml README.txt *.css"
name="huhnx025_hw08"

mkdir -p $name
cp $files $name
zip -r $name $name
rm -rf $name
