#!/bin/bash

echo "Executing create_package.sh..."

dir_name=lambda_dist_pkg_$function_name/
mkdir -p $path_cwd/build/$dir_name

# Create and activate virtual environment...
virtualenv -p $runtime $path_cwd/build/env_$function_name
source $path_cwd/build/env_$function_name/bin/activate

# Installing python dependencies...
FILE=$path_cwd/lambda_code/$function_name/requirements.txt

if [ -f "$FILE" ]; then
  echo "Installing dependencies..."
  echo "From: requirements.txt file exists..."
  pip install -r "$FILE"

  # Install regex package...
  pip install --platform $platform \
    --target $path_cwd/build/env_$function_name/lib/$runtime/site-packages \
    --implementation cp \
    --python-version ${runtime:6} \
    --only-binary=:all: --upgrade \
    regex

else
  echo "Error: requirements.txt does not exist!"
fi

# Deactivate virtual environment...
deactivate

# Create deployment package...
echo "Creating deployment package..."
cp -r $path_cwd/build/env_$function_name/lib/$runtime/site-packages/. $path_cwd/build/$dir_name
cp -r $path_cwd/lambda_code/$function_name/. $path_cwd/build/$dir_name
cp -r $path_cwd/utils $path_cwd/build/$dir_name

# Removing virtual environment folder...
echo "Removing virtual environment folder..."
rm -rf $path_cwd/build/env_$function_name

echo "Finished script execution!"
