# Cassandra-Operations
Ansible playbooks for automating operational tasks for Apache Cassandra. 

Cassandra is a distributed application. As a result, it can become a bit cumbersome to SSH to each of the host(s) running Cassandra and update configuration file manually. 

I came across this challenge when I started a large cluster of Cassandra nodes, and had to update a config file to enable authentication + authorization the cluster. 


## Tools used 
This code has been tested against:
 * Ansible 2.3.1.0
 * Python 2.7
 * Apache Cassandra (Community Edition) 3.11

## Launching playbook

* Reconfigure cassandra.yml can be used to reconfigure parameters inside cassandra.yml configuration file. The playbook takes the following inputs -
  * -u remote user to launch the playbook and connect to remote host(s)
  * -R this is standard Ansible switch for SU_USER
  * host_name is the variable passed to the playbook 
  * casandra_install_dir is the directory where Cassandra is installed on the remote server. Please note, this playbook has only been tested with community edition of Cassandra. 
  * cassandra_user_name - OS user account that owns Cassandra directory on the remote host(s).
  * cassandra_group_name - OS group on remote host(s) that Cassandra user (cassandra_user_name) is a member of. This is primarily used for assigning privileges on the remote host(s).  

reconfig-cass-params.yml -vvv -u "cloud-user" -R cassandra -e {'"host_name" : "xxx.xxx.xxx.xxx","cassandra_install_dir" : "/opt/cassandra/apache-cassandra-3.0.11", "cassandra_user_name" : "cassandra", "cassandra_group_name" : "cassandra"'}
