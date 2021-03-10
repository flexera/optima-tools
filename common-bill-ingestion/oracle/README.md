# Setup Oracle CBI

## Instructions

1. Create Bill Connect
2. Install [Oracle SDK](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/climanualinst.htm#Step_3_Installing_the_Command_Line_Interface)
3. Install [Docker](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsinstalldocker.htm#Install_Docker_for_Use_with_Oracle_Functions)
4. Install [FN](https://github.com/fnproject/cli#install)
5. Create [Dynamic Group](https://github.com/oracle/oracle-functions-samples/blob/97cc4edc33197009b5a96ffabe7ba38e82406ef6/samples/oci-objectstorage-get-object-python/README.md#create-or-update-your-dynamic-group)

5. `fn create context oracle-cbi --provider oracle`
6. `fn use context oracle-cbi`
7. `fn update context oracle.compartment-id <compartment-ocid>`
8. `fn update context api-url https://functions.<region-identifier>.oci.oraclecloud.com`
fn update context oracle.compartment-id ocid1.compartment.oc1..aaaaaaaa4pgzz4i655f3twupzhi7sxf4fxxmhngp3v4xu63ph3mveqoxte7q
fn update context api-url https://functions.<region-identifier>.oci.oraclecloud.com
