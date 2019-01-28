version=
build=
show=
update=
add=
build=
make=
pull=
push=
gitshow=
gitupdate=

changelog=$(dirname $0)/ChangeLog


while getopts "sbahurmptgz" opt; 
do
  case "$opt" in
    s) show="y"
      ;;
    b) build="y"
      ;;
    h) echo "Usage: ./version.sh -s/a/r/u/p/t/g/z"
       echo "-s: show current version"
       echo "-a or -r: add or release a new version"
       echo "-u: update all files with the most updated version"
       echo "-m: update build no, *this should not be called manually*"
       echo "-p: update monster infrastructure"
       echo "-t: push subtree back to warehouse"
       echo "-g: show git head"
       echo "-z: update git head"
       exit 1 
       ;;
    a) add="y"
      ;;
    u) update="y"
      ;;
    r) add="y"
      ;;
    m) make="y"
      ;;
    p) pull="y"
      ;;
    t) push="y"
      ;;
    g) gitshow="y"
      ;;
    z) gitupdate="y"
      ;;
  esac
done

if [[ -z $add ]] && [[ -z $gitshow ]] && [[ -z $gitupdate ]]  && [[ -z $update ]] && [[ -z $show ]] && [[ -z $build ]] && [[ -z $make ]] && [[ -z $push ]] && [[ -z $pull  ]]
then
    echo "Usage: ./version.sh -s/a/r/u/p/t"
    echo "-s: show current release version"
    echo "-a or -r : add or release a new version"
    echo "-b: show current build version"
    echo "-u: update all files with the most updated version"
    echo "-m: update build no, *this should not be called manually*"
    echo "-p: update monster infrastructure"
    echo "-g: acquire git head"
    echo "-z: update git head"
    echo "-t: push subtree back to warehouse"
    exit 1 
fi

line_num=0

while read line
do
  line_num=$((line_num+1))
  name=$(echo $line|tr -s " ")
  first_character=${name:0:1}
  if [ "$first_character" == "@" ];then
    name=${name:2:${#name}-3}
    version=$name
    break
  elif [ "$first_character" == "%" ];then
    name=${name:7:${#name}-8}
    buildno=$name
  fi
done < $changelog

if [[ ! -z $show ]]; then
  printf $version
  exit 0
fi


if [[ ! -z $build ]]; then
  printf $buildno
  exit 0
fi

if [[ ! -z $gitupdate ]]; then
  GH=$(git log -1 --format="%h")
  echo GITHEAD=$GH
  sed -i "/GITHEAD/c\GITHEAD=$GH" .para.inc 
  exit 0
fi


if [[ ! -z $gitshow ]]; then
  GH=$(git log -1 --format="%h")
  echo GITHEAD=$GH
  exit 0
fi


if [[ ! -z $pull ]]; then
  git submodule update --remote 
  exit 0
fi


if [[ ! -z $push ]]; then
  git push --recurse-submodules=check
  exit 0
fi


if [[ ! -z $make  ]]; then
    build_int=${buildno:9:${#buildno}-9}
    build_dt=${buildno:0:${#buildno}-5}  
    (( build_int = 10#$build_int + 1 ))
    today=`date +%Y%m%d`
    build_int=$(printf "%04d" $build_int)  
    if [ "$build_dt" -eq "$today"  ]; then
        buildno=$build_dt-$build_int
    else 
        buildno=$today-0001
    fi
    sed -i "s/.*BUILD.*/%BUILD[$buildno]/" $changelog
    printf $buildno
    exit 0
fi


modified=$(date +%Y-%m-%d)

yellow='\033[1;33m'
NC='\033[0m'

if [[ ! -z $add ]]; then
  printf "Releasing a new version, the most recent version is ${yellow}$version${NC}:\n"
  read -p "New version NO: " newversion
  read -p "New version name: " versionname
  read -p "New version brief: " brief
  sed -i "${line_num}i\\
@[$newversion]\n# $modified\n## $versionname \n- $brief\n\\
    " $changelog
  echo "ChangeLog updated, new version $newversion inserted"
  exit 0
fi

if [[ ! -z $update ]]; then 
    find . -type d \( -path ./monster -o -path ./.git -o -path ./lib \) -prune -o  -type f -print0 | xargs -0 sed -i -e "s/\*\s\\\version.*/\* \\\version   $version/"
    find . -type d \( -path ./monster -o -path ./.git -o -path ./lib \) -prune -o -type f -print0 | xargs -0 sed -i -e "s/\*\s\\\modified.*/\* \\\modified  $modified/"
    find . -type d \( -path ./monster -o -path ./.git -o -path ./lib \) -prune -o -type f -print0 | xargs -0 sed -i -e "s/\*\s\\\PROJECT_NUMBER.*/\* \\\PROJECT_NUMBER=$modified/"
    echo "Version NO in all files updated"
fi

