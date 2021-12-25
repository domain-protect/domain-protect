#!/bin/bash

echo "Executing create_package.sh..."

dir_name=lambda_dist_pkg_$function_name/
mkdir -p $path_module/build/$dir_name

# Create and activate virtual environment...
virtualenv -p $runtime env_$function_name
source $path_cwd/env_$function_name/bin/activate

# Installing python dependencies...
FILE=$path_module/code/$function_name/requirements.txt

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
cp -r $path_cwd/env_$function_name/lib/$runtime/site-packages/. $path_module/build/$dir_name
mkdir $path_module/build/$dir_name/content
cp -a $path_module/code/$function_name/content/. $path_module/build/$dir_name/content/
cp $path_module/code/$function_name/$function_name.py $path_module/build/$dir_name
cp $path_module/code/$function_name/s3.yaml $path_module/build/$dir_name

# Removing virtual environment folder...
echo "Removing virtual environment folder..."
rm -rf $path_cwd/env_$function_name

echo "Finished script execution!"
