#!/bin/bash

echo "Executing create_package.sh..."

function_list=${function_names//:/ }

for i in $function_list
do
  dir_name=lambda_dist_pkg_$i/
  mkdir -p $path_module/build/$dir_name

  # Create and activate virtual environment...
  virtualenv -p $runtime env_$i
  source $path_cwd/env_$i/bin/activate

  # Installing python dependencies...
  FILE=$path_module/code/$i/requirements.txt

  if [ -f "$FILE" ]; then
    echo "Installing dependencies..."
    echo "From: requirements.txt file exists..."
    pip install -r "$FILE"

  else
    echo "Error: requirements.txt does not exist!"
  fi

  # Deactivate virtual environment...
  deactivate

  # Create deployment package...
  echo "Creating deployment package..."
  cp -r $path_cwd/env_$i/lib/$runtime/site-packages/. $path_module/build/$dir_name
  cp $path_module/code/$i/$i.py $path_module/build/$dir_name
  cp $path_module/code/utils_aws.py $path_module/build/$dir_name
  cp $path_module/code/utils_dns.py $path_module/build/$dir_name
  cp $path_module/code/utils_requests.py $path_module/build/$dir_name

# Removing virtual environment folder...
echo "Removing virtual environment folder..."
rm -rf $path_cwd/env_$i

done

echo "Finished script execution!"
