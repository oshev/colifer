dir=$PWD
dir="$(basename $dir)"  # Returns last path of directory

if [ $dir = "scripts" ]; then
   cd ..
fi

python colifer/colifer.py --year $(date +%Y) --type weekly --period-num $1