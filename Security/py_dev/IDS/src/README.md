# Src
The Federated Capability-based AC strategy implementation, including smart gateway, CapAC enabled webservice application.

## Tools
The utilities and tools folder to support development.
* meas_perform.py: This module provide performance measure utilities, such as data extract, merge, and visualization.

## SGW_API
The smart gateway system development.
* ipset_config: This folder contains ipset configuration files.

* iptables_config: This folder maintains iptable configuration files.

* filter_list.py: This module provide filter list management classes by using file I/O API or SQLite engine.

* netwrok_monitor.py: This module provide network monitoring functions, such as sniff packets, by means of scapy.

* pkt_analysis.py: This module provide packet analysis functions, such as extract data, display data and log data. Need scapy libs.

* policy_firewall.py: This module provide network firewall policy functions based on python wrapper for ipset, iptables.

* test.py: Test functions to verify enviroment setup.

* utilities.py: This module provide utility functions to support project.

* vtAPI.py: This module provide encapsulation functions to access [VirusTotal API](https://developers.virustotal.com/v2.0/reference).

* wrapper_ipset.py: This module provide python wrapper functions to call ipset commands in linux system.

* wrapper_iptables.py: This module provide python wrapper functions to call iptables commands in linux system.

## WS_API
The capability-based access control strategy and webservice development.
* templates: This module maintains template files to address visualization design for web pages.

* CapAC_Policy.py: This module provide Capability token struct model and encapsulation of federated CapAC policy.

* WS_Client.py: This module provides encapsulation of client API that access to Web service.

* WS_Server.py: This module provides encapsulation of server API that handle and response client's request.

* wrapper_pyca.py: This module provide python wrapper functions to call pyca API.

* helloworld.py: This module provides test functions to verify configuration of flask.

* testapi.py: This module provides test data and flask functions to support test cases in helloworld.py.

* sqlite_demo.py: This module provides demo python wrapper functions to interact with SQLite engine.
