
# Set the address of the broker. This could be an IP Address or a FQDN
my_mqtt_broker = "my_mqtt_broker"

# Set your MySQL Credentials to connect to MySQL. Set the variables as needed.
mysql_host = 'mysql_host'
mysql_database = 'sensor_data'
mysql_user = 'mysql_user'
mysql_password = 'mysql_password'

# this is the connection string for your MySQL Database. Nothing is needed to be changed here.
sensor_data_db_config = {
    'host': mysql_host,
    'database': mysql_database,
    'user': mysql_user,
    'password': mysql_password,
    'auth_plugin': 'mysql_native_password'
}
