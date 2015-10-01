#!/bin/bash

# Check if has root privileges
if [[ $EUID -ne 0 ]]; then
	echo "You must have root privileges to create a new Hub" 1>&2
	exit 1
fi

# Get hub name
echo "Type the name of the Hub you want to create, followed by [ENTER]:"
read hubname

if [ $hubname = "" ]; then
	echo "You don't type any name. Exiting..." 1>&2
	exit 1
fi


# User creation
# TODO: Check status code 9
if useradd -d /home/$hubname -G www-data -m $hubname; then
	echo "User created succesfully"
else
	echo "User creation failed" 1>&2
	exit 1
fi

# Folder creation
if sudo -u $hubname mkdir /home/$hubname/moocng; then
	echo "MOOCng folder created succesfully"
else
	echo "MOOCng folder creation failed" 1>&2
fi

if sudo -u $hubname mkdir /home/$hubname/log; then
	echo "Log folder created succesfully"
else
	echo "Log folder creation failed" 1>&2
fi

# MOOCng git clone
if git clone https://github.com/GeographicaGS/moocng.git /home/$hubname/moocng; then
	echo "MOOCng project cloned succesfully"
else
	echo "MOOCng project clone failed" 1>&2
fi

# PostgreSQL database creation
databasecreation(){
	# Create database user and schema

	# Ask for the database address
	echo "Are the databases installed on this machine?, type 'yes' or 'no' followed by [ENTER]:"
	read localdatabase

	pg_address="127.0.0.1"
	pg_port="5432"
	pg_user="postgres"
	pg_pass="postgres"

	if [[ $localdatabase != "yes" ]]; then
		echo "Type the database address, default [127.0.0.1]:"
		read pg_address
		echo "Type the database port, default [5432]:"
		read pg_port
		echo "Type the database admin username, default [postgres]:"
		read pg_user
		echo "Type the database admin password, default [postgres]:"
		read -s pg_pass
	fi

	if [[ $pg_address = "" ]]; then
		pg_address="127.0.0.1"
	fi

	if [[ $pg_port = "" ]]; then
		pg_port="5432"
	fi

	if [[ $pg_user = "" ]]; then
		pg_user="postgres"
	fi

	if [[ $pg_pass = "" ]]; then
		pg_pass="postgres"
	fi

	echo "Creating PostgreSQL user..."
	echo "Note: You'll be asked for the postgreSQL admin password before and after the creation as 'Password for user $pg_user'"
	if psql -h $pg_address -p $pg_port -U $pg_user -tAc "SELECT 1 FROM pg_roles WHERE rolname='$hubname'" | grep -q 1 || createuser -h $pg_address -p $pg_port -U $pg_user $hubname --no-createrole --no-createdb --no-superuser -P; then
	 	echo "Type the postgres user password again, followed by [ENTER]:"
	 	read -s pg_pass

		echo "Creating PostgreSQL database..."
		if psql -h $pg_address -p $pg_port -U $pg_user -tAc "SELECT 1 FROM pg_database WHERE datname='$hubname'" | grep -q 1 || createdb -h $pg_address -p $pg_port -U $pg_user -E UTF8 --owner=$hubname $hubname; then
			echo "PostgreSQL database created succesfully"
		else
			echo "PostgreSQL database creation failed" 1>&2
			exit 1
		fi
	else
		echo "PostgreSQL user creation failed" 1>&2
		exit 1
	fi

	# Config postgreSQL to connect with
	if [[ $localdatabase == "yes" ]]; then
		# Edit pg_hba.conf
		PGA_FILE="/etc/postgresql/9.3/main/pg_hba.conf"
		if echo "local	$hubname	$hubname		md5" >> "$PGA_FILE"; then
			echo "PostgreSQL configurated succesfully"
		else
			echo "PostgreSQL configuration failed" 1>&2
			exit 1
		fi
	else
		echo "You must add to the server's pg_hba.conf file the following line BEFORE CONTINUING:"
		host_ip=$(hostname -I)
		echo "host	$hubname	$hubname	$host_ip	md5"
		read -p "Press any key to continue..."
	fi
}

databasecreation

# Celeryd config
# TODO Check if user exists
echo "Creating Celery service..."
service rabbitmq-server start

echo "Type a password for the RabbitMQ user, followed by [ENTER]:"
read -s rabbit_pass

if rabbitmqctl add_user $hubname $rabbit_pass; then
	if rabbitmqctl add_vhost $hubname; then
		if rabbitmqctl set_permissions -p $hubname $hubname ".*" ".*" ".*"; then
			cp /home/$hubname/moocng/celeryd /etc/init.d/celeryd_$hubname
			sed -i 's/\/var\/www\/moocng\/moocng/\/home\/$hubname\/moocng/g' /etc/init.d/celeryd_$hubname
			echo "Celery service created"
		else
			echo "Celery service creation failed" 1>&2
			exit 1
		fi
	else
		echo "Celery service creation failed" 1>&2
		exit 1
	fi
else
	echo "Celery service creation failed" 1>&2
	exit 1
fi

# MOOCng config
echo "Configuring MOOCng..."

cp /home/$hubname/moocng/moocng/settings/common.py.example /home/$hubname/moocng/moocng/settings/common.py
# PostgreSQL
sed -i "s/'NAME': 'moocng'/'NAME': '$hubname'/g" /home/$hubname/moocng/moocng/settings/common.py
sed -i "s/'USER': 'moocng'/'USER': '$hubname'/g" /home/$hubname/moocng/moocng/settings/common.py
sed -i "s/'PASSWORD': 'password'/'PASSWORD': '$pg_pass'/g" /home/$hubname/moocng/moocng/settings/common.py
sed -i "s/'HOST': ''/'HOST': '$pg_address'/g" /home/$hubname/moocng/moocng/settings/common.py
sed -i "s/'PORT': ''/'PORT': '$pg_port'/g" /home/$hubname/moocng/moocng/settings/common.py
# MongoDB
sed -i "s/mongodb:\/\/localhost:27017\/moocng/mongodb:\/\/$pg_address:27017\/$hubname/g" /home/$hubname/moocng/moocng/settings/common.py
# S3
echo "Type the AWS access key id, followed by [ENTER]:"
read aws_key
sed -i "s/AWS_ACCESS_KEY_ID = ''/AWS_ACCESS_KEY_ID = '$aws_key'/g" /home/$hubname/moocng/moocng/settings/common.py
echo "Type the AWS access secret, followed by [ENTER]:"
read aws_secret
sed -i "s/AWS_SECRET_ACCESS_KEY = ''/AWS_SECRET_ACCESS_KEY = '$aws_secret'/g" /home/$hubname/moocng/moocng/settings/common.py
echo "Type the AWS bucket name, followed by [ENTER]:"
read aws_bucket
sed -i "s/AWS_STORAGE_BUCKET_NAME = ''/AWS_STORAGE_BUCKET_NAME = '$aws_bucket'/g" /home/$hubname/moocng/moocng/settings/common.py
# Secret key
secret_key=$(tr -c -d '0123456789abcdefghijklmnopqrstuvwxyz' </dev/urandom | dd bs=32 count=1 2>/dev/null;echo)
sed -i "s/SECRET_KEY = 'set secret key here'/SECRET_KEY = '$secret_key'/g" /home/$hubname/moocng/moocng/settings/common.py
# Google Analytics
echo "Type the Google Analytics Id, followed by [ENTER]:"
read ga_id
sed -i "s/GOOGLE_ANALYTICS_CODE = ''/GOOGLE_ANALYTICS_CODE = '$ga_id'/g" /home/$hubname/moocng/moocng/settings/common.py
# Celery
sed -i "s/amqp:\/\/moocng:moocngpassword@localhost:5672\/moocng/amqp:\/\/$hubname:$rabbit_pass@localhost:5672\/$hubname/g" /home/$hubname/moocng/moocng/settings/common.py
# IdP
echo "Type the IdP address (without https://), followed by [ENTER]:"
read idp_address
sed -i "s/idp.devopenmooc.com/$idp_address/g" /home/$hubname/moocng/moocng/settings/common.py

cp /home/$hubname/moocng/moocng/settings/saml_settings.py.example /home/$hubname/moocng/moocng/settings/saml_settings.py
# MOOCng address
echo "Type the Hub address (without http(s)://), followed by [ENTER]:"
read hub_address
sed -i "s/moocng.devopenmooc.com/$hub_address/g" /home/$hubname/moocng/moocng/settings/saml_settings.py
sed -i "s/idp.devopenmooc.com/$idp_address/g" /home/$hubname/moocng/moocng/settings/saml_settings.py
# Copy IdP metadata
wget -O /home/$hubname/moocng/moocng/remote_metadata.xml https://$idp_address/simplesaml/saml2/idp/metadata.php --no-check-certificate

# NGINX config
echo "Configuring nginx..."
cp /home/$hubname/moocng/scripts/templates/nginx-hub.example /etc/nginx/sites-available/$hub_address
sed -i "s/hubX/$hubname/g" /etc/nginx/sites-available/$hub_address
ln -s /etc/nginx/sites-available/$hub_address /etc/nginx/sites-enabled/

# UWSGI
echo "Configuring uwsgi..."
ln -s /etc/uwsgi/moocng.skel /etc/uwsgi/$hubname.ini

# Init databases
echo "Initializing databases..."
. /var/www/moocng/bin/activate
cd /home/$hubname/moocng/
echo "When it asks you about to create a new admin/root user, answer 'no' on the first time."
./manage.py syncdb --settings=moocng.settings
./manage.py migrate moocng.courses
./manage.py migrate
echo "Type a password for the admin user, followed by [ENTER]:"
./manage.py createsuperuser --username=root --email=admin.$hubname@ecolearning.eu

# Collect static files
./manage.py collectstatic

#Config IdP server
echo "Configuring IdP server..."
echo "Type the user name to connect to the IdP server, followed by [ENTER]:"
read idp_username
ssh $idp_username@$idp_address "sed -i \"/components =  array (/a array \('$hubname' => 'http:\/\/$hub_address\/auth\/saml2\/metadata\/'\), \" /etc/simplesamlphp/config/openmooc_components.php"


echo "Hub $hubname created!"
echo "Remember to link the hub domain and restart moocngd and nginx services!"
exit 0
